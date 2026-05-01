import logging
import time

from django.shortcuts import redirect

logger = logging.getLogger("core.requests")


class PortalCiudadanoMiddleware:
    """
    Impide que usuarios del grupo Ciudadanos accedan al backoffice.
    Si un ciudadano autenticado accede a una URL fuera de /portal/, se lo redirige.
    """

    # Prefijos de URL fuera de /portal/ que los ciudadanos pueden usar (endpoints AJAX del portal)
    _ALLOWED_PREFIXES = (
        '/portal/',
        '/portal-ciudadano',
        '/static/',
        '/media/',
        '/conversaciones/iniciar-guiado/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if (
            request.user.is_authenticated
            and request.user.groups.filter(name='Ciudadanos').exists()
            and not any(request.path.startswith(p) for p in self._ALLOWED_PREFIXES)
            and not request.path.endswith('/reactivar-bot/')
        ):
            return redirect('portal:ciudadano_mi_perfil')
        return self.get_response(request)


class RequestLoggingMiddleware:
    """Loguea cada request HTTP con método, URL, usuario, IP, status y duración."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration_ms = int((time.monotonic() - start) * 1000)

        user = getattr(request, "user", None)
        username = user.username if user and user.is_authenticated else "anon"
        ip = request.META.get("HTTP_X_REAL_IP") or request.META.get("REMOTE_ADDR", "-")

        logger.info(
            "%s %s user=%s ip=%s status=%s duration=%dms",
            request.method,
            request.path,
            username,
            ip,
            response.status_code,
            duration_ms,
        )

        return response
