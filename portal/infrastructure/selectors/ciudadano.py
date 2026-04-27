from importlib import import_module

from django.http import Http404

from system_modules.infrastructure.services import module_is_active


def _conversaciones_api():
    return import_module("conversaciones.interfaces.module_api")


def get_ciudadano_perfil(user):
    return user.ciudadano_perfil


def get_ciudadano_conversaciones(user, ciudadano):
    if not module_is_active("conversaciones"):
        return []
    return _conversaciones_api().get_ciudadano_conversaciones(user=user, ciudadano=ciudadano)


def get_ciudadano_conversacion_or_404(user, ciudadano, pk):
    if not module_is_active("conversaciones"):
        raise Http404
    return _conversaciones_api().get_ciudadano_conversacion_or_404(
        user=user,
        ciudadano=ciudadano,
        pk=pk,
    )
