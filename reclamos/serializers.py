from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from .models import (
    Area,
    CampoDinamicoOpcion,
    CampoDinamicoReclamo,
    EstadoReclamo,
    EstadoReclamoTransicion,
    PrioridadReclamo,
    Reclamo,
    ReclamoAdjunto,
    ReclamoAsignacion,
    ReclamoComentario,
    ReclamoDatoDinamico,
    ReclamoHistorial,
    TipoReclamo,
)
from .services import (
    guardar_datos_dinamicos,
    obtener_estado_inicial,
    obtener_prioridad_base,
    registrar_historial,
    validar_requisitos_runtime_reclamo,
    validar_transicion_estado_reclamo,
    validar_y_preparar_datos_dinamicos,
)

User = get_user_model()


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TipoReclamoSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)
    prioridad_default_nombre = serializers.CharField(source="prioridad_default.nombre", read_only=True)

    class Meta:
        model = TipoReclamo
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EstadoReclamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoReclamo
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EstadoReclamoTransicionSerializer(serializers.ModelSerializer):
    estado_origen_nombre = serializers.CharField(source="estado_origen.nombre", read_only=True)
    estado_destino_nombre = serializers.CharField(source="estado_destino.nombre", read_only=True)

    class Meta:
        model = EstadoReclamoTransicion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PrioridadReclamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioridadReclamo
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CampoDinamicoOpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoDinamicoOpcion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CampoDinamicoReclamoSerializer(serializers.ModelSerializer):
    tipo_reclamo_nombre = serializers.CharField(source="tipo_reclamo.nombre", read_only=True)
    opciones = CampoDinamicoOpcionSerializer(many=True, read_only=True)

    class Meta:
        model = CampoDinamicoReclamo
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReclamoDatoDinamicoSerializer(serializers.ModelSerializer):
    campo_nombre = serializers.CharField(source="campo.nombre", read_only=True)
    campo_codigo = serializers.CharField(source="campo.codigo", read_only=True)

    class Meta:
        model = ReclamoDatoDinamico
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReclamoListSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    prioridad_nombre = serializers.CharField(source="prioridad.nombre", read_only=True)
    tipo_reclamo_nombre = serializers.CharField(source="tipo_reclamo.nombre", read_only=True)
    area_actual_nombre = serializers.CharField(source="area_actual.nombre", read_only=True)
    asignado_a_username = serializers.CharField(source="asignado_a.username", read_only=True)

    class Meta:
        model = Reclamo
        fields = (
            "id",
            "numero",
            "titulo",
            "estado",
            "estado_nombre",
            "prioridad",
            "prioridad_nombre",
            "tipo_reclamo",
            "tipo_reclamo_nombre",
            "area_actual",
            "area_actual_nombre",
            "asignado_a",
            "asignado_a_username",
            "origen",
            "fecha_ingreso",
            "activo",
            "created_at",
            "updated_at",
        )


class ReclamoDetailSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    prioridad_nombre = serializers.CharField(source="prioridad.nombre", read_only=True)
    tipo_reclamo_nombre = serializers.CharField(source="tipo_reclamo.nombre", read_only=True)
    area_actual_nombre = serializers.CharField(source="area_actual.nombre", read_only=True)
    area_responsable_nombre = serializers.CharField(source="area_responsable.nombre", read_only=True)
    ciudadano_nombre = serializers.CharField(source="ciudadano.nombre_completo", read_only=True)
    asignado_a_username = serializers.CharField(source="asignado_a.username", read_only=True)
    datos_dinamicos = ReclamoDatoDinamicoSerializer(many=True, read_only=True)

    class Meta:
        model = Reclamo
        fields = "__all__"
        read_only_fields = ("id", "numero", "created_at", "updated_at")


class ReclamoWriteSerializer(serializers.ModelSerializer):
    datos_dinamicos = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    comentario_transicion = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Reclamo
        fields = "__all__"
        read_only_fields = ("id", "numero", "created_at", "updated_at")

    def _current_user(self):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            return request.user
        return None

    @transaction.atomic
    def create(self, validated_data):
        user = self._current_user()
        datos_dinamicos = validated_data.pop("datos_dinamicos", [])
        validated_data.pop("comentario_transicion", "")
        tipo_reclamo = validated_data.get("tipo_reclamo")
        municipio = validated_data.get("municipio")

        if not validated_data.get("estado"):
            estado_inicial = obtener_estado_inicial(municipio=municipio)
            if estado_inicial:
                validated_data["estado"] = estado_inicial

        if not validated_data.get("prioridad"):
            prioridad = getattr(tipo_reclamo, "prioridad_default", None) if tipo_reclamo else None
            if not prioridad:
                prioridad = obtener_prioridad_base(municipio=municipio)
            if prioridad:
                validated_data["prioridad"] = prioridad

        if not validated_data.get("area_actual") and tipo_reclamo:
            validated_data["area_actual"] = tipo_reclamo.area
        if not validated_data.get("area_responsable") and validated_data.get("area_actual"):
            validated_data["area_responsable"] = validated_data["area_actual"]
        if not validated_data.get("fecha_ingreso"):
            validated_data["fecha_ingreso"] = timezone.now()
        if not validated_data.get("sla_horas") and tipo_reclamo and tipo_reclamo.sla_horas:
            validated_data["sla_horas"] = tipo_reclamo.sla_horas
        if user:
            validated_data.setdefault("creado_por", user)
            validated_data.setdefault("actualizado_por", user)

        try:
            datos_preparados = validar_y_preparar_datos_dinamicos(tipo_reclamo=tipo_reclamo, datos=datos_dinamicos)
        except ValueError as exc:
            raise serializers.ValidationError({"datos_dinamicos": str(exc)}) from exc

        reclamo = super().create(validated_data)
        guardar_datos_dinamicos(reclamo=reclamo, datos_preparados=datos_preparados)
        try:
            validar_requisitos_runtime_reclamo(
                reclamo=reclamo,
                tipo_reclamo=reclamo.tipo_reclamo,
                estado_objetivo=reclamo.estado,
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
        registrar_historial(
            reclamo=reclamo,
            accion="creacion",
            usuario=user,
            estado_nuevo=reclamo.estado,
            area_nueva=reclamo.area_actual,
            asignado_nuevo=reclamo.asignado_a,
            visible_ciudadano=True,
            metadata={"origen": reclamo.origen},
        )
        return reclamo

    @transaction.atomic
    def update(self, instance, validated_data):
        user = self._current_user()
        datos_dinamicos = validated_data.pop("datos_dinamicos", None)
        comentario_transicion = validated_data.pop("comentario_transicion", "")
        estado_anterior = instance.estado
        area_anterior = instance.area_actual
        asignado_anterior = instance.asignado_a

        if user:
            validated_data["actualizado_por"] = user

        estado_nuevo = validated_data.get("estado", instance.estado)
        area_nueva = validated_data.get("area_actual", instance.area_actual)
        area_responsable_nueva = validated_data.get("area_responsable", instance.area_responsable)
        asignado_nuevo = validated_data.get("asignado_a", instance.asignado_a)

        try:
            validar_transicion_estado_reclamo(
                reclamo=instance,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                usuario=user,
                comentario=comentario_transicion,
                area_actual=area_nueva,
                asignado_a=asignado_nuevo,
                area_responsable=area_responsable_nueva,
            )
            if estado_anterior != estado_nuevo and not area_responsable_nueva:
                # si cambia estado y no hay transicion que lo exija, aun asi mantenemos consistencia operativa
                validated_data.setdefault("area_responsable", area_nueva or area_responsable_nueva)
        except ValueError as exc:
            raise serializers.ValidationError({"estado": str(exc)}) from exc

        reclamo = super().update(instance, validated_data)
        if datos_dinamicos is not None:
            try:
                datos_preparados = validar_y_preparar_datos_dinamicos(
                    tipo_reclamo=reclamo.tipo_reclamo,
                    datos=datos_dinamicos,
                )
            except ValueError as exc:
                raise serializers.ValidationError({"datos_dinamicos": str(exc)}) from exc
            guardar_datos_dinamicos(reclamo=reclamo, datos_preparados=datos_preparados)
        else:
            datos_preparados = None

        try:
            validar_requisitos_runtime_reclamo(
                reclamo=reclamo,
                tipo_reclamo=reclamo.tipo_reclamo,
                estado_objetivo=reclamo.estado,
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

        cambio_estado = estado_anterior != reclamo.estado
        cambio_area = area_anterior != reclamo.area_actual
        cambio_asignado = asignado_anterior != reclamo.asignado_a
        if not (cambio_estado or cambio_area or cambio_asignado):
            return reclamo

        if cambio_estado and not (cambio_area or cambio_asignado):
            accion = "cambio_estado"
        elif cambio_area and not (cambio_estado or cambio_asignado):
            accion = "cambio_area"
        elif cambio_asignado and not (cambio_estado or cambio_area):
            accion = "cambio_asignado"
        else:
            accion = "actualizacion"

        registrar_historial(
            reclamo=reclamo,
            accion=accion,
            usuario=user,
            estado_anterior=estado_anterior if cambio_estado else None,
            estado_nuevo=reclamo.estado if cambio_estado else None,
            area_anterior=area_anterior if cambio_area else None,
            area_nueva=reclamo.area_actual if cambio_area else None,
            asignado_anterior=asignado_anterior if cambio_asignado else None,
            asignado_nuevo=reclamo.asignado_a if cambio_asignado else None,
            comentario=comentario_transicion if cambio_estado else "",
            metadata={
                "cambio_estado": cambio_estado,
                "cambio_area": cambio_area,
                "cambio_asignado": cambio_asignado,
                "campos_dinamicos_actualizados": bool(datos_preparados),
            },
        )
        return reclamo


class ReclamoHistorialSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    estado_anterior_nombre = serializers.CharField(source="estado_anterior.nombre", read_only=True)
    estado_nuevo_nombre = serializers.CharField(source="estado_nuevo.nombre", read_only=True)
    area_anterior_nombre = serializers.CharField(source="area_anterior.nombre", read_only=True)
    area_nueva_nombre = serializers.CharField(source="area_nueva.nombre", read_only=True)
    asignado_anterior_username = serializers.CharField(source="asignado_anterior.username", read_only=True)
    asignado_nuevo_username = serializers.CharField(source="asignado_nuevo.username", read_only=True)

    class Meta:
        model = ReclamoHistorial
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class ReclamoAdjuntoSerializer(serializers.ModelSerializer):
    subido_por_username = serializers.CharField(source="subido_por.username", read_only=True)

    class Meta:
        model = ReclamoAdjunto
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "subido_por")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["subido_por"] = request.user
        return super().create(validated_data)


class ReclamoComentarioSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    ciudadano_nombre = serializers.CharField(source="ciudadano.nombre_completo", read_only=True)

    class Meta:
        model = ReclamoComentario
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "usuario")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["usuario"] = request.user
        return super().create(validated_data)


class ReclamoAsignacionSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    asignado_por_username = serializers.CharField(source="asignado_por.username", read_only=True)
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)

    class Meta:
        model = ReclamoAsignacion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "asignado_por")

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        actor = request.user if request and request.user and request.user.is_authenticated else None
        reclamo = validated_data["reclamo"]
        area = validated_data["area"]
        usuario = validated_data.get("usuario")
        activa = validated_data.get("activa", True)

        if actor:
            validated_data["asignado_por"] = actor

        if activa:
            reclamo.asignaciones.filter(activa=True).update(activa=False, fecha_fin=timezone.now())

        asignacion = super().create(validated_data)

        estado_anterior_area = reclamo.area_actual
        estado_anterior_asignado = reclamo.asignado_a
        reclamo.area_actual = area
        reclamo.area_responsable = area
        reclamo.asignado_a = usuario
        reclamo.actualizado_por = actor
        reclamo.save(update_fields=["area_actual", "area_responsable", "asignado_a", "actualizado_por", "updated_at"])

        registrar_historial(
            reclamo=reclamo,
            accion="asignacion",
            usuario=actor,
            area_anterior=estado_anterior_area,
            area_nueva=reclamo.area_actual,
            asignado_anterior=estado_anterior_asignado,
            asignado_nuevo=reclamo.asignado_a,
            comentario=asignacion.motivo or "",
            metadata={"asignacion_id": asignacion.id},
        )
        return asignacion
