from django.test import SimpleTestCase

from legajos.interfaces.web.views import ProgramaDetailView, ProgramaListView
from legajos.interfaces.web.views.programas import (
    ProgramaDetailView as ProgramaDetailViewModule,
    ProgramaListView as ProgramaListViewModule,
)


class LegajosProgramasPackageTests(SimpleTestCase):
    def test_package_expone_views_de_programas(self):
        self.assertIs(ProgramaListView, ProgramaListViewModule)
        self.assertIs(ProgramaDetailView, ProgramaDetailViewModule)
