"""
Vistas para Gestión Operativa de Programas
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from django.contrib import messages

from .models_programas import Programa
from .models_institucional import (
    InstitucionPrograma,
    CoordinadorPrograma,
    DerivacionInstitucional,
    CasoInstitucional,
    EstadoDerivacion,
    EstadoCaso
)


class ProgramaListView(LoginRequiredMixin, ListView):
    """
    Lista de programas que el usuario puede gestionar.
    - SuperAdmin: ve todos
    - Coordinador: ve solo sus programas asignados
    """
    model = Programa
    template_name = 'legajos/programas/programa_list.html'
    context_object_name = 'programas'
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            # SuperAdmin ve todos los programas
            queryset = Programa.objects.filter(activo=True)
        else:
            # Coordinador ve solo sus programas
            queryset = Programa.objects.filter(
                coordinadores__usuario=self.request.user,
                coordinadores__activo=True,
                activo=True
            )
        
        # Agregar métricas
        queryset = queryset.annotate(
            total_instituciones=Count('instituciones_habilitadas', filter=Q(instituciones_habilitadas__activo=True)),
            total_derivaciones_pendientes=Count('derivaciones_programa', filter=Q(derivaciones_programa__estado=EstadoDerivacion.PENDIENTE)),
            total_casos_activos=Count('instituciones_habilitadas__casos', filter=Q(instituciones_habilitadas__casos__estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]))
        ).order_by('orden', 'nombre')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_superadmin'] = self.request.user.is_superuser
        return context


class ProgramaDetailView(LoginRequiredMixin, DetailView):
    """
    Vista detallada de un programa con 5 solapas operativas:
    1. Dashboard Ejecutivo
    2. Bandeja de Derivaciones
    3. Ciudadanos en Atención
    4. Instituciones Participantes
    5. Indicadores
    """
    model = Programa
    template_name = 'legajos/programas/programa_detail.html'
    context_object_name = 'programa'
    
    def dispatch(self, request, *args, **kwargs):
        # Permitir acceso a todos los usuarios autenticados temporalmente
        # TODO: Restaurar verificación de permisos cuando se asignen coordinadores
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        programa = self.get_object()
        
        # Métricas del dashboard
        instituciones_habilitadas = InstitucionPrograma.objects.filter(
            programa=programa,
            activo=True
        ).select_related('institucion')
        
        context['total_instituciones'] = instituciones_habilitadas.count()
        
        context['total_derivaciones_pendientes'] = DerivacionInstitucional.objects.filter(
            programa=programa,
            estado=EstadoDerivacion.PENDIENTE
        ).count()
        
        context['total_casos_activos'] = CasoInstitucional.objects.filter(
            institucion_programa__programa=programa,
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
        ).count()
        
        context['total_casos_totales'] = CasoInstitucional.objects.filter(
            institucion_programa__programa=programa
        ).count()
        
        # BANDEJA DE DERIVACIONES (ciudadanos)
        from .models_programas import DerivacionPrograma
        
        # Derivaciones de ciudadanos al mismo programa
        context['derivaciones_ciudadanos'] = DerivacionPrograma.objects.filter(
            programa_destino=programa
        ).select_related('ciudadano', 'programa_origen', 'derivado_por').order_by('-creado')[:20]
        
        # Stats de derivaciones ciudadanos
        context['stats_ciudadanos'] = {
            'pendientes': DerivacionPrograma.objects.filter(programa_destino=programa, estado='PENDIENTE').count(),
            'aceptadas': DerivacionPrograma.objects.filter(programa_destino=programa, estado='ACEPTADA').count(),
            'rechazadas': DerivacionPrograma.objects.filter(programa_destino=programa, estado='RECHAZADA').count(),
        }
        
        # Derivaciones institucionales
        context['derivaciones_institucionales'] = DerivacionInstitucional.objects.filter(
            programa=programa
        ).select_related('ciudadano', 'institucion', 'derivado_por').order_by('-creado')[:20]
        
        # Instituciones participantes
        context['instituciones'] = instituciones_habilitadas.annotate(
            casos_activos=Count('casos', filter=Q(casos__estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO])),
            derivaciones_pendientes=Count('derivaciones', filter=Q(derivaciones__estado=EstadoDerivacion.PENDIENTE))
        )
        
        # Casos activos
        context['casos_activos'] = CasoInstitucional.objects.filter(
            institucion_programa__programa=programa,
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO]
        ).select_related('ciudadano', 'institucion_programa__institucion', 'responsable').order_by('-fecha_apertura')[:20]
        
        context['es_superadmin'] = self.request.user.is_superuser
        
        return context
