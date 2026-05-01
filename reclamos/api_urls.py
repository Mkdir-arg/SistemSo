from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    AreaViewSet,
    CampoDinamicoOpcionViewSet,
    CampoDinamicoReclamoViewSet,
    EstadoReclamoViewSet,
    EstadoReclamoTransicionViewSet,
    PrioridadReclamoViewSet,
    ReclamoAdjuntoViewSet,
    ReclamoAsignacionViewSet,
    ReclamoComentarioViewSet,
    ReclamoDatoDinamicoViewSet,
    ReclamoHistorialViewSet,
    ReclamoViewSet,
    TipoReclamoViewSet,
)

router = DefaultRouter()
router.register(r"areas", AreaViewSet)
router.register(r"tipos", TipoReclamoViewSet)
router.register(r"estados", EstadoReclamoViewSet)
router.register(r"estados-transiciones", EstadoReclamoTransicionViewSet)
router.register(r"prioridades", PrioridadReclamoViewSet)
router.register(r"campos-dinamicos", CampoDinamicoReclamoViewSet)
router.register(r"campos-dinamicos-opciones", CampoDinamicoOpcionViewSet)
router.register(r"reclamos", ReclamoViewSet)
router.register(r"datos-dinamicos", ReclamoDatoDinamicoViewSet)
router.register(r"historial", ReclamoHistorialViewSet)
router.register(r"comentarios", ReclamoComentarioViewSet)
router.register(r"adjuntos", ReclamoAdjuntoViewSet)
router.register(r"asignaciones", ReclamoAsignacionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
