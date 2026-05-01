from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from config.branding import get_branding_profile
from system_modules.registry import get_module_registry


def _route_include(route):
    if route.namespace:
        return include((route.urlconf, route.app_name or route.namespace), namespace=route.namespace)
    return include(route.urlconf)


def _module_web_paths():
    return [
        path(route.route, _route_include(route))
        for _definition, route in get_module_registry().web_routes()
    ]


def _module_api_paths():
    return [
        path(route.route, _route_include(route))
        for _definition, route in get_module_registry().api_routes()
    ]

urlpatterns = [
    path(
        "favicon.ico",
        RedirectView.as_view(url=f"{settings.STATIC_URL}{get_branding_profile()['favicon_path']}", permanent=True),
    ),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    
    # Specific paths first
    path("legajos/", include("legajos.interfaces.web.urls")),
    path("configuracion/", include("configuracion.interfaces.web.urls")),
    path("portal/", include("portal.interfaces.web.urls")),
    path("portal-ciudadano/", include("portal_ciudadano.urls")),
    path("auditoria/", include("core.interfaces.web.urls_auditoria")),
] + _module_web_paths() + [
    # Root paths last
    path("", include("django.contrib.auth.urls")),
    path("", include(("users.interfaces.web.urls", "users"), namespace="users")),
    path("", include(("core.interfaces.web.urls", "core"), namespace="core")),
    path("", include("dashboard.interfaces.web.urls")),
    path("", include(("healthcheck.interfaces.web.urls", "healthcheck"), namespace="healthcheck")),
    # Flujos - editor visual HTML

    # API Routes
    path("api/legajos/", include("legajos.interfaces.api.urls")),
    path("api/core/", include("core.interfaces.api.urls")),
    path("api/users/", include("users.interfaces.api.urls")),
    path("api/reclamos/", include("reclamos.api_urls")),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # Health Check
    path("health/", include('health_check.urls')),
    
    # Performance Profiling (solo en desarrollo/staging)
    path("silk/", include('silk.urls', namespace='silk')),
]

urlpatterns += _module_api_paths()

# URLs de desarrollo se pueden agregar aquí si es necesario

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = "config.views.server_error"
