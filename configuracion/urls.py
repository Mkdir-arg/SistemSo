from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views
from .views import programas as views_programas

app_name = 'configuracion'

urlpatterns = [
    # Provincias
    path('provincias/', login_required(views.ProvinciaListView.as_view()), name='provincias'),
    path('provincias/crear/', login_required(views.ProvinciaCreateView.as_view()), name='provincia_crear'),
    path('provincias/<int:pk>/editar/', login_required(views.ProvinciaUpdateView.as_view()), name='provincia_editar'),
    path('provincias/<int:pk>/eliminar/', login_required(views.ProvinciaDeleteView.as_view()), name='provincia_eliminar'),
    
    # Municipios
    path('municipios/', login_required(views.MunicipioListView.as_view()), name='municipios'),
    path('municipios/crear/', login_required(views.MunicipioCreateView.as_view()), name='municipio_crear'),
    path('municipios/<int:pk>/editar/', login_required(views.MunicipioUpdateView.as_view()), name='municipio_editar'),
    path('municipios/<int:pk>/eliminar/', login_required(views.MunicipioDeleteView.as_view()), name='municipio_eliminar'),
    
    # Localidades
    path('localidades/', login_required(views.LocalidadListView.as_view()), name='localidades'),
    path('localidades/crear/', login_required(views.LocalidadCreateView.as_view()), name='localidad_crear'),
    path('localidades/<int:pk>/editar/', login_required(views.LocalidadUpdateView.as_view()), name='localidad_editar'),
    path('localidades/<int:pk>/eliminar/', login_required(views.LocalidadDeleteView.as_view()), name='localidad_eliminar'),

    # Reclamos (configuracion)
    path('reclamos/', login_required(views.ReclamoCatalogosConfigView.as_view()), name='reclamos'),
    path('reclamos/configuracion/', login_required(views.ReclamoCatalogosConfigView.as_view()), name='reclamos_configuracion'),
    # Reclamos (operacion)
    path('reclamos/listado/', login_required(views.ReclamoConfigListView.as_view()), name='reclamos_listado'),
    path('reclamos/listado/crear/', login_required(views.ReclamoConfigCreateView.as_view()), name='reclamo_crear'),
    path('reclamos/listado/<int:pk>/', login_required(views.ReclamoConfigDetailView.as_view()), name='reclamo_detalle'),
    path('reclamos/configuracion/areas/', login_required(views.AreaReclamoListView.as_view()), name='reclamos_areas'),
    path('reclamos/configuracion/areas/crear/', login_required(views.AreaReclamoCreateView.as_view()), name='reclamos_areas_crear'),
    path('reclamos/configuracion/areas/<int:pk>/editar/', login_required(views.AreaReclamoUpdateView.as_view()), name='reclamos_areas_editar'),
    path('reclamos/configuracion/areas/<int:pk>/eliminar/', login_required(views.AreaReclamoDeleteView.as_view()), name='reclamos_areas_eliminar'),
    path('reclamos/configuracion/tipos/', login_required(views.TipoReclamoListView.as_view()), name='reclamos_tipos'),
    path('reclamos/configuracion/tipos/crear/', login_required(views.TipoReclamoCreateView.as_view()), name='reclamos_tipos_crear'),
    path('reclamos/configuracion/tipos/<int:pk>/editar/', login_required(views.TipoReclamoUpdateView.as_view()), name='reclamos_tipos_editar'),
    path('reclamos/configuracion/tipos/<int:pk>/eliminar/', login_required(views.TipoReclamoDeleteView.as_view()), name='reclamos_tipos_eliminar'),
    path('reclamos/configuracion/estados/', login_required(views.EstadoReclamoListView.as_view()), name='reclamos_estados'),
    path('reclamos/configuracion/estados/crear/', login_required(views.EstadoReclamoCreateView.as_view()), name='reclamos_estados_crear'),
    path('reclamos/configuracion/estados/<int:pk>/editar/', login_required(views.EstadoReclamoUpdateView.as_view()), name='reclamos_estados_editar'),
    path('reclamos/configuracion/estados/<int:pk>/eliminar/', login_required(views.EstadoReclamoDeleteView.as_view()), name='reclamos_estados_eliminar'),
    path('reclamos/configuracion/prioridades/', login_required(views.PrioridadReclamoListView.as_view()), name='reclamos_prioridades'),
    path('reclamos/configuracion/prioridades/crear/', login_required(views.PrioridadReclamoCreateView.as_view()), name='reclamos_prioridades_crear'),
    path('reclamos/configuracion/prioridades/<int:pk>/editar/', login_required(views.PrioridadReclamoUpdateView.as_view()), name='reclamos_prioridades_editar'),
    path('reclamos/configuracion/prioridades/<int:pk>/eliminar/', login_required(views.PrioridadReclamoDeleteView.as_view()), name='reclamos_prioridades_eliminar'),
    path('reclamos/configuracion/transiciones-estado/', login_required(views.EstadoReclamoTransicionListView.as_view()), name='reclamos_transiciones_estado'),
    path('reclamos/configuracion/transiciones-estado/crear/', login_required(views.EstadoReclamoTransicionCreateView.as_view()), name='reclamos_transiciones_estado_crear'),
    path('reclamos/configuracion/transiciones-estado/<int:pk>/editar/', login_required(views.EstadoReclamoTransicionUpdateView.as_view()), name='reclamos_transiciones_estado_editar'),
    path('reclamos/configuracion/transiciones-estado/<int:pk>/eliminar/', login_required(views.EstadoReclamoTransicionDeleteView.as_view()), name='reclamos_transiciones_estado_eliminar'),
    path('reclamos/configuracion/campos-dinamicos/', login_required(views.CampoDinamicoReclamoListView.as_view()), name='reclamos_campos_dinamicos'),
    path('reclamos/configuracion/campos-dinamicos/crear/', login_required(views.CampoDinamicoReclamoCreateView.as_view()), name='reclamos_campos_dinamicos_crear'),
    path('reclamos/configuracion/campos-dinamicos/<int:pk>/editar/', login_required(views.CampoDinamicoReclamoUpdateView.as_view()), name='reclamos_campos_dinamicos_editar'),
    path('reclamos/configuracion/campos-dinamicos/<int:pk>/eliminar/', login_required(views.CampoDinamicoReclamoDeleteView.as_view()), name='reclamos_campos_dinamicos_eliminar'),
    path('reclamos/configuracion/campos-opciones/', login_required(views.CampoDinamicoOpcionListView.as_view()), name='reclamos_campos_opciones'),
    path('reclamos/configuracion/campos-opciones/crear/', login_required(views.CampoDinamicoOpcionCreateView.as_view()), name='reclamos_campos_opciones_crear'),
    path('reclamos/configuracion/campos-opciones/<int:pk>/editar/', login_required(views.CampoDinamicoOpcionUpdateView.as_view()), name='reclamos_campos_opciones_editar'),
    path('reclamos/configuracion/campos-opciones/<int:pk>/eliminar/', login_required(views.CampoDinamicoOpcionDeleteView.as_view()), name='reclamos_campos_opciones_eliminar'),

    # Tramites (configuracion)
    path('tramites/', login_required(views.TramiteCatalogosConfigView.as_view()), name='tramites'),
    path('tramites/configuracion/', login_required(views.TramiteCatalogosConfigView.as_view()), name='tramites_configuracion'),
    # Tramites (operacion)
    path('tramites/listado/', login_required(views.TramiteConfigListView.as_view()), name='tramites_listado'),
    path('tramites/listado/crear/', login_required(views.TramiteConfigCreateView.as_view()), name='tramite_crear'),
    path('tramites/listado/<int:pk>/', login_required(views.TramiteConfigDetailView.as_view()), name='tramite_detalle'),
    path('tramites/configuracion/areas/', login_required(views.AreaTramiteListView.as_view()), name='tramites_areas'),
    path('tramites/configuracion/areas/crear/', login_required(views.AreaTramiteCreateView.as_view()), name='tramites_areas_crear'),
    path('tramites/configuracion/areas/<int:pk>/editar/', login_required(views.AreaTramiteUpdateView.as_view()), name='tramites_areas_editar'),
    path('tramites/configuracion/areas/<int:pk>/eliminar/', login_required(views.AreaTramiteDeleteView.as_view()), name='tramites_areas_eliminar'),
    path('tramites/configuracion/tipos/', login_required(views.TipoTramiteListView.as_view()), name='tramites_tipos'),
    path('tramites/configuracion/tipos/crear/', login_required(views.TipoTramiteCreateView.as_view()), name='tramites_tipos_crear'),
    path('tramites/configuracion/tipos/<int:pk>/editar/', login_required(views.TipoTramiteUpdateView.as_view()), name='tramites_tipos_editar'),
    path('tramites/configuracion/tipos/<int:pk>/eliminar/', login_required(views.TipoTramiteDeleteView.as_view()), name='tramites_tipos_eliminar'),
    path('tramites/configuracion/estados/', login_required(views.EstadoTramiteListView.as_view()), name='tramites_estados'),
    path('tramites/configuracion/estados/crear/', login_required(views.EstadoTramiteCreateView.as_view()), name='tramites_estados_crear'),
    path('tramites/configuracion/estados/<int:pk>/editar/', login_required(views.EstadoTramiteUpdateView.as_view()), name='tramites_estados_editar'),
    path('tramites/configuracion/estados/<int:pk>/eliminar/', login_required(views.EstadoTramiteDeleteView.as_view()), name='tramites_estados_eliminar'),
    path('tramites/configuracion/prioridades/', login_required(views.PrioridadTramiteListView.as_view()), name='tramites_prioridades'),
    path('tramites/configuracion/prioridades/crear/', login_required(views.PrioridadTramiteCreateView.as_view()), name='tramites_prioridades_crear'),
    path('tramites/configuracion/prioridades/<int:pk>/editar/', login_required(views.PrioridadTramiteUpdateView.as_view()), name='tramites_prioridades_editar'),
    path('tramites/configuracion/prioridades/<int:pk>/eliminar/', login_required(views.PrioridadTramiteDeleteView.as_view()), name='tramites_prioridades_eliminar'),
    path('tramites/configuracion/transiciones-estado/', login_required(views.EstadoTramiteTransicionListView.as_view()), name='tramites_transiciones_estado'),
    path('tramites/configuracion/transiciones-estado/crear/', login_required(views.EstadoTramiteTransicionCreateView.as_view()), name='tramites_transiciones_estado_crear'),
    path('tramites/configuracion/transiciones-estado/<int:pk>/editar/', login_required(views.EstadoTramiteTransicionUpdateView.as_view()), name='tramites_transiciones_estado_editar'),
    path('tramites/configuracion/transiciones-estado/<int:pk>/eliminar/', login_required(views.EstadoTramiteTransicionDeleteView.as_view()), name='tramites_transiciones_estado_eliminar'),
    path('tramites/configuracion/requisitos/', login_required(views.RequisitoTramiteListView.as_view()), name='tramites_requisitos'),
    path('tramites/configuracion/requisitos/crear/', login_required(views.RequisitoTramiteCreateView.as_view()), name='tramites_requisitos_crear'),
    path('tramites/configuracion/requisitos/<int:pk>/editar/', login_required(views.RequisitoTramiteUpdateView.as_view()), name='tramites_requisitos_editar'),
    path('tramites/configuracion/requisitos/<int:pk>/eliminar/', login_required(views.RequisitoTramiteDeleteView.as_view()), name='tramites_requisitos_eliminar'),
    path('tramites/configuracion/campos-dinamicos/', login_required(views.CampoDinamicoTramiteListView.as_view()), name='tramites_campos_dinamicos'),
    path('tramites/configuracion/campos-dinamicos/crear/', login_required(views.CampoDinamicoTramiteCreateView.as_view()), name='tramites_campos_dinamicos_crear'),
    path('tramites/configuracion/campos-dinamicos/<int:pk>/editar/', login_required(views.CampoDinamicoTramiteUpdateView.as_view()), name='tramites_campos_dinamicos_editar'),
    path('tramites/configuracion/campos-dinamicos/<int:pk>/eliminar/', login_required(views.CampoDinamicoTramiteDeleteView.as_view()), name='tramites_campos_dinamicos_eliminar'),
    path('tramites/configuracion/campos-opciones/', login_required(views.CampoDinamicoOpcionListView.as_view()), name='tramites_campos_opciones'),
    path('tramites/configuracion/campos-opciones/crear/', login_required(views.CampoDinamicoOpcionCreateView.as_view()), name='tramites_campos_opciones_crear'),
    path('tramites/configuracion/campos-opciones/<int:pk>/editar/', login_required(views.CampoDinamicoOpcionUpdateView.as_view()), name='tramites_campos_opciones_editar'),
    path('tramites/configuracion/campos-opciones/<int:pk>/eliminar/', login_required(views.CampoDinamicoOpcionDeleteView.as_view()), name='tramites_campos_opciones_eliminar'),
    
    # Instituciones
    path('instituciones/<int:pk>/', login_required(views.InstitucionDetailView.as_view()), name='institucion_detalle'),
    
    # Actividades
    path('actividades/<int:pk>/', login_required(views.ActividadDetailView.as_view()), name='actividad_detalle'),
    path('actividades/<int:actividad_pk>/staff/crear/', login_required(views.StaffActividadCreateView.as_view()), name='staff_crear'),
    path('actividades/<int:actividad_pk>/buscar-personal/', views.buscar_personal_ajax, name='buscar_personal_ajax'),
    path('derivaciones/<int:pk>/aceptar/', login_required(views.DerivacionAceptarView.as_view()), name='derivacion_aceptar'),
    path('derivaciones/<int:pk>/rechazar/', login_required(views.DerivacionRechazarView.as_view()), name='derivacion_rechazar'),
    path('inscriptos/<int:pk>/editar/', login_required(views.InscriptoEditarView.as_view()), name='inscripto_editar'),
    path('actividades/<int:pk>/editar/', login_required(views.ActividadEditarView.as_view()), name='actividad_editar'),
    path('staff/<int:pk>/editar/', login_required(views.StaffEditarView.as_view()), name='staff_editar'),
    path('staff/<int:pk>/desasignar/', login_required(views.StaffDesasignarView.as_view()), name='staff_desasignar'),
    path('actividades/<int:pk>/asistencia/', login_required(views.AsistenciaView.as_view()), name='asistencia'),
    path('actividades/<int:pk>/tomar-asistencia/', login_required(views.TomarAsistenciaView.as_view()), name='tomar_asistencia'),
    path('actividades/<int:actividad_pk>/inscribir/', login_required(views.InscripcionDirectaView.as_view()), name='inscripcion_directa'),
    path('actividades/<int:pk>/clases/', login_required(views.ClaseListView.as_view()), name='clase_lista'),
    path('actividades/<int:actividad_pk>/clases/crear/', login_required(views.ClaseCreateView.as_view()), name='clase_crear'),
    path('clases/<int:pk>/editar/', login_required(views.ClaseEditarView.as_view()), name='clase_editar'),
    path('clases/<int:pk>/eliminar/', login_required(views.ClaseEliminarView.as_view()), name='clase_eliminar'),
    path('clases/<int:pk>/asistencia/', login_required(views.ClaseAsistenciaView.as_view()), name='clase_asistencia'),
    
    # Gestión de legajo institucional
    path('instituciones/<int:institucion_pk>/personal/crear/', login_required(views.PersonalInstitucionCreateView.as_view()), name='personal_crear'),
    path('instituciones/<int:institucion_pk>/evaluaciones/crear/', login_required(views.EvaluacionInstitucionCreateView.as_view()), name='evaluacion_crear'),
    path('instituciones/<int:institucion_pk>/planes/crear/', login_required(views.PlanFortalecimientoCreateView.as_view()), name='plan_crear'),
    path('instituciones/<int:institucion_pk>/indicadores/crear/', login_required(views.IndicadorInstitucionCreateView.as_view()), name='indicador_crear'),
    path('instituciones/<int:pk>/documentos/subir/', login_required(views.documento_subir), name='documento_subir'),
    

    
    # Secretarías y Subsecretarías
    path('secretarias/', login_required(views.SecretariaListView.as_view()), name='secretarias'),
    path('secretarias/crear/', login_required(views.SecretariaCreateView.as_view()), name='secretaria_crear'),
    path('secretarias/<int:pk>/editar/', login_required(views.SecretariaUpdateView.as_view()), name='secretaria_editar'),
    path('secretarias/<int:pk>/eliminar/', login_required(views.SecretariaDeleteView.as_view()), name='secretaria_eliminar'),
    path('subsecretarias/', login_required(views.SubsecretariaListView.as_view()), name='subsecretarias'),
    path('subsecretarias/crear/', login_required(views.SubsecretariaCreateView.as_view()), name='subsecretaria_crear'),
    path('subsecretarias/<int:pk>/editar/', login_required(views.SubsecretariaUpdateView.as_view()), name='subsecretaria_editar'),
    path('subsecretarias/<int:pk>/eliminar/', login_required(views.SubsecretariaDeleteView.as_view()), name='subsecretaria_eliminar'),

    # Programas — wizard de configuración
    path('programas/', views_programas.programa_list, name='programas'),
    path('programas/nuevo/paso1/', views_programas.programa_wizard_paso1, name='programa_wizard_paso1'),
    path('programas/nuevo/paso2/', views_programas.programa_wizard_paso2, name='programa_wizard_paso2'),
    path('programas/nuevo/paso3/', views_programas.programa_wizard_paso3, name='programa_wizard_paso3'),
    path('programas/nuevo/paso4/', views_programas.programa_wizard_paso4, name='programa_wizard_paso4'),
    path('programas/<int:pk>/editar/paso1/', views_programas.programa_editar_paso1, name='programa_editar_paso1'),
    path('programas/<int:pk>/editar/paso2/', views_programas.programa_editar_paso2, name='programa_editar_paso2'),
    path('programas/<int:pk>/editar/paso3/', views_programas.programa_editar_paso3, name='programa_editar_paso3'),
    path('programas/<int:pk>/editar/paso4/', views_programas.programa_editar_paso4, name='programa_editar_paso4'),
    path('programas/<int:pk>/estado/', views_programas.programa_cambiar_estado, name='programa_cambiar_estado'),

    # Dispositivos (compatibilidad)
    path('dispositivos/', login_required(views.InstitucionListView.as_view()), name='dispositivos'),
    path('dispositivos/crear/', login_required(views.InstitucionCreateView.as_view()), name='dispositivo_crear'),
    path('dispositivos/<int:pk>/editar/', login_required(views.InstitucionUpdateView.as_view()), name='dispositivo_editar'),
    path('dispositivos/<int:pk>/eliminar/', login_required(views.InstitucionDeleteView.as_view()), name='dispositivo_eliminar'),
]
