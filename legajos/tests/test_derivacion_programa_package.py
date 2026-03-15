from django.test import SimpleTestCase

from legajos.views import (
    aceptar_derivacion_programa as aceptar_derivacion_programa_pkg,
    rechazar_derivacion_programa as rechazar_derivacion_programa_pkg,
)
from legajos.views_derivacion_programa import (
    aceptar_derivacion_programa,
    rechazar_derivacion_programa,
)


class LegajosDerivacionProgramaPackageTests(SimpleTestCase):
    def test_package_expone_views_de_derivacion_programa(self):
        self.assertIs(aceptar_derivacion_programa_pkg, aceptar_derivacion_programa)
        self.assertIs(rechazar_derivacion_programa_pkg, rechazar_derivacion_programa)
