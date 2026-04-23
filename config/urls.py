from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from config.branding import get_branding_profile
from system_modules.registry import get_module_registry


def _module_paths(slug, route, include_target):
    if not get_module_registry().has(slug):
        return []
    return [path(route, include_target)]

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url=f"{settings.STATIC_URL}{get_branding_profile()['favicon_path']}", permanent=True),
    ),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    
    # Specific paths first
    path("legajos/", include("legajos.urls")),
    path("configuracion/", include("configuracion.urls")),
    path("portal/", include("portal.urls")),
    path("auditoria/", include("core.urls_auditoria")),
] + _module_paths("chatbot", "chatbot/", include("chatbot.urls")) + _module_paths(
    "conversaciones", "conversaciones/", include("conversaciones.urls")
) + _module_paths("turnos", "turnos/", include("turnos.urls")) + _module_paths(
    "tramites", "tramites/", include("tramites.urls")
) + [
    # Root paths last
    path("", include("django.contrib.auth.urls")),
    path("", include(("users.urls", "users"), namespace="users")),
    path("", include(("core.urls", "core"), namespace="core")),
    path("", include("dashboard.urls")),
    path("", include(("healthcheck.urls", "healthcheck"), namespace="healthcheck")),
    # Flujos - editor visual HTML

    # API Routes
    path("api/legajos/", include("legajos.api_urls")),
    path("api/core/", include("core.api_urls")),
    path("api/users/", include("users.api_urls")),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # Health Check
    path("health/", include('health_check.urls')),
    
    # Performance Profiling (solo en desarrollo/staging)
    path("silk/", include('silk.urls', namespace='silk')),
]

urlpatterns += _module_paths(
    "flujos",
    "flujos/",
    include(("flujos.views_urls", "flujos_editor"), namespace="flujos_editor"),
)
urlpatterns += _module_paths(
    "flujos",
    "api/",
    include(("flujos.urls", "flujos"), namespace="flujos"),
)
urlpatterns += _module_paths("chatbot", "api/chatbot/", include("chatbot.api_urls"))

# URLs de desarrollo se pueden agregar aquí si es necesario

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = "config.views.server_error"
