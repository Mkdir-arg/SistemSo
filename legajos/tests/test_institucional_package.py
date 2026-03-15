from django.test import SimpleTestCase

from legajos.views import (
    api_programa_indicadores as api_programa_indicadores_pkg,
    institucion_detalle_programatico as institucion_detalle_programatico_pkg,
    programa_derivaciones as programa_derivaciones_pkg,
)
from legajos.views_institucional import (
    api_programa_indicadores,
    institucion_detalle_programatico,
    programa_derivaciones,
)


class LegajosInstitucionalPackageTests(SimpleTestCase):
    def test_package_expone_views_institucionales(self):
        self.assertIs(institucion_detalle_programatico_pkg, institucion_detalle_programatico)
        self.assertIs(programa_derivaciones_pkg, programa_derivaciones)
        self.assertIs(api_programa_indicadores_pkg, api_programa_indicadores)
