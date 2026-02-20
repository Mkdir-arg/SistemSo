from django.urls import path
from . import views
from . import views_dashboard_simple as views_simple
from . import views_simple_contactos as views_contactos_simple
from . import views_alertas
from . import views_cursos
from . import views_derivacion
from . import views_api_derivaciones
from . import views_institucional
from . import views_programas

app_name = 'legajos'

urlpatterns = [
    path('', views.LegajoListView.as_view(), name='lista'),
    path('nuevo/', views.LegajoCreateView.as_view(), name='nuevo'),
    path('ciudadanos/', views.CiudadanoListView.as_view(), name='ciudadanos'),
    path('ciudadanos/nuevo/', views.CiudadanoCreateView.as_view(), name='ciudadano_nuevo'),
    path('ciudadanos/confirmar/', views.CiudadanoConfirmarView.as_view(), name='ciudadano_confirmar'),
    path('ciudadanos/manual/', views.CiudadanoManualView.as_view(), name='ciudadano_manual'),
    path('ciudadanos/<int:pk>/', views.CiudadanoDetailView.as_view(), name='ciudadano_detalle'),
    path('ciudadanos/<int:pk>/editar/', views.CiudadanoUpdateView.as_view(), name='ciudadano_editar'),
    
    # ========================================================================
    # GESTIÓN OPERATIVA DE PROGRAMAS
    # ========================================================================
    
    path('programas/', views_programas.ProgramaListView.as_view(), name='programas'),
    path('programas/<int:pk>/', views_programas.ProgramaDetailView.as_view(), name='programa_detalle'),
    
    # ========================================================================
    # SISTEMA NODO - GESTIÓN PROGRAMÁTICA INSTITUCIONAL
    # ========================================================================
    
    # Detalle institucional con solapas dinámicas
    path('instituciones/<int:pk>/detalle-programatico/', 
         views_institucional.institucion_detalle_programatico, 
         name='institucion_detalle_programatico'),
    
    # Derivaciones por programa
    path('programa/<int:institucion_programa_id>/derivaciones/', 
         views_institucional.programa_derivaciones, 
         name='programa_derivaciones'),
    path('derivacion/<int:derivacion_id>/aceptar/', 
         views_institucional.aceptar_derivacion, 
         name='derivacion_aceptar'),
    path('derivacion/<int:derivacion_id>/rechazar/', 
         views_institucional.rechazar_derivacion_view, 
         name='derivacion_rechazar'),
    
    # Casos por programa
    path('programa/<int:institucion_programa_id>/casos/', 
         views_institucional.programa_casos, 
         name='programa_casos'),
    path('caso/<int:caso_id>/', 
         views_institucional.caso_detalle, 
         name='caso_detalle'),
    path('caso/<int:caso_id>/cambiar-estado/', 
         views_institucional.cambiar_estado_caso_view, 
         name='caso_cambiar_estado'),
    
    # API Indicadores
    path('programa/<int:institucion_programa_id>/indicadores/', 
         views_institucional.api_programa_indicadores, 
         name='api_programa_indicadores'),
    
    # ========================================================================
    path('', views.LegajoListView.as_view(), name='lista'),
    path('nuevo/', views.LegajoCreateView.as_view(), name='nuevo'),
    path('ciudadanos/', views.CiudadanoListView.as_view(), name='ciudadanos'),
    path('ciudadanos/nuevo/', views.CiudadanoCreateView.as_view(), name='ciudadano_nuevo'),
    path('ciudadanos/confirmar/', views.CiudadanoConfirmarView.as_view(), name='ciudadano_confirmar'),
    path('ciudadanos/manual/', views.CiudadanoManualView.as_view(), name='ciudadano_manual'),
    path('ciudadanos/<int:pk>/', views.CiudadanoDetailView.as_view(), name='ciudadano_detalle'),
    path('ciudadanos/<int:pk>/editar/', views.CiudadanoUpdateView.as_view(), name='ciudadano_editar'),
    
    # Derivación a Programas
    path('ciudadanos/<int:ciudadano_id>/derivar-programa/', views_derivacion.derivar_programa_view, name='derivar_programa'),
    
    # API Derivaciones de Programas
    path('ciudadanos/<int:ciudadano_id>/derivaciones-programa/<int:programa_id>/', views_api_derivaciones.derivaciones_programa_api, name='derivaciones_programa_api'),
    
    path('admision/paso1/', views.AdmisionPaso1View.as_view(), name='admision_paso1'),
    path('admision/paso2/', views.AdmisionPaso2View.as_view(), name='admision_paso2'),
    path('admision/paso3/', views.AdmisionPaso3View.as_view(), name='admision_paso3'),
    # Evaluaciones
    path('<uuid:legajo_id>/evaluaciones/', views.EvaluacionListView.as_view(), name='evaluaciones'),
    path('<uuid:legajo_id>/evaluacion/', views.EvaluacionInicialView.as_view(), name='evaluacion'),
    
    # Planes de Intervención
    path('<uuid:legajo_id>/planes/', views.PlanListView.as_view(), name='planes'),
    path('<uuid:legajo_id>/plan/', views.PlanIntervencionView.as_view(), name='plan'),
    path('plan/<int:pk>/editar/', views.PlanUpdateView.as_view(), name='plan_editar'),
    path('plan/<int:pk>/marcar-etapa/', views.marcar_etapa_plan, name='marcar_etapa_plan'),
    
    # Seguimientos
    path('<uuid:legajo_id>/seguimientos/', views.SeguimientoListView.as_view(), name='seguimientos'),
    path('<uuid:legajo_id>/seguimiento/', views.SeguimientoCreateView.as_view(), name='seguimiento_nuevo'),
    path('seguimiento/<int:pk>/editar/', views.SeguimientoUpdateView.as_view(), name='seguimiento_editar'),
    
    # Derivaciones
    path('<uuid:legajo_id>/derivaciones/', views.DerivacionListView.as_view(), name='derivaciones'),
    path('<uuid:legajo_id>/derivacion/', views.DerivacionCreateView.as_view(), name='derivacion_nueva'),
    path('derivacion/<int:pk>/editar/', views.DerivacionUpdateView.as_view(), name='derivacion_editar'),
    path('actividades-por-institucion/<int:institucion_id>/', views.actividades_por_institucion, name='actividades_por_institucion'),
    
    # Eventos Críticos
    path('<uuid:legajo_id>/eventos/', views.EventoListView.as_view(), name='eventos'),
    path('<uuid:legajo_id>/evento/', views.EventoCriticoCreateView.as_view(), name='evento_nuevo'),
    path('evento/<int:pk>/editar/', views.EventoUpdateView.as_view(), name='evento_editar'),
    
    # Inscripción a Actividades
    path('<uuid:legajo_id>/inscribir-actividad/', views.InscribirActividadView.as_view(), name='inscribir_actividad'),
    path('<uuid:legajo_id>/actividades-inscrito/', views.ActividadesInscritoListView.as_view(), name='actividades_inscrito'),
    
    path('<uuid:pk>/', views.LegajoDetailView.as_view(), name='detalle'),
    path('<uuid:pk>/cerrar/', views.LegajoCerrarView.as_view(), name='cerrar'),
    path('<uuid:pk>/reabrir/', views.LegajoReabrirView.as_view(), name='reabrir'),
    path('<uuid:pk>/cambiar-responsable/', views.CambiarResponsableView.as_view(), name='cambiar_responsable'),
    path('reportes/', views.ReportesView.as_view(), name='reportes'),
    path('exportar-csv/', views.ExportarCSVView.as_view(), name='exportar_csv'),
    path('dispositivo/<int:dispositivo_id>/derivaciones/', views.DispositivoDerivacionesView.as_view(), name='dispositivo_derivaciones'),
    path('cerrar-alerta/', views.CerrarAlertaEventoView.as_view(), name='cerrar_alerta'),
    
    # Dashboard Contactos
    path('dashboard-contactos/', views_contactos_simple.dashboard_contactos_simple, name='dashboard_contactos'),
    path('test-contactos/', views_simple.dashboard_contactos_simple, name='test_contactos'),
    path('test-api/', views_simple.test_api, name='test_api'),
    
    # Historial de Contactos
    path('<uuid:legajo_id>/historial-contactos/', views_contactos_simple.historial_contactos_simple, name='historial_contactos'),
    
    # Red de Contactos
    path('<uuid:legajo_id>/red-contactos/', views_contactos_simple.red_contactos_simple, name='red_contactos'),
    
    # API Actividades
    path('ciudadanos/<int:ciudadano_id>/actividades/', views_contactos_simple.actividades_ciudadano_api, name='actividades_ciudadano'),
    
    # Subir archivos
    path('<uuid:legajo_id>/subir-archivos/', views_contactos_simple.subir_archivos_legajo, name='subir_archivos'),
    
    # API Archivos
    path('ciudadanos/<int:ciudadano_id>/archivos/', views_contactos_simple.archivos_ciudadano_api, name='archivos_ciudadano'),
    path('ciudadanos/<int:ciudadano_id>/subir-archivos/', views_contactos_simple.subir_archivos_ciudadano, name='subir_archivos_ciudadano'),
    path('archivos/<int:archivo_id>/eliminar/', views_contactos_simple.eliminar_archivo, name='eliminar_archivo'),
    
    # API Alertas
    path('ciudadanos/<int:ciudadano_id>/alertas/', views_contactos_simple.alertas_ciudadano_api, name='alertas_ciudadano'),
    path('alertas/<int:alerta_id>/cerrar/', views_contactos_simple.cerrar_alerta_api, name='cerrar_alerta'),
    
    # API Cursos y Actividades
    path('ciudadanos/<int:pk>/cursos-actividades/', views_cursos.cursos_actividades_ciudadano, name='cursos_actividades_ciudadano'),
    
    # API Línea Temporal
    path('ciudadanos/<int:ciudadano_id>/timeline/', views_contactos_simple.timeline_ciudadano_api, name='timeline_ciudadano'),
    
    # API Predicción de Riesgo
    path('ciudadanos/<int:ciudadano_id>/prediccion-riesgo/', views_contactos_simple.prediccion_riesgo_api, name='prediccion_riesgo'),
    
    # API Evolución de Legajo
    path('<uuid:legajo_id>/evolucion/', views_contactos_simple.evolucion_legajo_api, name='evolucion_legajo'),
    
    # Dashboard de Alertas
    path('alertas/', views_alertas.alertas_dashboard, name='alertas_dashboard'),
    path('alertas/<int:alerta_id>/cerrar-ajax/', views_alertas.cerrar_alerta_ajax, name='cerrar_alerta_ajax'),
    path('alertas/count/', views_alertas.alertas_count_ajax, name='alertas_count_ajax'),
    path('alertas/preview/', views_alertas.alertas_preview_ajax, name='alertas_preview_ajax'),
    path('alertas/debug/', views_alertas.debug_alertas, name='debug_alertas'),
    path('alertas/test/', views_alertas.test_alertas_page, name='test_alertas'),
    
    # Instituciones
    path('instituciones/', views.InstitucionListView.as_view(), name='instituciones'),
    path('instituciones/crear/', views.InstitucionCreateView.as_view(), name='institucion_crear'),
    path('instituciones/<int:pk>/editar/', views.InstitucionUpdateView.as_view(), name='institucion_editar'),
    path('instituciones/<int:pk>/eliminar/', views.InstitucionDeleteView.as_view(), name='institucion_eliminar'),
    
    # Legajos Institucionales
    path('legajos-institucionales/', views.LegajoInstitucionalListView.as_view(), name='legajos_institucionales'),
    path('legajos-institucionales/crear/', views.LegajoInstitucionalCreateView.as_view(), name='legajo_institucional_crear'),
    path('legajos-institucionales/<int:pk>/', views.LegajoInstitucionalDetailView.as_view(), name='legajo_institucional_detalle'),
    path('legajos-institucionales/<int:pk>/editar/', views.LegajoInstitucionalUpdateView.as_view(), name='legajo_institucional_editar'),
]