from django.test import SimpleTestCase

from legajos import views_nachec
from legajos.views_nachec_cierre import cerrar_caso_nachec, reabrir_caso_nachec
from legajos.views_nachec_dashboard import dashboard_nachec
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
