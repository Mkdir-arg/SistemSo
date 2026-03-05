import logging
import time

logger = logging.getLogger("core.requests")


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
