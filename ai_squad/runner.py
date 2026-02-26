# ai_squad/runner.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import RunStep, Artifact, ArtifactType, StepRole
from .codex_agent import CodexAgent
from .context_builder import ProjectContextBuilder


@dataclass(frozen=True)
class StepResult:
    ok: bool
    artifact_type: str | None = None
    artifact_title: str = ""
    artifact_text: str = ""
    artifact_json: dict | None = None
    meta: dict | None = None
    error: str = ""


def _artifact_version(run_id: int, artifact_type: str) -> int:
    return Artifact.next_version(run_id, artifact_type)


def run_step_logic(step: RunStep) -> StepResult:
    """
    MVP: genera artefactos "placeholder" por rol para validar pipeline.
    Luego reemplazamos DEV_BACKEND/DEV_FRONT/QA por integración real (Codex + comandos).
    """
    role = step.role

    if role == StepRole.ANALISTA_FUNCIONAL:
        return StepResult(
            ok=True,
            artifact_type=ArtifactType.RF,
            artifact_title="RF - Especificación funcional",
            artifact_text="(MVP) RF generado. Próximo: completar con template formal + criterios de aceptación.",
            artifact_json={"sections": ["Objetivo", "Alcance", "Casos de uso", "Reglas", "Criterios de aceptación"]},
        )

    if role == StepRole.ARQUITECTO_SW:
        return StepResult(
            ok=True,
            artifact_type=ArtifactType.ARCH,
            artifact_title="Arquitectura - Diseño técnico",
            artifact_text="(MVP) Diseño técnico generado. Próximo: módulos, límites, integraciones, diagramas.",
            artifact_json={"backend": "Django/DRF", "ws": "Channels/Daphne", "async": "Celery/Redis"},
        )

    if role == StepRole.ANALISTA_DB:
        return StepResult(
            ok=True,
            artifact_type=ArtifactType.DB,
            artifact_title="DB - Diseño y migraciones",
            artifact_text="(MVP) Diseño DB generado. Próximo: modelos, índices, constraints, migraciones.",
            artifact_json={"tables": [], "indexes": [], "constraints": []},
        )

    if role == StepRole.UX_UI:
        return StepResult(
            ok=True,
            artifact_type=ArtifactType.UX,
            artifact_title="UX/UI - Wireframe y reglas de diseño",
            artifact_text="(MVP) UX/UI generado. Próximo: pantallas, flujos, componentes, accesibilidad, manual de marca.",
            artifact_json={"screens": [], "components": [], "brand_compliance": True},
        )

    if role == StepRole.DEV_BACKEND:
        # Usar agente real de OpenAI
        try:
            # Obtener RF del step anterior
            rf_artifact = Artifact.objects.filter(
                run_id=step.run_id,
                type=ArtifactType.RF
            ).first()
            
            requirement = rf_artifact.content_text if rf_artifact else step.run.need_description
            
            # Construir contexto del proyecto
            context = ProjectContextBuilder.build_context()
            
            # Generar código con OpenAI
            agent = CodexAgent()
            result = agent.generate_backend_code(requirement, context)
            
            if result.get("ok"):
                return StepResult(
                    ok=True,
                    artifact_type=ArtifactType.CODE_BACKEND,
                    artifact_title="Backend - Código generado por IA",
                    artifact_text=result.get("explanation", ""),
                    artifact_json={
                        "files": result.get("files", []),
                        "commands": result.get("commands", []),
                        "tests": result.get("tests", []),
                        "model": result.get("model", "gpt-4o-mini"),
                        "tokens_used": result.get("tokens_used", 0)
                    },
                    meta={"ai_generated": True, "model": result.get("model")}
                )
            else:
                return StepResult(
                    ok=False,
                    error=f"Error generando código: {result.get('error', 'Unknown')}"
                )
        except Exception as e:
            return StepResult(
                ok=False,
                error=f"Error en agente de código: {str(e)}"
            )

    if role == StepRole.DEV_FRONT:
        return StepResult(
            ok=True,
            artifact_type=ArtifactType.CODE_FRONT,
            artifact_title="Front/Mobile - Cambios propuestos",
            artifact_text="(MVP) Pendiente integración Codex: RN/Expo + navegación + componentes.",
            artifact_json={"files": [], "diff": ""},  # luego: diff real
        )

    if role == StepRole.QA:
        return StepResult(
            ok=True,
            artifact_type=ArtifactType.QA_REPORT,
            artifact_title="QA - Reporte",
            artifact_text="(MVP) QA OK. Próximo: lint+tests reales y gates obligatorios.",
            artifact_json={"lint": "SKIPPED", "tests": "SKIPPED"},
        )

    return StepResult(ok=True, artifact_type=ArtifactType.LOG, artifact_title="Log", artifact_text="Step sin lógica.")


def persist_artifact(step: RunStep, result: StepResult) -> Artifact | None:
    if not result.artifact_type:
        return None
    return Artifact.objects.create(
        run=step.run,
        step=step,
        type=result.artifact_type,
        title=result.artifact_title,
        version=_artifact_version(step.run_id, result.artifact_type),
        content_text=result.artifact_text or "",
        content_json=result.artifact_json or {},
        meta=result.meta or {},
    )
