from django.urls import path

from flujos import views

urlpatterns = [
    path('programas/<int:programa_id>/flujo/editar/', views.editor_flujo, name='editor_flujo'),
]
