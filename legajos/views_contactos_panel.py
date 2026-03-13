from django.shortcuts import render

from .selectors_contactos import get_legajo_contactos_context


def red_contactos_simple(request, legajo_id):
    """Vista simple para red de contactos"""
    return render(
        request,
        'legajos/red_contactos_simple.html',
        get_legajo_contactos_context(legajo_id),
    )


def dashboard_contactos_simple(request):
    """Dashboard simple de contactos"""
    return render(
        request,
        'legajos/dashboard_contactos_simple.html',
        {'titulo': 'Dashboard de Contactos'},
    )


def historial_contactos_simple(request, legajo_id):
    """Vista simple para historial de contactos"""
    return render(
        request,
        'legajos/historial_contactos_simple.html',
        get_legajo_contactos_context(legajo_id),
    )
