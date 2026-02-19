from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (
    inicio_view,
    relevamiento_detail_view,
    relevamientos_view,
    load_localidad,
    load_municipios,
)
from .performance_dashboard import (
    performance_dashboard,
    performance_api,
    query_analysis_api,
    optimization_suggestions_api,
    system_metrics_api,
    alerts_api,
    realtime_metrics_api,
    phase2_metrics_api,
    run_phase2_tests_api,
)

urlpatterns = [
    path("inicio/", login_required(inicio_view), name="inicio"),
    path("relevamientos/", login_required(relevamientos_view), name="relevamientos"),
    path("relevamientos/<uuid:relevamiento_id>/", login_required(relevamiento_detail_view), name="relevamiento_detail"),
    path(
        "ajax/load-municipios/",
        login_required(load_municipios),
        name="ajax_load_municipios",
    ),
    path(
        "ajax/load-localidades/",
        login_required(load_localidad),
        name="ajax_load_localidades",
    ),
    # Performance Dashboard URLs
    path("performance-dashboard/", performance_dashboard, name="performance_dashboard"),
    path("performance-api/", performance_api, name="performance_api"),
    path("query-analysis-api/", query_analysis_api, name="query_analysis_api"),
    path("optimization-suggestions-api/", optimization_suggestions_api, name="optimization_suggestions_api"),
    # Monitoring APIs
    path("system-metrics-api/", system_metrics_api, name="system_metrics_api"),
    path("alerts-api/", alerts_api, name="alerts_api"),
    path("realtime-metrics-api/", realtime_metrics_api, name="realtime_metrics_api"),
    path("phase2-metrics-api/", phase2_metrics_api, name="phase2_metrics_api"),
    path("run-phase2-tests-api/", run_phase2_tests_api, name="run_phase2_tests_api"),
]
