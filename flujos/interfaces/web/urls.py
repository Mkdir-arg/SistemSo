from django.urls import path

from flujos.interfaces.web import views

urlpatterns = [
    path('programas/<int:programa_id>/flujo/editar/', views.editor_flujo, name='editor_flujo'),
    path('tareas/pendientes/', views.bandeja_tareas, name='bandeja_tareas'),
    path('tareas/<int:pk>/', views.tarea_detalle, name='tarea_detalle'),
    path('tareas/<int:pk>/asignar/', views.tarea_asignar, name='tarea_asignar'),
    path('tareas/<int:pk>/resolver/', views.tarea_resolver, name='tarea_resolver'),
    path('programas/<int:programa_id>/roles/', views.roles_programa_list, name='roles_programa_list'),
    path('programas/<int:programa_id>/roles/crear/', views.rol_programa_crear, name='rol_programa_crear'),
    path('roles/<int:pk>/eliminar/', views.rol_programa_eliminar, name='rol_programa_eliminar'),
    path('roles/<int:pk>/asignar/', views.rol_programa_asignar, name='rol_programa_asignar'),
    path('asignaciones-rol/<int:pk>/eliminar/', views.rol_programa_desasignar, name='rol_programa_desasignar'),
]
