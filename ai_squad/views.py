from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import SquadRun, SquadRunStatus
from .serializers import SquadRunCreateSerializer, SquadRunDetailSerializer
from .services import SquadRunService
from .tasks import execute_run


class SquadRunViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = (
        SquadRun.objects.all()
        .prefetch_related("steps__artifacts", "steps__gates", "artifacts", "gates")
        .order_by("-id")
    )

    def get_serializer_class(self):
        if self.action == "create":
            return SquadRunCreateSerializer
        return SquadRunDetailSerializer

    def perform_create(self, serializer):
        run = serializer.save(created_by=self.request.user)
        SquadRunService.ensure_steps(run)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        run = self.get_object()
        if run.status != SquadRunStatus.CREATED:
            return Response(
                {"detail": "Solo se puede iniciar un run en estado CREATED."},
                status=status.HTTP_409_CONFLICT,
            )
        execute_run.delay(run.id)
        return Response({"ok": True}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        run = self.get_object()
        if run.status != SquadRunStatus.RUNNING:
            return Response(
                {"detail": "Solo se puede pausar un run en estado RUNNING."},
                status=status.HTTP_409_CONFLICT,
            )
        run.status = SquadRunStatus.PAUSED
        run.save(update_fields=["status"])
        return Response({"ok": True})

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        run = self.get_object()
        if run.status != SquadRunStatus.PAUSED:
            return Response(
                {"detail": "Solo se puede reanudar un run en estado PAUSED."},
                status=status.HTTP_409_CONFLICT,
            )
        run.status = SquadRunStatus.RUNNING
        run.save(update_fields=["status"])
        execute_run.delay(run.id)
        return Response({"ok": True}, status=status.HTTP_202_ACCEPTED)
