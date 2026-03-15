"""Selectors para la app de legajos."""

from .ciudadanos import (  # noqa: F401
    build_ciudadano_detail_context,
    get_ciudadanos_dashboard_metrics,
    get_ciudadanos_queryset,
)
from .contactos import (  # noqa: F401
    build_ciudadano_actividades_payload,
    get_legajo_contactos_context,
)
from .legajos import (  # noqa: F401
    get_legajo_detail_queryset,
    get_legajos_queryset,
    get_legajos_report_stats,
    get_seguimientos_dashboard_metrics,
)
