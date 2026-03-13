"""Fachada compatible para formularios de legajos."""

from .forms_ciudadanos import (
    AdmisionLegajoForm,
    BuscarCiudadanoForm,
    CiudadanoConfirmarForm,
    CiudadanoForm,
    CiudadanoManualForm,
    CiudadanoUpdateForm,
    ConsentimientoForm,
    ConsultaRenaperForm,
)
from .forms_clinico import (
    DerivacionForm,
    EvaluacionInicialForm,
    EventoCriticoForm,
    LegajoCerrarForm,
    LegajoReabrirForm,
    PlanIntervencionForm,
    SeguimientoForm,
)
from .forms_operativa import InscribirActividadForm
