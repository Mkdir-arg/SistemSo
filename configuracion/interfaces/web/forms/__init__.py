"""Forms para la app de configuracion."""

from .institucional import *  # noqa: F401,F403
from .reclamos import (  # noqa: F401
    AreaConfigForm,
    AreaRaizConfigForm,
    CampoDinamicoOpcionConfigForm,
    CampoDinamicoReclamoInlineConfigForm,
    CampoDinamicoReclamoConfigForm,
    EstadoReclamoConfigForm,
    EstadoReclamoTransicionConfigForm,
    PrioridadReclamoConfigForm,
    ReclamoCambioEstadoForm,
    ReclamoConfigForm,
    ReclamoDerivacionForm,
    ReclamoSolicitudDatoCampoForm,
    ReclamoSeguimientoForm,
    SubareaConfigForm,
    TipoReclamoConfigForm,
)
from .tramites import (  # noqa: F401
    CampoDinamicoOpcionConfigForm,
    CampoDinamicoTramiteInlineConfigForm,
    CampoDinamicoTramiteConfigForm,
    EstadoTramiteConfigForm,
    EstadoTramiteTransicionConfigForm,
    PrioridadTramiteConfigForm,
    RequisitoTramiteConfigForm,
    TipoTramiteConfigForm,
    TramiteCambioEstadoForm,
    TramiteConfigForm,
    TramiteDerivacionForm,
    TramiteSeguimientoForm,
    TramiteSolicitudDatoCampoForm,
)
