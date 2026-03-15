from django.test import SimpleTestCase

from legajos.views import (
    LegajoDetailView as LegajoDetailViewPkg,
    LegajoListView as LegajoListViewPkg,
    ReportesView as ReportesViewPkg,
)
from legajos.views_clinico import LegajoDetailView, LegajoListView, ReportesView


class LegajosClinicoPackageTests(SimpleTestCase):
    def test_package_expone_views_clinicas(self):
        self.assertIs(LegajoListViewPkg, LegajoListView)
        self.assertIs(LegajoDetailViewPkg, LegajoDetailView)
        self.assertIs(ReportesViewPkg, ReportesView)
