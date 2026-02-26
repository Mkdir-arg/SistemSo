from rest_framework import serializers
from .models import SquadRun, RunStep, Artifact, GateResult


class ArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artifact
        fields = [
            "id", "run", "step", "type", "title", "version",
            "content_text", "content_json", "meta", "created_at",
        ]
        read_only_fields = ["id", "version", "created_at"]


class GateResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateResult
        fields = [
            "id", "run", "step", "gate_type", "status",
            "summary", "details", "report_json", "started_at", "finished_at",
        ]
        read_only_fields = ["id", "started_at", "finished_at"]


class RunStepSerializer(serializers.ModelSerializer):
    artifacts = ArtifactSerializer(many=True, read_only=True)
    gates = GateResultSerializer(many=True, read_only=True)

    class Meta:
        model = RunStep
        fields = [
            "id", "run", "role", "status", "order",
            "input_data", "output_data",
            "log", "error_message",
            "tokens_in", "tokens_out", "cost_usd",
            "started_at", "finished_at",
            "artifacts", "gates",
        ]
        read_only_fields = ["id", "started_at", "finished_at"]


class SquadRunCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SquadRun
        fields = [
            "need_title",
            "need_description",
            "scope",
            "mode_interactive",
            "max_iterations",
            "prompt_version",
        ]


class SquadRunDetailSerializer(serializers.ModelSerializer):
    steps = RunStepSerializer(many=True, read_only=True)
    artifacts = ArtifactSerializer(many=True, read_only=True)
    gates = GateResultSerializer(many=True, read_only=True)

    class Meta:
        model = SquadRun
        fields = [
            "id", "name", "status", "scope",
            "need_title", "need_description",
            "language", "mode_interactive", "max_iterations",
            "created_by", "started_at", "finished_at",
            "prompt_version", "context_pack_versions",
            "summary", "error_message",
            "steps", "artifacts", "gates",
        ]
        read_only_fields = [
            "id", "name", "status", "language",
            "created_by", "started_at", "finished_at",
            "context_pack_versions", "summary", "error_message",
            "steps", "artifacts", "gates",
        ]
