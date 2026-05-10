from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

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
from .serializers import (
    AreaSerializer,
    CampoDinamicoOpcionSerializer,
    CampoDinamicoReclamoSerializer,
    EstadoReclamoSerializer,
    EstadoReclamoTransicionSerializer,
    PrioridadReclamoSerializer,
    ReclamoAdjuntoSerializer,
    ReclamoAsignacionSerializer,
    ReclamoComentarioSerializer,
    ReclamoDatoDinamicoSerializer,
    ReclamoDetailSerializer,
    ReclamoHistorialSerializer,
    ReclamoListSerializer,
    ReclamoWriteSerializer,
    TipoReclamoSerializer,
)


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "parent"]
    search_fields = ["nombre", "codigo"]
    ordering = ["orden", "nombre"]


class TipoReclamoViewSet(viewsets.ModelViewSet):
    queryset = TipoReclamo.objects.select_related("area", "prioridad_default").all()
    serializer_class = TipoReclamoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "area", "permite_anonimo"]
    search_fields = ["nombre", "descripcion"]
    ordering = ["orden", "nombre"]


class EstadoReclamoViewSet(viewsets.ModelViewSet):
    queryset = EstadoReclamo.objects.all()
    serializer_class = EstadoReclamoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "es_inicial", "es_final"]
    search_fields = ["nombre", "codigo", "descripcion"]
    ordering = ["orden", "nombre"]


class EstadoReclamoTransicionViewSet(viewsets.ModelViewSet):
    queryset = EstadoReclamoTransicion.objects.select_related("estado_origen", "estado_destino").prefetch_related(
        "grupos_permitidos",
        "areas_permitidas",
    )
    serializer_class = EstadoReclamoTransicionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "estado_origen", "estado_destino"]
    search_fields = ["nombre", "descripcion", "estado_origen__nombre", "estado_destino__nombre"]
    ordering = ["estado_origen", "orden", "id"]


class PrioridadReclamoViewSet(viewsets.ModelViewSet):
    queryset = PrioridadReclamo.objects.all()
    serializer_class = PrioridadReclamoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "nivel"]
    search_fields = ["nombre", "codigo", "descripcion"]
    ordering = ["nivel", "nombre"]


class CampoDinamicoReclamoViewSet(viewsets.ModelViewSet):
    queryset = CampoDinamicoReclamo.objects.select_related("tipo_reclamo").prefetch_related("opciones")
    serializer_class = CampoDinamicoReclamoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "tipo_reclamo", "tipo_dato", "obligatorio"]
    search_fields = ["nombre", "codigo", "descripcion", "tipo_reclamo__nombre"]
    ordering = ["tipo_reclamo", "orden", "nombre"]


class CampoDinamicoOpcionViewSet(viewsets.ModelViewSet):
    queryset = CampoDinamicoOpcion.objects.select_related("campo", "campo__tipo_reclamo")
    serializer_class = CampoDinamicoOpcionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "campo", "campo__tipo_reclamo"]
    search_fields = ["etiqueta", "valor", "campo__nombre", "campo__tipo_reclamo__nombre"]
    ordering = ["campo", "orden", "etiqueta"]


class ReclamoDatoDinamicoViewSet(viewsets.ModelViewSet):
    queryset = ReclamoDatoDinamico.objects.select_related("reclamo", "campo", "campo__tipo_reclamo")
    serializer_class = ReclamoDatoDinamicoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["activo", "reclamo", "campo", "campo__tipo_reclamo"]
    search_fields = ["reclamo__numero", "campo__nombre", "campo__codigo"]
    ordering = ["reclamo", "campo__orden", "id"]


class ReclamoViewSet(viewsets.ModelViewSet):
    queryset = Reclamo.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "activo",
        "estado",
        "prioridad",
        "area_actual",
        "area_responsable",
        "tipo_reclamo",
        "origen",
        "municipio",
        "es_anonimo",
        "visible_ciudadano",
        "asignado_a",
    ]
    search_fields = ["numero", "titulo", "descripcion", "externo_id", "dni_contacto", "email_contacto"]
    ordering = ["-fecha_ingreso", "-id"]

    def get_queryset(self):
        return Reclamo.objects.select_related(
            "tipo_reclamo",
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
            return ReclamoListSerializer
        if self.action == "retrieve":
            return ReclamoDetailSerializer
        return ReclamoWriteSerializer


class ReclamoHistorialViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReclamoHistorial.objects.select_related(
        "reclamo",
        "usuario",
        "estado_anterior",
        "estado_nuevo",
        "area_anterior",
        "area_nueva",
        "asignado_anterior",
        "asignado_nuevo",
    )
    serializer_class = ReclamoHistorialSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["reclamo", "accion", "visible_ciudadano", "usuario"]
    ordering = ["-fecha", "-id"]


class ReclamoComentarioViewSet(viewsets.ModelViewSet):
    queryset = ReclamoComentario.objects.select_related("reclamo", "usuario", "ciudadano")
    serializer_class = ReclamoComentarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["reclamo", "usuario", "ciudadano", "es_interno", "visible_ciudadano"]
    search_fields = ["comentario", "reclamo__numero"]
    ordering = ["-created_at", "-id"]


class ReclamoAdjuntoViewSet(viewsets.ModelViewSet):
    queryset = ReclamoAdjunto.objects.select_related("reclamo", "subido_por")
    serializer_class = ReclamoAdjuntoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["reclamo", "visible_ciudadano", "subido_por"]
    search_fields = ["nombre_original", "tipo_mime", "reclamo__numero"]
    ordering = ["-created_at", "-id"]


class ReclamoAsignacionViewSet(viewsets.ModelViewSet):
    queryset = ReclamoAsignacion.objects.select_related("reclamo", "area", "usuario", "asignado_por")
    serializer_class = ReclamoAsignacionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["reclamo", "area", "usuario", "activa"]
    search_fields = ["reclamo__numero", "area__nombre", "usuario__username", "motivo"]
    ordering = ["-fecha_asignacion", "-id"]
