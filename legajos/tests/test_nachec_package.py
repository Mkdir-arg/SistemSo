from django.test import SimpleTestCase

from legajos.views import (
    completar_validacion as completar_validacion_pkg,
    dashboard_nachec as dashboard_nachec_pkg,
    iniciar_prestacion as iniciar_prestacion_pkg,
)
from legajos.views_nachec_dashboard import dashboard_nachec
from legajos.views_nachec_operacion import completar_validacion
from legajos.views_nachec_prestaciones import iniciar_prestacion


class LegajosNachecPackageTests(SimpleTestCase):
    def test_package_expone_views_nachec(self):
        self.assertIs(dashboard_nachec_pkg, dashboard_nachec)
        self.assertIs(completar_validacion_pkg, completar_validacion)
        self.assertIs(iniciar_prestacion_pkg, iniciar_prestacion)
