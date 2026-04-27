from django.test import SimpleTestCase

from legajos.interfaces.web.views import (
    alertas_dashboard,
    crear_legajo_acompanamiento,
    cursos_actividades_ciudadano,
    derivaciones_programa_api,
    derivar_programa_view,
)
from legajos.interfaces.web.views.acompanamiento import crear_legajo_acompanamiento as crear_legajo_acompanamiento_module
from legajos.interfaces.web.views.alertas import alertas_dashboard as alertas_dashboard_module
from legajos.interfaces.web.views.api_derivaciones import derivaciones_programa_api as derivaciones_programa_api_module
from legajos.interfaces.web.views.cursos import cursos_actividades_ciudadano as cursos_actividades_ciudadano_module
from legajos.interfaces.web.views.derivacion import derivar_programa_view as derivar_programa_view_module


class LegajosSupportViewsPackageTests(SimpleTestCase):
    def test_package_expone_views_de_soporte(self):
        self.assertIs(alertas_dashboard, alertas_dashboard_module)
        self.assertIs(crear_legajo_acompanamiento, crear_legajo_acompanamiento_module)
        self.assertIs(cursos_actividades_ciudadano, cursos_actividades_ciudadano_module)
        self.assertIs(derivaciones_programa_api, derivaciones_programa_api_module)
        self.assertIs(derivar_programa_view, derivar_programa_view_module)
