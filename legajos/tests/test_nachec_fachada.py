from django.test import SimpleTestCase

from legajos import views_nachec
from legajos.views_nachec_cierre import cerrar_caso_nachec, reabrir_caso_nachec
from legajos.views_nachec_dashboard import dashboard_nachec
from legajos.views_nachec_decisiones import (
    activar_plan,
    cerrar_caso,
    evaluar_caso,
    pasar_a_seguimiento,
)
from legajos.views_nachec_operacion import (
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
from legajos.views_nachec_prestaciones import (
    cancelar_prestacion,
    confirmar_entrega_prestacion,
    iniciar_prestacion,
    reprogramar_prestacion,
)


class NachecFachadaTests(SimpleTestCase):
    def test_views_nachec_expone_prestaciones_desde_modulo_dedicado(self):
        self.assertIs(views_nachec.iniciar_prestacion, iniciar_prestacion)
        self.assertIs(views_nachec.confirmar_entrega_prestacion, confirmar_entrega_prestacion)
        self.assertIs(views_nachec.reprogramar_prestacion, reprogramar_prestacion)
        self.assertIs(views_nachec.cancelar_prestacion, cancelar_prestacion)

    def test_views_nachec_expone_cierre_y_dashboard_desde_modulos_dedicados(self):
        self.assertIs(views_nachec.cerrar_caso_nachec, cerrar_caso_nachec)
        self.assertIs(views_nachec.reabrir_caso_nachec, reabrir_caso_nachec)
        self.assertIs(views_nachec.dashboard_nachec, dashboard_nachec)

    def test_views_nachec_expone_evaluacion_y_plan_desde_modulo_dedicado(self):
        self.assertIs(views_nachec.evaluar_caso, evaluar_caso)
        self.assertIs(views_nachec.activar_plan, activar_plan)
        self.assertIs(views_nachec.pasar_a_seguimiento, pasar_a_seguimiento)
        self.assertIs(views_nachec.cerrar_caso, cerrar_caso)

    def test_views_nachec_expone_operacion_desde_modulo_dedicado(self):
        self.assertIs(views_nachec.completar_validacion, completar_validacion)
        self.assertIs(views_nachec.ver_tarea_validacion, ver_tarea_validacion)
        self.assertIs(views_nachec.completar_tarea, completar_tarea)
        self.assertIs(views_nachec.enviar_a_asignacion, enviar_a_asignacion)
        self.assertIs(views_nachec.asignar_territorial, asignar_territorial)
        self.assertIs(views_nachec.reasignar_territorial, reasignar_territorial)
        self.assertIs(views_nachec.iniciar_relevamiento, iniciar_relevamiento)
        self.assertIs(views_nachec.finalizar_relevamiento, finalizar_relevamiento)
        self.assertIs(views_nachec.formulario_relevamiento, formulario_relevamiento)
        self.assertIs(views_nachec.adjuntar_evidencias, adjuntar_evidencias)
