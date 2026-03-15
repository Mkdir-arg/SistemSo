from django.test import SimpleTestCase

from legajos.views import ProgramaDetailView as ProgramaDetailViewPkg
from legajos.views import ProgramaListView as ProgramaListViewPkg
from legajos.views_programas import ProgramaDetailView, ProgramaListView


class LegajosProgramasPackageTests(SimpleTestCase):
    def test_package_expone_views_de_programas(self):
        self.assertIs(ProgramaListViewPkg, ProgramaListView)
        self.assertIs(ProgramaDetailViewPkg, ProgramaDetailView)
