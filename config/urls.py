from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    
    # Specific paths first
    path("legajos/", include("legajos.urls")),
    path("configuracion/", include("configuracion.urls")),
    path("chatbot/", include("chatbot.urls")),
    path("conversaciones/", include("conversaciones.urls")),
    path("portal/", include("portal.urls")),
    path("tramites/", include("tramites.urls")),
    path("auditoria/", include("core.urls_auditoria")),
    
    # Root paths last
    path("", include("django.contrib.auth.urls")),
    path("", include("users.urls")),
    path("", include("core.urls")),
    path("", include("dashboard.urls")),

    path("", include("healthcheck.urls")),
    
    # API Routes
    path("api/legajos/", include("legajos.api_urls")),
    path("api/core/", include("core.api_urls")),
    path("api/chatbot/", include("chatbot.api_urls")),
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

# URLs de desarrollo se pueden agregar aquí si es necesario

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler500 = "config.views.server_error"
