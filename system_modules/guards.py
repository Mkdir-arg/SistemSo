from functools import wraps

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.permissions import BasePermission

from .services import ModuleResolver, module_is_active


def build_module_disabled_response(request, slug):
    resolver = ModuleResolver()
    if resolver.is_registered(slug):
        display_name = resolver.get_definition(slug).display_name
    else:
        display_name = slug.replace("_", " ").title()
    wants_json = (
        request.path.startswith("/api/")
        or request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("Accept", "")
    )
    payload = {
        "code": "module_inactive",
        "module": slug,
        "display_name": display_name,
        "message": (
            f'El modulo "{display_name}" no esta disponible para esta instancia.'
        ),
    }
    if wants_json:
        return JsonResponse(payload, status=403)
    return render(
        request,
        "system_modules/module_disabled.html",
        payload,
        status=403,
    )


def module_required(slug):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not module_is_active(slug):
                return build_module_disabled_response(request, slug)
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class ModuleRequiredMixin:
    module_slug = None

    def dispatch(self, request, *args, **kwargs):
        if self.module_slug and not module_is_active(self.module_slug):
            return build_module_disabled_response(request, self.module_slug)
        return super().dispatch(request, *args, **kwargs)


class ModuleActivePermission(BasePermission):
    module_slug = None

    def has_permission(self, request, view):
        module_slug = self.module_slug or getattr(view, "module_slug", None)
        if not module_slug:
            return True
        return module_is_active(module_slug)


def run_if_module_active(slug, callback, *args, **kwargs):
    if not module_is_active(slug):
        return None
    return callback(*args, **kwargs)
