"""
URLs para transiciones de estado Ñachec
"""
from django.urls import path
from . import views_nachec

urlpatterns = [
    path('tarea/<int:tarea_id>/completar/', views_nachec.completar_tarea, name='nachec_completar_tarea'),
    path('caso/<int:caso_id>/tarea-validacion/', views_nachec.ver_tarea_validacion, name='nachec_ver_tarea_validacion'),
    path('caso/<int:caso_id>/completar-validacion/', views_nachec.completar_validacion, name='nachec_completar_validacion'),
    path('caso/<int:caso_id>/enviar-asignacion/', views_nachec.enviar_a_asignacion, name='nachec_enviar_asignacion'),
    path('caso/<int:caso_id>/asignar-territorial/', views_nachec.asignar_territorial, name='nachec_asignar_territorial'),
    path('caso/<int:caso_id>/iniciar-relevamiento/', views_nachec.iniciar_relevamiento, name='nachec_iniciar_relevamiento'),
    path('caso/<int:caso_id>/relevamiento/', views_nachec.formulario_relevamiento, name='nachec_formulario_relevamiento'),
    path('caso/<int:caso_id>/finalizar-relevamiento/', views_nachec.finalizar_relevamiento, name='nachec_finalizar_relevamiento'),
    path('caso/<int:caso_id>/evaluar/', views_nachec.evaluar_caso, name='nachec_evaluar_caso'),
    path('caso/<int:caso_id>/activar-plan/', views_nachec.activar_plan, name='nachec_activar_plan'),
    path('caso/<int:caso_id>/pasar-seguimiento/', views_nachec.pasar_a_seguimiento, name='nachec_pasar_seguimiento'),
    path('caso/<int:caso_id>/cerrar/', views_nachec.cerrar_caso, name='nachec_cerrar_caso'),
    # PASO 8 - Gestión de prestaciones
    path('prestacion/<int:prestacion_id>/iniciar/', views_nachec.iniciar_prestacion, name='nachec_iniciar_prestacion'),
    path('prestacion/<int:prestacion_id>/confirmar-entrega/', views_nachec.confirmar_entrega_prestacion, name='nachec_confirmar_entrega'),
    path('prestacion/<int:prestacion_id>/reprogramar/', views_nachec.reprogramar_prestacion, name='nachec_reprogramar_prestacion'),
    path('prestacion/<int:prestacion_id>/cancelar/', views_nachec.cancelar_prestacion, name='nachec_cancelar_prestacion'),
    # PASO 9 - Cierre de caso
    path('caso/<int:caso_id>/cerrar-caso/', views_nachec.cerrar_caso_nachec, name='nachec_cerrar_caso'),
    # PASO 10 - Reabrir caso
    path('caso/<int:caso_id>/reabrir-caso/', views_nachec.reabrir_caso_nachec, name='nachec_reabrir_caso'),
]
