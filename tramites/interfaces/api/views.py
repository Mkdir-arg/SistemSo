from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from reclamos.models import Area

from tramites.models import (
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
from .serializers import (
    AreaTramiteSerializer,
    CampoDinamicoOpcionSerializer,
    CampoDinamicoTramiteSerializer,
    EstadoTramiteSerializer,
    EstadoTramiteTransicionSerializer,
    PrioridadTramiteSerializer,
    RequisitoTramiteSerializer,
    TipoTramiteSerializer,
    TramiteAdjuntoSerializer,
    TramiteAsignacionSerializer,
    TramiteComentarioSerializer,
    TramiteDatoDinamicoSerializer,
    TramiteDetailSerializer,
    TramiteHistorialSerializer,
    TramiteListSerializer,
    TramiteWriteSerializer,
)


class AreaTramiteViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.select_related("municipio").all()
    serializer_class = AreaTramiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "municipio"]
    search_fields = ["nombre", "codigo"]
    ordering = ["orden", "nombre"]


class TipoTramiteViewSet(viewsets.ModelViewSet):
    queryset = TipoTramite.objects.select_related("area", "prioridad_default", "municipio").all()
    serializer_class = TipoTramiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "activo",
        "area",
        "municipio",
        "requiere_pago",
        "requiere_turno",
        "permite_online",
        "permite_presencial",
        "requiere_adjunto",
        "requiere_validacion_manual",
    ]
    search_fields = ["nombre", "codigo", "descripcion"]
    ordering = ["orden", "nombre"]


class EstadoTramiteViewSet(viewsets.ModelViewSet):
    queryset = EstadoTramite.objects.select_related("municipio").all()
    serializer_class = EstadoTramiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "es_inicial", "es_final", "municipio"]
    search_fields = ["nombre", "codigo", "descripcion"]
    ordering = ["orden", "nombre"]


class EstadoTramiteTransicionViewSet(viewsets.ModelViewSet):
    queryset = EstadoTramiteTransicion.objects.select_related("estado_origen", "estado_destino").prefetch_related(
        "grupos_permitidos",
        "areas_permitidas",
    )
    serializer_class = EstadoTramiteTransicionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "estado_origen", "estado_destino"]
    search_fields = ["nombre", "descripcion", "estado_origen__nombre", "estado_destino__nombre"]
    ordering = ["estado_origen", "orden", "id"]


class PrioridadTramiteViewSet(viewsets.ModelViewSet):
    queryset = PrioridadTramite.objects.select_related("municipio").all()
    serializer_class = PrioridadTramiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "municipio", "nivel"]
    search_fields = ["nombre", "codigo", "descripcion"]
    ordering = ["nivel", "nombre"]


class RequisitoTramiteViewSet(viewsets.ModelViewSet):
    queryset = RequisitoTramite.objects.select_related("tipo_tramite").all()
    serializer_class = RequisitoTramiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "tipo_tramite", "obligatorio", "requiere_adjunto"]
    search_fields = ["nombre", "descripcion", "tipo_tramite__nombre"]
    ordering = ["tipo_tramite", "orden", "nombre"]


class CampoDinamicoTramiteViewSet(viewsets.ModelViewSet):
    queryset = CampoDinamicoTramite.objects.select_related("tipo_tramite").prefetch_related("opciones")
    serializer_class = CampoDinamicoTramiteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "tipo_tramite", "tipo_dato", "obligatorio"]
    search_fields = ["nombre", "codigo", "descripcion", "tipo_tramite__nombre"]
    ordering = ["tipo_tramite", "orden", "nombre"]


class CampoDinamicoOpcionViewSet(viewsets.ModelViewSet):
    queryset = CampoDinamicoOpcion.objects.select_related("campo", "campo__tipo_tramite")
    serializer_class = CampoDinamicoOpcionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "campo", "campo__tipo_tramite"]
    search_fields = ["etiqueta", "valor", "campo__nombre", "campo__tipo_tramite__nombre"]
    ordering = ["campo", "orden", "etiqueta"]


class TramiteDatoDinamicoViewSet(viewsets.ModelViewSet):
    queryset = TramiteDatoDinamico.objects.select_related("tramite", "campo", "campo__tipo_tramite")
    serializer_class = TramiteDatoDinamicoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "tramite", "campo", "campo__tipo_tramite"]
    search_fields = ["tramite__numero", "campo__nombre", "campo__codigo"]
    ordering = ["tramite", "campo__orden", "id"]


class TramiteViewSet(viewsets.ModelViewSet):
    queryset = Tramite.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "activo",
        "estado",
        "prioridad",
        "area_actual",
        "area_responsable",
        "tipo_tramite",
        "origen",
        "municipio",
        "visible_ciudadano",
        "asignado_a",
    ]
    search_fields = ["numero", "titulo", "descripcion", "externo_id", "dni_contacto", "email_contacto"]
    ordering = ["-fecha_inicio", "-id"]

    def get_queryset(self):
        return Tramite.objects.select_related(
            "tipo_tramite",
            "estado",
            "prioridad",
            "area_actual",
            "area_responsable",
            "ciudadano",
            "provincia",
            "municipio",
            "localidad",
            "asignado_a",
            "creado_por",
            "actualizado_por",
        ).prefetch_related("adjuntos", "comentarios", "asignaciones", "historial")

    def get_serializer_class(self):
        if self.action == "list":
            return TramiteListSerializer
        if self.action == "retrieve":
            return TramiteDetailSerializer
        return TramiteWriteSerializer


class TramiteHistorialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TramiteHistorial.objects.select_related(
        "tramite",
        "usuario",
        "estado_anterior",
        "estado_nuevo",
        "area_anterior",
        "area_nueva",
        "asignado_anterior",
        "asignado_nuevo",
    )
    serializer_class = TramiteHistorialSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tramite", "accion", "visible_ciudadano", "usuario"]
    ordering = ["-fecha", "-id"]


class TramiteComentarioViewSet(viewsets.ModelViewSet):
    queryset = TramiteComentario.objects.select_related("tramite", "usuario", "ciudadano")
    serializer_class = TramiteComentarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tramite", "usuario", "ciudadano", "es_interno", "visible_ciudadano"]
    search_fields = ["comentario", "tramite__numero"]
    ordering = ["-created_at", "-id"]


class TramiteAdjuntoViewSet(viewsets.ModelViewSet):
    queryset = TramiteAdjunto.objects.select_related("tramite", "subido_por")
    serializer_class = TramiteAdjuntoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tramite", "visible_ciudadano", "subido_por"]
    search_fields = ["nombre_original", "tipo_mime", "tramite__numero"]
    ordering = ["-created_at", "-id"]


class TramiteAsignacionViewSet(viewsets.ModelViewSet):
    queryset = TramiteAsignacion.objects.select_related("tramite", "area", "usuario", "asignado_por")
    serializer_class = TramiteAsignacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tramite", "area", "usuario", "activa"]
    search_fields = ["tramite__numero", "area__nombre", "usuario__username", "motivo"]
    ordering = ["-fecha_asignacion", "-id"]
