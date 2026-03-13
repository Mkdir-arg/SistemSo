"""Paquete de vistas para la app de configuracion."""

from .actividades import (
    ActividadDetailView,
    ActividadEditarView,
    DerivacionAceptarView,
    DerivacionRechazarView,
    InscriptoEditarView,
    StaffActividadCreateView,
    buscar_personal_ajax,
)
from .extra import (
    AsistenciaView,
    StaffDesasignarView,
    StaffEditarView,
    TomarAsistenciaView,
)
from .geografia import (
    LocalidadCreateView,
    LocalidadDeleteView,
    LocalidadListView,
    LocalidadUpdateView,
    MunicipioCreateView,
    MunicipioDeleteView,
    MunicipioListView,
    MunicipioUpdateView,
    ProvinciaCreateView,
    ProvinciaDeleteView,
    ProvinciaListView,
    ProvinciaUpdateView,
)
from .institucional import (
    DispositivoCreateView,
    DispositivoForm,
    DispositivoListView,
    DispositivoRed,
    DispositivoUpdateView,
    EvaluacionInstitucionCreateView,
    IndicadorInstitucionCreateView,
    InstitucionCreateView,
    InstitucionDeleteView,
    InstitucionDetailView,
    InstitucionListView,
    InstitucionUpdateView,
    PersonalInstitucionCreateView,
    PlanFortalecimientoCreateView,
    documento_subir,
)
