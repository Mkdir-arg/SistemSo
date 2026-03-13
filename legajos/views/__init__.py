"""Views agrupadas de la app de legajos."""

from .acompanamiento import crear_legajo_acompanamiento  # noqa: F401
from .alertas import (  # noqa: F401
    alertas_count_ajax,
    alertas_dashboard,
    alertas_preview_ajax,
    cerrar_alerta_ajax,
    debug_alertas,
    test_alertas_page,
)
from .api_derivaciones import derivaciones_programa_api  # noqa: F401
from .contactos_api import (  # noqa: F401
    actividades_ciudadano_api,
    alertas_ciudadano_api,
    archivos_ciudadano_api,
    archivos_legajo_api,
    cerrar_alerta_api,
    eliminar_archivo,
    evolucion_legajo_api,
    prediccion_riesgo_api,
    subir_archivos_ciudadano,
    subir_archivos_legajo,
    timeline_ciudadano_api,
)
from .contactos_panel import (  # noqa: F401
    dashboard_contactos_simple,
    historial_contactos_simple,
    red_contactos_simple,
)
from .cursos import cursos_actividades_ciudadano  # noqa: F401
from .dashboard_contactos import (  # noqa: F401
    dashboard_contactos,
    exportar_reporte_contactos,
    metricas_contactos_api,
    metricas_red_contactos_api,
)
from .dashboard_simple import dashboard_contactos_simple as dashboard_contactos_simple_debug  # noqa: F401
from .dashboard_simple import test_api  # noqa: F401
from .derivacion import derivar_programa_view  # noqa: F401
from .derivacion_programa import (  # noqa: F401
    aceptar_derivacion_programa,
    rechazar_derivacion_programa,
)
from .historial_contactos import (  # noqa: F401
    contactos_api,
    crear_contacto,
    detalle_contacto,
    editar_contacto,
    eliminar_contacto,
    historial_contactos_view,
)
from .institucional import (  # noqa: F401
    aceptar_derivacion,
    api_programa_indicadores,
    cambiar_estado_caso_view,
    caso_detalle,
    institucion_detalle_programatico,
    programa_casos,
    programa_derivaciones,
    rechazar_derivacion_view,
)
from .operativa import (  # noqa: F401
    ActividadesInscritoListView,
    InscribirActividadView,
    InstitucionCreateView,
    InstitucionDeleteView,
    InstitucionListView,
    InstitucionUpdateView,
    LegajoInstitucionalCreateView,
    LegajoInstitucionalDetailView,
    LegajoInstitucionalListView,
    LegajoInstitucionalUpdateView,
    actividades_por_institucion,
    marcar_etapa_plan,
)
from .programas import ProgramaDetailView, ProgramaListView  # noqa: F401
from .red_contactos import (  # noqa: F401
    contacto_emergencia_api,
    crear_contacto_emergencia,
    crear_dispositivo,
    crear_profesional,
    crear_vinculo,
    dispositivos_api,
    eliminar_contacto_emergencia,
    eliminar_dispositivo,
    eliminar_profesional,
    eliminar_vinculo,
    profesionales_api,
    red_contactos_view,
    vinculos_api,
)
from .solapas import (  # noqa: F401
    CiudadanoDetalleConSolapasView,
    aceptar_derivacion_programa,
    cerrar_inscripcion_programa,
    ciudadano_detalle_con_solapas,
    derivar_a_programa,
    inscribir_a_programa,
    rechazar_derivacion_programa,
)
