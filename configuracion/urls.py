from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

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
    
    # Gestión de legajo institucional
    path('instituciones/<int:institucion_pk>/personal/crear/', login_required(views.PersonalInstitucionCreateView.as_view()), name='personal_crear'),
    path('instituciones/<int:institucion_pk>/evaluaciones/crear/', login_required(views.EvaluacionInstitucionCreateView.as_view()), name='evaluacion_crear'),
    path('instituciones/<int:institucion_pk>/planes/crear/', login_required(views.PlanFortalecimientoCreateView.as_view()), name='plan_crear'),
    path('instituciones/<int:institucion_pk>/indicadores/crear/', login_required(views.IndicadorInstitucionCreateView.as_view()), name='indicador_crear'),
    path('instituciones/<int:pk>/documentos/subir/', login_required(views.documento_subir), name='documento_subir'),
    

    
    # Dispositivos (compatibilidad)
    path('dispositivos/', login_required(views.InstitucionListView.as_view()), name='dispositivos'),
    path('dispositivos/crear/', login_required(views.InstitucionCreateView.as_view()), name='dispositivo_crear'),
    path('dispositivos/<int:pk>/editar/', login_required(views.InstitucionUpdateView.as_view()), name='dispositivo_editar'),
    path('dispositivos/<int:pk>/eliminar/', login_required(views.InstitucionDeleteView.as_view()), name='dispositivo_eliminar'),
]