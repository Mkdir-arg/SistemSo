# ai_squad/models.py
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone

from simple_history.models import HistoricalRecords


class SquadRunStatus(models.TextChoices):
    CREATED = "CREATED", "Creado"
    RUNNING = "RUNNING", "En ejecución"
    PAUSED = "PAUSED", "Pausado"
    FAILED = "FAILED", "Fallido"
    SUCCEEDED = "SUCCEEDED", "Exitoso"
    CANCELED = "CANCELED", "Cancelado"


class StepRole(models.TextChoices):
    ANALISTA_FUNCIONAL = "ANALISTA_FUNCIONAL", "Analista Funcional"
    ARQUITECTO_SW = "ARQUITECTO_SW", "Arquitecto de Software"
    ANALISTA_DB = "ANALISTA_DB", "Analista de Base de Datos"
    UX_UI = "UX_UI", "UX/UI"
    DEV_BACKEND = "DEV_BACKEND", "Dev Backend"
    DEV_FRONT = "DEV_FRONT", "Dev Front"
    QA = "QA", "QA"


class StepStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    RUNNING = "RUNNING", "En ejecución"
    WAITING_USER = "WAITING_USER", "Esperando usuario"
    FAILED = "FAILED", "Fallido"
    SUCCEEDED = "SUCCEEDED", "Exitoso"
    SKIPPED = "SKIPPED", "Omitido"
    CANCELED = "CANCELED", "Cancelado"


class ArtifactType(models.TextChoices):
    RF = "RF", "Requerimiento Funcional"
    ARCH = "ARCH", "Diseño/Arquitectura"
    DB = "DB", "Diseño Base de Datos"
    UX = "UX", "UX/UI"
    CODE_BACKEND = "CODE_BACKEND", "Código Backend"
    CODE_FRONT = "CODE_FRONT", "Código Front/Mobile"
    TESTS = "TESTS", "Tests"
    QA_REPORT = "QA_REPORT", "Reporte QA"
    PR_PACKAGE = "PR_PACKAGE", "Paquete PR"
    LOG = "LOG", "Log/Notas"


class GateType(models.TextChoices):
    LINT = "LINT", "Lint/Format"
    TESTS = "TESTS", "Tests"
    SECURITY = "SECURITY", "Checklist Seguridad"
    PERFORMANCE = "PERFORMANCE", "Chequeo Performance"
    BRAND = "BRAND", "Manual de Marca (UX/UI)"


class GateStatus(models.TextChoices):
    PENDING = "PENDING", "Pendiente"
    RUNNING = "RUNNING", "En ejecución"
    PASSED = "PASSED", "Aprobado"
    FAILED = "FAILED", "Rechazado"
    SKIPPED = "SKIPPED", "Omitido"


class SquadRun(models.Model):
    """
    Un 'run' representa un ciclo completo del squad: necesidad -> artefactos -> código -> gates -> PR package.
    """
    name = models.CharField(max_length=180, default="el squad mas picante")
    status = models.CharField(max_length=20, choices=SquadRunStatus.choices, default=SquadRunStatus.CREATED)

    # Scope: para locks/concurrencia (ej: "legajos", "core", "conversaciones", "mobile", etc.)
    scope = models.CharField(max_length=120, blank=True, default="")

    # Entrada del usuario
    need_title = models.CharField(max_length=240)
    need_description = models.TextField()

    # Configuración del run
    language = models.CharField(max_length=16, default="es")  # "es" por defecto
    mode_interactive = models.BooleanField(default=True)      # pausas por fase / aprobaciones
    max_iterations = models.PositiveIntegerField(default=3)

    # Observabilidad / control
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="squad_runs_created"
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    # Para reproducibilidad: versión de prompts / context packs (si los implementás luego)
    prompt_version = models.CharField(max_length=32, blank=True, default="v1")
    context_pack_versions = models.JSONField(default=dict, blank=True)  # ej: {"brand": "1.0.0", "api": "0.3.0"}

    # Resumen final
    summary = models.TextField(blank=True, default="")
    error_message = models.TextField(blank=True, default="")

    history = HistoricalRecords()

    class Meta:
        db_table = "ai_squad_run"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["scope"]),
            models.Index(fields=["created_by"]),
            models.Index(fields=["-id"]),
        ]

    def mark_started(self):
        if not self.started_at:
            self.started_at = timezone.now()
        self.status = SquadRunStatus.RUNNING
        self.save(update_fields=["started_at", "status"])

    def mark_finished(self, ok: bool, summary: str = "", error_message: str = ""):
        self.finished_at = timezone.now()
        self.status = SquadRunStatus.SUCCEEDED if ok else SquadRunStatus.FAILED
        self.summary = summary or self.summary
        self.error_message = error_message or self.error_message
        self.save(update_fields=["finished_at", "status", "summary", "error_message"])


class RunStep(models.Model):
    """
    Un paso del pipeline asociado a un rol.
    Guarda inputs/outputs normalizados y metadatos (incl. trazas de ejecución).
    """
    run = models.ForeignKey(SquadRun, on_delete=models.CASCADE, related_name="steps")
    role = models.CharField(max_length=40, choices=StepRole.choices)
    status = models.CharField(max_length=20, choices=StepStatus.choices, default=StepStatus.PENDING)

    order = models.PositiveIntegerField(default=0)  # orden dentro del pipeline

    # Entradas/salidas del step (estructuradas)
    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)

    # Logs y errores
    log = models.TextField(blank=True, default="")
    error_message = models.TextField(blank=True, default="")

    # Métricas (optativas)
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=4, default=0)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "ai_squad_step"
        unique_together = [("run", "order")]
        indexes = [
            models.Index(fields=["run", "order"]),
            models.Index(fields=["run", "role"]),
            models.Index(fields=["status"]),
        ]

    def mark_started(self):
        if not self.started_at:
            self.started_at = timezone.now()
        self.status = StepStatus.RUNNING
        self.save(update_fields=["started_at", "status"])

    def mark_finished(self, ok: bool, error_message: str = ""):
        self.finished_at = timezone.now()
        self.status = StepStatus.SUCCEEDED if ok else StepStatus.FAILED
        self.error_message = error_message or self.error_message
        self.save(update_fields=["finished_at", "status", "error_message"])


class Artifact(models.Model):
    """
    Artefactos versionados por run y (opcionalmente) por step.
    Ej: RF, DB design, UX specs, diffs de código, reporte QA, PR package.
    """
    run = models.ForeignKey(SquadRun, on_delete=models.CASCADE, related_name="artifacts")
    step = models.ForeignKey(RunStep, on_delete=models.SET_NULL, null=True, blank=True, related_name="artifacts")

    type = models.CharField(max_length=24, choices=ArtifactType.choices)
    title = models.CharField(max_length=240, blank=True, default="")
    version = models.PositiveIntegerField(default=1)

    # Contenido del artefacto (texto o estructura)
    content_text = models.TextField(blank=True, default="")
    content_json = models.JSONField(default=dict, blank=True)

    # Para "código": lista de archivos tocados, diffs, comandos ejecutados, etc.
    meta = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        db_table = "ai_squad_artifact"
        indexes = [
            models.Index(fields=["run", "type"]),
            models.Index(fields=["run", "created_at"]),
        ]

    @staticmethod
    def next_version(run_id: int, artifact_type: str) -> int:
        last = Artifact.objects.filter(run_id=run_id, type=artifact_type).order_by("-version").first()
        return (last.version + 1) if last else 1


class GateResult(models.Model):
    """
    Resultado de un gate (lint/tests/security/perf/brand).
    Puede asociarse a un step o correr al final del run.
    """
    run = models.ForeignKey(SquadRun, on_delete=models.CASCADE, related_name="gates")
    step = models.ForeignKey(RunStep, on_delete=models.SET_NULL, null=True, blank=True, related_name="gates")

    gate_type = models.CharField(max_length=24, choices=GateType.choices)
    status = models.CharField(max_length=16, choices=GateStatus.choices, default=GateStatus.PENDING)

    summary = models.CharField(max_length=300, blank=True, default="")
    details = models.TextField(blank=True, default="")
    report_json = models.JSONField(default=dict, blank=True)

    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        db_table = "ai_squad_gate_result"
        indexes = [
            models.Index(fields=["run", "gate_type"]),
            models.Index(fields=["status"]),
        ]
