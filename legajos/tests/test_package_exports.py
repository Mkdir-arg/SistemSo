from django.test import SimpleTestCase


class LegajosPackageExportsTests(SimpleTestCase):
    def test_services_and_selectors_packages_export_public_symbols(self):
        from legajos.selectors import (
            build_ciudadano_detail_context,
            get_legajos_report_stats,
        )
        from legajos.services import (
            AdmisionSessionService,
            CiudadanosService,
            ContactosFilesError,
            LegajoWorkflowService,
            SolapasService,
        )

        self.assertIsNotNone(AdmisionSessionService)
        self.assertIsNotNone(CiudadanosService)
        self.assertIsNotNone(LegajoWorkflowService)
        self.assertIsNotNone(SolapasService)
        self.assertIsNotNone(ContactosFilesError)
        self.assertTrue(callable(build_ciudadano_detail_context))
        self.assertTrue(callable(get_legajos_report_stats))
