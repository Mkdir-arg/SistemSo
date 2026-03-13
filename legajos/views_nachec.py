"""Fachada compatible para vistas de Ñachec."""

from .views_nachec_cierre import cerrar_caso_nachec, reabrir_caso_nachec
from .views_nachec_dashboard import dashboard_nachec
from .views_nachec_decisiones import (
    activar_plan,
    cerrar_caso,
    evaluar_caso,
    pasar_a_seguimiento,
)
from .views_nachec_operacion import (
    adjuntar_evidencias,
    asignar_territorial,
    completar_tarea,
    completar_validacion,
    enviar_a_asignacion,
    finalizar_relevamiento,
    formulario_relevamiento,
    iniciar_relevamiento,
    reasignar_territorial,
    ver_tarea_validacion,
)
from .views_nachec_prestaciones import (
    cancelar_prestacion,
    confirmar_entrega_prestacion,
    iniciar_prestacion,
    reprogramar_prestacion,
)
