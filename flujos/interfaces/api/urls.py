from django.urls import path

from flujos.interfaces.web import views

app_name = 'flujos'

urlpatterns = [
    path('flujos/<int:programa_id>/definicion/', views.api_definicion, name='api_definicion'),
    path('flujos/<int:programa_id>/publicar/', views.api_publicar, name='api_publicar'),
    path('flujos/instancia/<int:instancia_id>/', views.api_instancia, name='api_instancia'),
    path('flujos/tareas/', views.api_bandeja_tareas, name='api_bandeja_tareas'),
    path('flujos/tareas/<int:pk>/', views.api_tarea_detalle, name='api_tarea_detalle'),
    path('flujos/tareas/<int:pk>/asignar/', views.api_tarea_asignar, name='api_tarea_asignar'),
    path('flujos/tareas/<int:pk>/resolver/', views.api_tarea_resolver, name='api_tarea_resolver'),
]
