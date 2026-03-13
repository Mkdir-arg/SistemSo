from django.test import SimpleTestCase

from legajos.views import (
    alertas_dashboard as alertas_dashboard_pkg,
    crear_legajo_acompanamiento as crear_legajo_acompanamiento_pkg,
    cursos_actividades_ciudadano as cursos_actividades_ciudadano_pkg,
    derivaciones_programa_api as derivaciones_programa_api_pkg,
    derivar_programa_view as derivar_programa_view_pkg,
)
from legajos.views_acompanamiento import crear_legajo_acompanamiento
from legajos.views_alertas import alertas_dashboard
from legajos.views_api_derivaciones import derivaciones_programa_api
from legajos.views_cursos import cursos_actividades_ciudadano
from legajos.views_derivacion import derivar_programa_view


class LegajosSupportViewsPackageTests(SimpleTestCase):
    def test_package_expone_views_de_soporte(self):
        self.assertIs(alertas_dashboard_pkg, alertas_dashboard)
        self.assertIs(crear_legajo_acompanamiento_pkg, crear_legajo_acompanamiento)
        self.assertIs(cursos_actividades_ciudadano_pkg, cursos_actividades_ciudadano)
        self.assertIs(derivaciones_programa_api_pkg, derivaciones_programa_api)
        self.assertIs(derivar_programa_view_pkg, derivar_programa_view)
