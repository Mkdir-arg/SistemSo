from .models import SquadRun, RunStep, StepRole


DEFAULT_PIPELINE = [
    StepRole.ANALISTA_FUNCIONAL,
    StepRole.ARQUITECTO_SW,
    StepRole.ANALISTA_DB,
    StepRole.UX_UI,
    StepRole.DEV_BACKEND,
    StepRole.DEV_FRONT,
    StepRole.QA,
]


class SquadRunService:
    @staticmethod
    def ensure_steps(run: SquadRun) -> None:
        if run.steps.exists():
            return
        RunStep.objects.bulk_create(
            [RunStep(run=run, role=role, order=i) for i, role in enumerate(DEFAULT_PIPELINE, start=1)]
        )
