from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .api_views import (
    AreaTramiteViewSet,
    CampoDinamicoOpcionViewSet,
    CampoDinamicoTramiteViewSet,
    EstadoTramiteViewSet,
    EstadoTramiteTransicionViewSet,
    PrioridadTramiteViewSet,
    RequisitoTramiteViewSet,
    TipoTramiteViewSet,
    TramiteAdjuntoViewSet,
    TramiteAsignacionViewSet,
    TramiteComentarioViewSet,
    TramiteDatoDinamicoViewSet,
    TramiteHistorialViewSet,
    TramiteViewSet,
)

router = DefaultRouter()
router.register(r"areas", AreaTramiteViewSet)
router.register(r"tipos", TipoTramiteViewSet)
router.register(r"estados", EstadoTramiteViewSet)
router.register(r"estados-transiciones", EstadoTramiteTransicionViewSet)
router.register(r"prioridades", PrioridadTramiteViewSet)
router.register(r"requisitos", RequisitoTramiteViewSet)
router.register(r"campos-dinamicos", CampoDinamicoTramiteViewSet)
router.register(r"campos-dinamicos-opciones", CampoDinamicoOpcionViewSet)
router.register(r"tramites", TramiteViewSet)
router.register(r"datos-dinamicos", TramiteDatoDinamicoViewSet)
router.register(r"historial", TramiteHistorialViewSet)
router.register(r"comentarios", TramiteComentarioViewSet)
router.register(r"adjuntos", TramiteAdjuntoViewSet)
router.register(r"asignaciones", TramiteAsignacionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
