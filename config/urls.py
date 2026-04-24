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
    path("legajos/", include("legajos.urls")),
    path("configuracion/", include("configuracion.urls")),
    path("portal/", include("portal.urls")),
    path("auditoria/", include("core.urls_auditoria")),
] + _module_web_paths() + [
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

urlpatterns += _module_api_paths()

# URLs de desarrollo se pueden agregar aquí si es necesario

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = "config.views.server_error"
