from django.urls import path
from turnos.interfaces.web.views import backoffice as v

app_name = 'turnos'

urlpatterns = [
    # Dashboard
    path('', v.backoffice_home, name='home'),

    # Configuraciones
    path('configuraciones/', v.configuracion_lista, name='configuracion_lista'),
    path('configuraciones/nueva/', v.configuracion_crear, name='configuracion_crear'),
    path('configuraciones/<int:pk>/editar/', v.configuracion_editar, name='configuracion_editar'),
    path('configuraciones/<int:pk>/eliminar/', v.configuracion_eliminar, name='configuracion_eliminar'),
    path('sedes/', v.sedes_lista, name='sedes_lista'),
    path('sedes/nueva/', v.sede_crear, name='sede_crear'),
    path('sedes/<int:pk>/', v.sede_detalle, name='sede_detalle'),
    path('sedes/<int:pk>/editar/', v.sede_editar, name='sede_editar'),

    # Disponibilidad (grilla semanal)
    path('configuraciones/<int:pk>/disponibilidad/', v.disponibilidad_grilla, name='disponibilidad_grilla'),
    path('configuraciones/<int:pk>/disponibilidad/agregar/', v.disponibilidad_agregar, name='disponibilidad_agregar'),
    path('configuraciones/<int:pk>/disponibilidad/<int:disp_pk>/editar/', v.disponibilidad_editar, name='disponibilidad_editar'),
    path('configuraciones/<int:pk>/disponibilidad/<int:disp_pk>/eliminar/', v.disponibilidad_eliminar, name='disponibilidad_eliminar'),

    # Agenda
    path('agenda/', v.agenda, name='agenda'),

    # Bandeja de pendientes
    path('pendientes/', v.bandeja_pendientes, name='bandeja_pendientes'),

    # Detalle y acciones sobre turnos
    path('turnos/<int:pk>/', v.turno_detalle, name='turno_detalle'),
    path('turnos/<int:pk>/aprobar/', v.turno_aprobar, name='turno_aprobar'),
    path('turnos/<int:pk>/rechazar/', v.turno_rechazar, name='turno_rechazar'),
    path('turnos/<int:pk>/cancelar/', v.turno_cancelar, name='turno_cancelar'),
    path('turnos/<int:pk>/completar/', v.turno_completar, name='turno_completar'),

    # API interna
    path('api/slots/', v.api_slots_configuracion, name='api_slots'),
]
