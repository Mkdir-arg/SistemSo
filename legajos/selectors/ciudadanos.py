from datetime import date

from django.db.models import Q

from ..models import Ciudadano, EventoCritico, LegajoAtencion, SeguimientoContacto
from ..models_nachec import (
    CasoNachec,
    EvaluacionVulnerabilidad,
    HistorialEstadoCaso,
    PlanIntervencionNachec,
    PrestacionNachec,
    RelevamientoNachec,
)
from ..services import SolapasService


def get_ciudadanos_queryset(search=""):
    queryset = Ciudadano.objects.filter(activo=True)
    if search:
        queryset = queryset.filter(
            Q(dni__icontains=search)
            | Q(nombre__icontains=search)
            | Q(apellido__icontains=search)
        )
    return queryset.order_by("apellido", "nombre")


def get_ciudadanos_dashboard_metrics():
    total_seguimientos = SeguimientoContacto.objects.count()
    seguimientos_adecuados = SeguimientoContacto.objects.filter(
        adherencia="ADECUADA"
    ).count()
    tasa_adherencia = round(
        (seguimientos_adecuados / total_seguimientos * 100)
        if total_seguimientos > 0
        else 0
    )

    return {
        "total_ciudadanos": Ciudadano.objects.filter(activo=True).count(),
        "legajos_activos": LegajoAtencion.objects.filter(
            estado__in=["ABIERTO", "EN_SEGUIMIENTO"]
        ).count(),
        "alertas_criticas": EventoCritico.objects.count(),
        "seguimientos_hoy": SeguimientoContacto.objects.filter(
            creado__date=date.today()
        ).count(),
        "tasa_adherencia": tasa_adherencia,
        "casos_alto_riesgo": LegajoAtencion.objects.filter(
            nivel_riesgo="ALTO"
        ).count(),
    }


def build_ciudadano_detail_context(ciudadano):
    context = {
        "legajos": ciudadano.legajos.select_related(
            "dispositivo",
            "responsable",
        ).order_by("-fecha_apertura"),
        "solapas": SolapasService.obtener_solapas_ciudadano(ciudadano),
        "programas_activos": SolapasService.obtener_programas_activos(ciudadano),
    }

    caso_nachec = (
        CasoNachec.objects.filter(ciudadano_titular=ciudadano)
        .exclude(estado__in=["CERRADO", "RECHAZADO", "SUSPENDIDO"])
        .select_related("territorial", "coordinador", "operador_admision")
        .order_by("-creado")
        .first()
    )
    if not caso_nachec:
        return context

    context["caso_nachec"] = caso_nachec
    context["relevamiento"] = RelevamientoNachec.objects.filter(
        caso=caso_nachec
    ).order_by("-creado").first()
    context["evaluacion"] = EvaluacionVulnerabilidad.objects.filter(
        caso=caso_nachec
    ).first()
    context["plan_vigente"] = PlanIntervencionNachec.objects.filter(
        caso=caso_nachec,
        vigente=True,
    ).first()
    context["prestaciones"] = PrestacionNachec.objects.filter(
        caso=caso_nachec
    ).select_related("responsable").order_by("-creado")[:10]
    context["historial_estados"] = HistorialEstadoCaso.objects.filter(
        caso=caso_nachec
    ).select_related("usuario").order_by("-timestamp")[:10]
    return context
