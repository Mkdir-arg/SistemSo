"""Servicios para la app de legajos."""

from .admision import AdmisionSessionService  # noqa: F401
from .ciudadanos import CiudadanosService, RenaperLookupError  # noqa: F401
from .contactos import (  # noqa: F401
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    ContactosFilesError,
    eliminar_archivo_por_id,
    subir_archivos_para_objeto,
)
from .derivaciones_programa import DerivacionProgramaResult, DerivacionProgramaService  # noqa: F401
from .legajos import LegajoWorkflowService  # noqa: F401
from .solapas import SolapasService  # noqa: F401
