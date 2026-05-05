from django.urls import path

from flujos.interfaces.web import views

urlpatterns = [
    path('programas/<int:programa_id>/flujo/editar/', views.editor_flujo, name='editor_flujo'),
    path('tareas/pendientes/', views.bandeja_tareas, name='bandeja_tareas'),
    path('tareas/<int:pk>/', views.tarea_detalle, name='tarea_detalle'),
    path('tareas/<int:pk>/asignar/', views.tarea_asignar, name='tarea_asignar'),
    path('tareas/<int:pk>/resolver/', views.tarea_resolver, name='tarea_resolver'),
]
