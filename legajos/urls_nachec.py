"""
URLs para Programa Ñachec
"""
from django.urls import path
from . import views_nachec

app_name = 'nachec'

urlpatterns = [
    # ========================================================================
    # OPERADOR - Derivaciones entrantes
    # ========================================================================
    path('derivaciones/', views_nachec.bandeja_derivaciones, name='bandeja_derivaciones'),
    path('derivaciones/<int:caso_id>/', views_nachec.detalle_derivacion, name='detalle_derivacion'),
    path('derivaciones/<int:caso_id>/tomar/', views_nachec.tomar_caso, name='tomar_caso'),
    path('derivaciones/<int:caso_id>/rechazar/', views_nachec.rechazar_caso, name='rechazar_caso'),
    path('derivaciones/<int:caso_id>/enviar-asignacion/', views_nachec.enviar_a_asignacion, name='enviar_asignacion'),
    
    # ========================================================================
    # COORDINADOR - Asignación
    # ========================================================================
    path('asignacion/', views_nachec.bandeja_asignacion, name='bandeja_asignacion'),
    path('asignacion/<int:caso_id>/asignar/', views_nachec.asignar_territorial, name='asignar_territorial'),
    
    # ========================================================================
    # TERRITORIAL - Mis casos
    # ========================================================================
    path('mis-casos/', views_nachec.mis_casos, name='mis_casos'),
    path('casos/<int:caso_id>/iniciar-relevamiento/', views_nachec.iniciar_relevamiento, name='iniciar_relevamiento'),
    path('casos/<int:caso_id>/relevamiento/', views_nachec.formulario_relevamiento, name='formulario_relevamiento'),
    
    # ========================================================================
    # EVALUADOR - Evaluación
    # ========================================================================
    path('evaluacion/', views_nachec.bandeja_evaluacion, name='bandeja_evaluacion'),
    path('evaluacion/<int:caso_id>/', views_nachec.formulario_evaluacion, name='formulario_evaluacion'),
    
    # ========================================================================
    # REFERENTE - Planes
    # ========================================================================
    path('planes/', views_nachec.bandeja_planes, name='bandeja_planes'),
    
    # ========================================================================
    # API
    # ========================================================================
    path('api/caso/<int:caso_id>/', views_nachec.api_caso_detalle, name='api_caso_detalle'),
]
