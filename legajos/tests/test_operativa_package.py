from django.test import SimpleTestCase

from legajos.views import (
    ActividadesInscritoListView as ActividadesInscritoListViewPkg,
    InscribirActividadView as InscribirActividadViewPkg,
    actividades_por_institucion as actividades_por_institucion_pkg,
    marcar_etapa_plan as marcar_etapa_plan_pkg,
)
from legajos.views_operativa import (
    ActividadesInscritoListView,
    InscribirActividadView,
    actividades_por_institucion,
    marcar_etapa_plan,
)


class LegajosOperativaPackageTests(SimpleTestCase):
    def test_package_expone_views_operativas(self):
        self.assertIs(InscribirActividadViewPkg, InscribirActividadView)
        self.assertIs(ActividadesInscritoListViewPkg, ActividadesInscritoListView)
        self.assertIs(actividades_por_institucion_pkg, actividades_por_institucion)
        self.assertIs(marcar_etapa_plan_pkg, marcar_etapa_plan)
