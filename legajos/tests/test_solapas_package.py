from django.test import SimpleTestCase

from legajos.views import (
    CiudadanoDetalleConSolapasView as CiudadanoDetalleConSolapasViewPkg,
    ciudadano_detalle_con_solapas as ciudadano_detalle_con_solapas_pkg,
    derivar_a_programa as derivar_a_programa_pkg,
)
from legajos.views_solapas import (
    CiudadanoDetalleConSolapasView,
    ciudadano_detalle_con_solapas,
    derivar_a_programa,
)


class LegajosSolapasPackageTests(SimpleTestCase):
    def test_package_expone_views_de_solapas(self):
        self.assertIs(CiudadanoDetalleConSolapasViewPkg, CiudadanoDetalleConSolapasView)
        self.assertIs(ciudadano_detalle_con_solapas_pkg, ciudadano_detalle_con_solapas)
        self.assertIs(derivar_a_programa_pkg, derivar_a_programa)
