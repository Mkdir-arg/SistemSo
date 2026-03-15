from django.test import SimpleTestCase

from legajos import forms
from legajos.forms import HistorialContactoForm
from legajos.forms_ciudadanos import (
    AdmisionLegajoForm,
    BuscarCiudadanoForm,
    CiudadanoConfirmarForm,
    CiudadanoManualForm,
    CiudadanoUpdateForm,
    ConsentimientoForm,
    ConsultaRenaperForm,
)
from legajos.forms_clinico import (
    DerivacionForm,
    EvaluacionInicialForm,
    EventoCriticoForm,
    LegajoCerrarForm,
    LegajoReabrirForm,
    PlanIntervencionForm,
    SeguimientoForm,
)
from legajos.forms_operativa import InscribirActividadForm


class LegajosFormsFachadaTests(SimpleTestCase):
    def test_package_expone_forms_publicos(self):
        self.assertIs(forms.ConsultaRenaperForm, ConsultaRenaperForm)
        self.assertIs(forms.HistorialContactoForm, HistorialContactoForm)

    def test_expone_forms_de_ciudadanos(self):
        self.assertIs(forms.ConsultaRenaperForm, ConsultaRenaperForm)
        self.assertIs(forms.CiudadanoManualForm, CiudadanoManualForm)
        self.assertIs(forms.CiudadanoConfirmarForm, CiudadanoConfirmarForm)
        self.assertIs(forms.CiudadanoUpdateForm, CiudadanoUpdateForm)
        self.assertIs(forms.BuscarCiudadanoForm, BuscarCiudadanoForm)
        self.assertIs(forms.AdmisionLegajoForm, AdmisionLegajoForm)
        self.assertIs(forms.ConsentimientoForm, ConsentimientoForm)

    def test_expone_forms_clinicos(self):
        self.assertIs(forms.EvaluacionInicialForm, EvaluacionInicialForm)
        self.assertIs(forms.PlanIntervencionForm, PlanIntervencionForm)
        self.assertIs(forms.SeguimientoForm, SeguimientoForm)
        self.assertIs(forms.DerivacionForm, DerivacionForm)
        self.assertIs(forms.EventoCriticoForm, EventoCriticoForm)
        self.assertIs(forms.LegajoCerrarForm, LegajoCerrarForm)
        self.assertIs(forms.LegajoReabrirForm, LegajoReabrirForm)

    def test_expone_forms_operativos(self):
        self.assertIs(forms.InscribirActividadForm, InscribirActividadForm)
