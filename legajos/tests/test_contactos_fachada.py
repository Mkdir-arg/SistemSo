from django.test import SimpleTestCase

from legajos import views_simple_contactos
from legajos.views_contactos_api import (
    actividades_ciudadano_api,
    alertas_ciudadano_api,
    archivos_ciudadano_api,
    archivos_legajo_api,
    cerrar_alerta_api,
    eliminar_archivo,
    evolucion_legajo_api,
    prediccion_riesgo_api,
    subir_archivos_ciudadano,
    subir_archivos_legajo,
    timeline_ciudadano_api,
)
from legajos.views_contactos_panel import (
    dashboard_contactos_simple,
    historial_contactos_simple,
    red_contactos_simple,
)


class ContactosFachadaTests(SimpleTestCase):
    def test_expone_views_de_panel(self):
        self.assertIs(views_simple_contactos.red_contactos_simple, red_contactos_simple)
        self.assertIs(
            views_simple_contactos.dashboard_contactos_simple,
            dashboard_contactos_simple,
        )
        self.assertIs(
            views_simple_contactos.historial_contactos_simple,
            historial_contactos_simple,
        )

    def test_expone_views_api(self):
        self.assertIs(views_simple_contactos.actividades_ciudadano_api, actividades_ciudadano_api)
        self.assertIs(views_simple_contactos.subir_archivos_ciudadano, subir_archivos_ciudadano)
        self.assertIs(views_simple_contactos.subir_archivos_legajo, subir_archivos_legajo)
        self.assertIs(views_simple_contactos.archivos_ciudadano_api, archivos_ciudadano_api)
        self.assertIs(views_simple_contactos.eliminar_archivo, eliminar_archivo)
        self.assertIs(views_simple_contactos.alertas_ciudadano_api, alertas_ciudadano_api)
        self.assertIs(views_simple_contactos.cerrar_alerta_api, cerrar_alerta_api)
        self.assertIs(views_simple_contactos.prediccion_riesgo_api, prediccion_riesgo_api)
        self.assertIs(views_simple_contactos.evolucion_legajo_api, evolucion_legajo_api)
        self.assertIs(views_simple_contactos.timeline_ciudadano_api, timeline_ciudadano_api)
        self.assertIs(views_simple_contactos.archivos_legajo_api, archivos_legajo_api)
