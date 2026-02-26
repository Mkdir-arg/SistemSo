# ai_squad/tasks.py
from __future__ import annotations

from celery import shared_task
from django.db import transaction
from django.utils import timezone
import time

from .events import emit_run_event
from .models import SquadRun, SquadRunStatus, RunStep, StepStatus
from .runner import run_step_logic, persist_artifact


@shared_task(bind=True)
def ping_squad(self):
    time.sleep(2)
    return {"ok": True, "msg": "pong from ai_squad"}


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def execute_run(self, run_id: int) -> dict:
    """
    Ejecuta el pipeline completo.
    - Respeta PAUSED/CANCELED
    - Ejecuta steps PENDING/FAILED (reintento) en orden
    - Emite eventos por WS
    """
    with transaction.atomic():
        run = SquadRun.objects.select_for_update().get(id=run_id)

        # si está cancelado o ya terminó, salir
        if run.status in (SquadRunStatus.SUCCEEDED, SquadRunStatus.CANCELED):
            return {"ok": True, "skipped": True, "run_id": run_id, "status": run.status}

        # iniciar si corresponde
        if run.status == SquadRunStatus.CREATED:
            run.started_at = run.started_at or timezone.now()
            run.status = SquadRunStatus.RUNNING
            run.save(update_fields=["started_at", "status"])
            emit_run_event(run_id, "RUN_STARTED", {"run_id": run_id})

        if run.status == SquadRunStatus.PAUSED:
            return {"ok": True, "paused": True, "run_id": run_id}

    # ejecutar steps
    steps = (
        RunStep.objects.filter(run_id=run_id)
        .order_by("order")
    )

    for step in steps:
        # re-leer estado del run (pausa/cancel en caliente)
        run.refresh_from_db(fields=["status"])
        if run.status == SquadRunStatus.PAUSED:
            emit_run_event(run_id, "RUN_PAUSED", {"run_id": run_id})
            return {"ok": True, "paused": True, "run_id": run_id}
        if run.status == SquadRunStatus.CANCELED:
            emit_run_event(run_id, "RUN_CANCELED", {"run_id": run_id})
            return {"ok": True, "canceled": True, "run_id": run_id}

        if step.status in (StepStatus.SUCCEEDED, StepStatus.SKIPPED, StepStatus.CANCELED):
            continue
        if step.status == StepStatus.WAITING_USER:
            # modo interactivo: el usuario debe destrabar
            emit_run_event(run_id, "STEP_WAITING_USER", {"run_id": run_id, "step_id": step.id, "role": step.role})
            return {"ok": True, "waiting_user": True, "run_id": run_id, "step_id": step.id}

        # marcar step RUNNING
        step.started_at = step.started_at or timezone.now()
        step.status = StepStatus.RUNNING
        step.save(update_fields=["started_at", "status"])

        emit_run_event(run_id, "STEP_STARTED", {"run_id": run_id, "step_id": step.id, "role": step.role})

        # ejecutar lógica del step
        try:
            result = run_step_logic(step)

            # persistencia atómica del resultado
            with transaction.atomic():
                step.refresh_from_db()
                if result.ok:
                    persist_artifact(step, result)
                    step.status = StepStatus.SUCCEEDED
                    step.finished_at = timezone.now()
                    step.error_message = ""
                    step.save(update_fields=["status", "finished_at", "error_message"])
                    emit_run_event(
                        run_id,
                        "STEP_SUCCEEDED",
                        {"run_id": run_id, "step_id": step.id, "role": step.role},
                    )
                else:
                    step.status = StepStatus.FAILED
                    step.finished_at = timezone.now()
                    step.error_message = result.error or "Step failed"
                    step.save(update_fields=["status", "finished_at", "error_message"])
                    emit_run_event(
                        run_id,
                        "STEP_FAILED",
                        {"run_id": run_id, "step_id": step.id, "role": step.role, "error": step.error_message},
                    )

                    # si interactivo, pausar para intervención
                    if run.mode_interactive:
                        run.status = SquadRunStatus.PAUSED
                        run.save(update_fields=["status"])
                        emit_run_event(run_id, "RUN_PAUSED", {"run_id": run_id, "reason": "step_failed"})
                        return {"ok": False, "run_id": run_id, "failed_step_id": step.id}

        except Exception as e:
            # fallo inesperado: marcar step y run
            with transaction.atomic():
                step.refresh_from_db()
                step.status = StepStatus.FAILED
                step.finished_at = timezone.now()
                step.error_message = str(e)
                step.save(update_fields=["status", "finished_at", "error_message"])
                run.status = SquadRunStatus.FAILED
                run.error_message = str(e)
                run.finished_at = timezone.now()
                run.save(update_fields=["status", "error_message", "finished_at"])

            emit_run_event(run_id, "RUN_FAILED", {"run_id": run_id, "error": str(e)})
            raise

    # si llegó al final, marcar run OK
    run.refresh_from_db()
    if run.status not in (SquadRunStatus.PAUSED, SquadRunStatus.CANCELED, SquadRunStatus.FAILED):
        run.status = SquadRunStatus.SUCCEEDED
        run.finished_at = timezone.now()
        run.summary = run.summary or "Run finalizado correctamente (MVP)."
        run.save(update_fields=["status", "finished_at", "summary"])
        emit_run_event(run_id, "RUN_SUCCEEDED", {"run_id": run_id})

    return {"ok": True, "run_id": run_id, "status": run.status}
