"""Forms para la app de configuracion."""

from .institucional import *  # noqa: F401,F403
from .reclamos import (  # noqa: F401
    AreaConfigForm,
    CampoDinamicoOpcionConfigForm,
    CampoDinamicoReclamoConfigForm,
    EstadoReclamoConfigForm,
    EstadoReclamoTransicionConfigForm,
    PrioridadReclamoConfigForm,
    ReclamoCambioEstadoForm,
    ReclamoConfigForm,
    ReclamoDerivacionForm,
    ReclamoSeguimientoForm,
    TipoReclamoConfigForm,
)
from .tramites import (  # noqa: F401
    AreaTramiteConfigForm,
    CampoDinamicoOpcionConfigForm,
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
)
