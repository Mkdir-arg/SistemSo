from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from reclamos.models import Area

from .models import (
    CampoDinamicoOpcion,
    CampoDinamicoTramite,
    EstadoTramite,
    EstadoTramiteTransicion,
    PrioridadTramite,
    RequisitoTramite,
    TipoTramite,
    Tramite,
    TramiteAdjunto,
    TramiteAsignacion,
    TramiteComentario,
    TramiteDatoDinamico,
    TramiteHistorial,
)
from .services import (
    guardar_datos_dinamicos,
    obtener_estado_inicial,
    obtener_prioridad_base,
    registrar_historial,
    validar_requisitos_runtime_tramite,
    validar_transicion_estado_tramite,
    validar_y_preparar_datos_dinamicos,
)


class AreaTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TipoTramiteSerializer(serializers.ModelSerializer):
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)
    prioridad_default_nombre = serializers.CharField(source="prioridad_default.nombre", read_only=True)

    class Meta:
        model = TipoTramite
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EstadoTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoTramite
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class EstadoTramiteTransicionSerializer(serializers.ModelSerializer):
    estado_origen_nombre = serializers.CharField(source="estado_origen.nombre", read_only=True)
    estado_destino_nombre = serializers.CharField(source="estado_destino.nombre", read_only=True)

    class Meta:
        model = EstadoTramiteTransicion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class PrioridadTramiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioridadTramite
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class RequisitoTramiteSerializer(serializers.ModelSerializer):
    tipo_tramite_nombre = serializers.CharField(source="tipo_tramite.nombre", read_only=True)
    campo_dinamico_nombre = serializers.CharField(source="campo_dinamico.nombre", read_only=True)

    class Meta:
        model = RequisitoTramite
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CampoDinamicoOpcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampoDinamicoOpcion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class CampoDinamicoTramiteSerializer(serializers.ModelSerializer):
    tipo_tramite_nombre = serializers.CharField(source="tipo_tramite.nombre", read_only=True)
    opciones = CampoDinamicoOpcionSerializer(many=True, read_only=True)

    class Meta:
        model = CampoDinamicoTramite
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TramiteDatoDinamicoSerializer(serializers.ModelSerializer):
    campo_nombre = serializers.CharField(source="campo.nombre", read_only=True)
    campo_codigo = serializers.CharField(source="campo.codigo", read_only=True)

    class Meta:
        model = TramiteDatoDinamico
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TramiteListSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    prioridad_nombre = serializers.CharField(source="prioridad.nombre", read_only=True)
    tipo_tramite_nombre = serializers.CharField(source="tipo_tramite.nombre", read_only=True)
    area_actual_nombre = serializers.CharField(source="area_actual.nombre", read_only=True)
    asignado_a_username = serializers.CharField(source="asignado_a.username", read_only=True)

    class Meta:
        model = Tramite
        fields = (
            "id",
            "numero",
            "titulo",
            "estado",
            "estado_nombre",
            "prioridad",
            "prioridad_nombre",
            "tipo_tramite",
            "tipo_tramite_nombre",
            "area_actual",
            "area_actual_nombre",
            "asignado_a",
            "asignado_a_username",
            "origen",
            "fecha_inicio",
            "activo",
            "created_at",
            "updated_at",
        )


class TramiteDetailSerializer(serializers.ModelSerializer):
    estado_nombre = serializers.CharField(source="estado.nombre", read_only=True)
    prioridad_nombre = serializers.CharField(source="prioridad.nombre", read_only=True)
    tipo_tramite_nombre = serializers.CharField(source="tipo_tramite.nombre", read_only=True)
    area_actual_nombre = serializers.CharField(source="area_actual.nombre", read_only=True)
    area_responsable_nombre = serializers.CharField(source="area_responsable.nombre", read_only=True)
    ciudadano_nombre = serializers.CharField(source="ciudadano.nombre_completo", read_only=True)
    asignado_a_username = serializers.CharField(source="asignado_a.username", read_only=True)
    datos_dinamicos = TramiteDatoDinamicoSerializer(many=True, read_only=True)

    class Meta:
        model = Tramite
        fields = "__all__"
        read_only_fields = ("id", "numero", "created_at", "updated_at")


class TramiteWriteSerializer(serializers.ModelSerializer):
    datos_dinamicos = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)
    comentario_transicion = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Tramite
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
        tipo_tramite = validated_data.get("tipo_tramite")
        municipio = validated_data.get("municipio")

        if not validated_data.get("estado"):
            estado_inicial = obtener_estado_inicial(municipio=municipio)
            if estado_inicial:
                validated_data["estado"] = estado_inicial

        if not validated_data.get("prioridad"):
            prioridad = getattr(tipo_tramite, "prioridad_default", None) if tipo_tramite else None
            if not prioridad:
                prioridad = obtener_prioridad_base(municipio=municipio)
            if prioridad:
                validated_data["prioridad"] = prioridad

        if not validated_data.get("area_actual") and tipo_tramite:
            validated_data["area_actual"] = tipo_tramite.area
        if not validated_data.get("area_responsable") and validated_data.get("area_actual"):
            validated_data["area_responsable"] = validated_data["area_actual"]
        if not validated_data.get("fecha_inicio"):
            validated_data["fecha_inicio"] = timezone.now()
        if not validated_data.get("sla_horas") and tipo_tramite and tipo_tramite.sla_horas:
            validated_data["sla_horas"] = tipo_tramite.sla_horas
        if user:
            validated_data.setdefault("creado_por", user)
            validated_data.setdefault("actualizado_por", user)

        try:
            datos_preparados = validar_y_preparar_datos_dinamicos(tipo_tramite=tipo_tramite, datos=datos_dinamicos)
        except ValueError as exc:
            raise serializers.ValidationError({"datos_dinamicos": str(exc)}) from exc

        tramite = super().create(validated_data)
        guardar_datos_dinamicos(tramite=tramite, datos_preparados=datos_preparados)
        try:
            validar_requisitos_runtime_tramite(
                tramite=tramite,
                tipo_tramite=tramite.tipo_tramite,
                estado_objetivo=tramite.estado,
                datos_preparados=datos_preparados,
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc
        registrar_historial(
            tramite=tramite,
            accion="creacion",
            usuario=user,
            estado_nuevo=tramite.estado,
            area_nueva=tramite.area_actual,
            asignado_nuevo=tramite.asignado_a,
            visible_ciudadano=True,
            metadata={"origen": tramite.origen},
        )
        return tramite

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
            validar_transicion_estado_tramite(
                tramite=instance,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                usuario=user,
                comentario=comentario_transicion,
                area_actual=area_nueva,
                asignado_a=asignado_nuevo,
                area_responsable=area_responsable_nueva,
            )
            if estado_anterior != estado_nuevo and not area_responsable_nueva:
                validated_data.setdefault("area_responsable", area_nueva or area_responsable_nueva)
        except ValueError as exc:
            raise serializers.ValidationError({"estado": str(exc)}) from exc

        tramite = super().update(instance, validated_data)
        if datos_dinamicos is not None:
            try:
                datos_preparados = validar_y_preparar_datos_dinamicos(
                    tipo_tramite=tramite.tipo_tramite,
                    datos=datos_dinamicos,
                )
            except ValueError as exc:
                raise serializers.ValidationError({"datos_dinamicos": str(exc)}) from exc
            guardar_datos_dinamicos(tramite=tramite, datos_preparados=datos_preparados)
        else:
            datos_preparados = None

        try:
            validar_requisitos_runtime_tramite(
                tramite=tramite,
                tipo_tramite=tramite.tipo_tramite,
                estado_objetivo=tramite.estado,
                datos_preparados=datos_preparados,
            )
        except ValueError as exc:
            raise serializers.ValidationError({"detail": str(exc)}) from exc

        cambio_estado = estado_anterior != tramite.estado
        cambio_area = area_anterior != tramite.area_actual
        cambio_asignado = asignado_anterior != tramite.asignado_a
        if not (cambio_estado or cambio_area or cambio_asignado):
            return tramite

        if cambio_estado and not (cambio_area or cambio_asignado):
            accion = "cambio_estado"
        elif cambio_area and not (cambio_estado or cambio_asignado):
            accion = "cambio_area"
        elif cambio_asignado and not (cambio_estado or cambio_area):
            accion = "cambio_asignado"
        else:
            accion = "actualizacion"

        registrar_historial(
            tramite=tramite,
            accion=accion,
            usuario=user,
            estado_anterior=estado_anterior if cambio_estado else None,
            estado_nuevo=tramite.estado if cambio_estado else None,
            area_anterior=area_anterior if cambio_area else None,
            area_nueva=tramite.area_actual if cambio_area else None,
            asignado_anterior=asignado_anterior if cambio_asignado else None,
            asignado_nuevo=tramite.asignado_a if cambio_asignado else None,
            comentario=comentario_transicion if cambio_estado else "",
            metadata={
                "cambio_estado": cambio_estado,
                "cambio_area": cambio_area,
                "cambio_asignado": cambio_asignado,
                "campos_dinamicos_actualizados": bool(datos_preparados),
            },
        )
        return tramite


class TramiteHistorialSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    estado_anterior_nombre = serializers.CharField(source="estado_anterior.nombre", read_only=True)
    estado_nuevo_nombre = serializers.CharField(source="estado_nuevo.nombre", read_only=True)
    area_anterior_nombre = serializers.CharField(source="area_anterior.nombre", read_only=True)
    area_nueva_nombre = serializers.CharField(source="area_nueva.nombre", read_only=True)
    asignado_anterior_username = serializers.CharField(source="asignado_anterior.username", read_only=True)
    asignado_nuevo_username = serializers.CharField(source="asignado_nuevo.username", read_only=True)

    class Meta:
        model = TramiteHistorial
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")


class TramiteAdjuntoSerializer(serializers.ModelSerializer):
    subido_por_username = serializers.CharField(source="subido_por.username", read_only=True)

    class Meta:
        model = TramiteAdjunto
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "subido_por")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["subido_por"] = request.user
        return super().create(validated_data)


class TramiteComentarioSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    ciudadano_nombre = serializers.CharField(source="ciudadano.nombre_completo", read_only=True)

    class Meta:
        model = TramiteComentario
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "usuario")

    def create(self, validated_data):
        request = self.context.get("request")
        if request and request.user and request.user.is_authenticated:
            validated_data["usuario"] = request.user
        return super().create(validated_data)


class TramiteAsignacionSerializer(serializers.ModelSerializer):
    usuario_username = serializers.CharField(source="usuario.username", read_only=True)
    asignado_por_username = serializers.CharField(source="asignado_por.username", read_only=True)
    area_nombre = serializers.CharField(source="area.nombre", read_only=True)

    class Meta:
        model = TramiteAsignacion
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at", "asignado_por")

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")
        actor = request.user if request and request.user and request.user.is_authenticated else None
        tramite = validated_data["tramite"]
        area = validated_data["area"]
        usuario = validated_data.get("usuario")
        activa = validated_data.get("activa", True)

        if actor:
            validated_data["asignado_por"] = actor

        if activa:
            tramite.asignaciones.filter(activa=True).update(activa=False, fecha_fin=timezone.now())

        asignacion = super().create(validated_data)

        area_anterior = tramite.area_actual
        asignado_anterior = tramite.asignado_a
        tramite.area_actual = area
        tramite.area_responsable = area
        tramite.asignado_a = usuario
        tramite.actualizado_por = actor
        tramite.save(update_fields=["area_actual", "area_responsable", "asignado_a", "actualizado_por", "updated_at"])

        registrar_historial(
            tramite=tramite,
            accion="asignacion",
            usuario=actor,
            area_anterior=area_anterior,
            area_nueva=tramite.area_actual,
            asignado_anterior=asignado_anterior,
            asignado_nuevo=tramite.asignado_a,
            comentario=asignacion.motivo or "",
            metadata={"asignacion_id": asignacion.id},
        )
        return asignacion
