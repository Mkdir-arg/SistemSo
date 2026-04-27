from django.urls import path
from conversaciones.interfaces.api import views as api_views
from conversaciones.interfaces.api.views.extra import conversacion_detalle

app_name = 'conversaciones_api'

urlpatterns = [
    path('alertas/count/', api_views.alertas_conversaciones_count, name='alertas_count'),
    path('alertas/preview/', api_views.alertas_conversaciones_preview, name='alertas_preview'),
    path('alertas/marcar-leidos/<int:conversacion_id>/', api_views.marcar_mensajes_leidos, name='marcar_leidos'),
    path('conversacion/<int:conversacion_id>/', conversacion_detalle, name='conversacion_detalle'),
]
