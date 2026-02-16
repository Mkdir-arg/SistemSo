from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView, View
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils.decorators import method_decorator
from core.cache_decorators import cache_view, cache_queryset, invalidate_cache_pattern
import csv
import json
from datetime import datetime
from .models import Ciudadano, LegajoAtencion, EvaluacionInicial, PlanIntervencion, SeguimientoContacto, Profesional, Derivacion, EventoCritico, AlertaEventoCritico, LegajoInstitucional, InscriptoActividad, PlanFortalecimiento
from core.models import DispositivoRed
from .forms import ConsultaRenaperForm, CiudadanoForm, BuscarCiudadanoForm, AdmisionLegajoForm, ConsentimientoForm, EvaluacionInicialForm, PlanIntervencionForm, SeguimientoForm, DerivacionForm, EventoCriticoForm, LegajoCerrarForm, InscribirActividadForm
from .services.consulta_renaper import consultar_datos_renaper

# Importar views de contactos
from .views_dashboard_contactos import dashboard_contactos, metricas_contactos_api, metricas_red_contactos_api, exportar_reporte_contactos
from .views_historial_contactos import historial_contactos_view, contactos_api, crear_contacto, detalle_contacto, editar_contacto, eliminar_contacto
from .views_red_contactos import red_contactos_view, vinculos_api, profesionales_api, dispositivos_api, emergencias_api, buscar_ciudadanos_api, buscar_usuarios_api, crear_vinculo, crear_profesional, crear_contacto_emergencia


@method_decorator(cache_view(timeout=300), name='dispatch')
class CiudadanoListView(LoginRequiredMixin, ListView):
    model = Ciudadano
    template_name = 'legajos/ciudadano_list.html'
    context_object_name = 'ciudadanos'
    paginate_by = 20
    
    def get_queryset(self):
        search = self.request.GET.get('search', '')
        queryset = Ciudadano.objects.filter(activo=True)
        
        if search:
            queryset = queryset.filter(
                Q(dni__icontains=search) |
                Q(nombre__icontains=search) |
                Q(apellido__icontains=search)
            )
        
        return queryset.order_by('apellido', 'nombre')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Métricas del dashboard
        total_ciudadanos = Ciudadano.objects.filter(activo=True).count()
        legajos_activos = LegajoAtencion.objects.filter(estado__in=['ABIERTO', 'EN_SEGUIMIENTO']).count()
        alertas_criticas = EventoCritico.objects.count()
        
        from datetime import date
        seguimientos_hoy = SeguimientoContacto.objects.filter(creado__date=date.today()).count()
        
        # Tasa de adherencia
        total_seguimientos = SeguimientoContacto.objects.count()
        seguimientos_adecuados = SeguimientoContacto.objects.filter(adherencia='ADECUADA').count()
        tasa_adherencia = round((seguimientos_adecuados / total_seguimientos * 100) if total_seguimientos > 0 else 0)
        
        casos_alto_riesgo = LegajoAtencion.objects.filter(nivel_riesgo='ALTO').count()
        
        context['metricas'] = {
            'total_ciudadanos': total_ciudadanos,
            'legajos_activos': legajos_activos,
            'alertas_criticas': alertas_criticas,
            'seguimientos_hoy': seguimientos_hoy,
            'tasa_adherencia': tasa_adherencia,
            'casos_alto_riesgo': casos_alto_riesgo,
        }
        
        return context
    



class CiudadanoDetailView(LoginRequiredMixin, DetailView):
    model = Ciudadano
    template_name = 'legajos/ciudadano_detail.html'
    context_object_name = 'ciudadano'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajos'] = self.object.legajos.select_related('dispositivo', 'responsable').order_by('-fecha_apertura')
        
        # Agregar solapas dinámicas
        from .services_solapas import SolapasService
        context['solapas'] = SolapasService.obtener_solapas_ciudadano(self.object)
        context['programas_activos'] = SolapasService.obtener_programas_activos(self.object)
        
        return context


class CiudadanoCreateView(LoginRequiredMixin, FormView):
    """Vista para crear ciudadanos con integración RENAPER"""
    template_name = 'legajos/ciudadano_renaper_form.html'
    form_class = ConsultaRenaperForm
    
    def extraer_dni_de_cuit(self, cuit):
        """Extrae el DNI del CUIT (formato XX-XXXXXXXX-X)"""
        import re
        # Limpiar el CUIT de guiones y espacios
        cuit_limpio = re.sub(r'[^0-9]', '', cuit)
        
        # Verificar que tenga 11 dígitos
        if len(cuit_limpio) != 11:
            return None
            
        # Extraer DNI (dígitos 3 al 10)
        dni = cuit_limpio[2:10]
        
        # Verificar que el DNI tenga 8 dígitos
        if len(dni) != 8:
            return None
            
        return dni
    
    def form_valid(self, form):
        dni = form.cleaned_data['dni']
        sexo = form.cleaned_data['sexo']
        
        # Verificar si el ciudadano ya existe
        if Ciudadano.objects.filter(dni=dni).exists():
            messages.error(self.request, f'Ya existe un ciudadano con DNI {dni}')
            return self.form_invalid(form)
        
        # Consultar RENAPER
        resultado = consultar_datos_renaper(dni, sexo)
        
        if not resultado['success']:
            # Guardar datos para mostrar opción manual
            context = self.get_context_data(form=form)
            context['renaper_error'] = True
            context['dni_consultado'] = dni
            context['sexo_consultado'] = sexo
            
            if resultado.get('fallecido'):
                context['error_message'] = 'La persona consultada figura como fallecida en RENAPER'
            else:
                context['error_message'] = f'No se encontraron datos en RENAPER: {resultado.get("error", "Error desconocido")}'
            
            return self.render_to_response(context)
        
        # Guardar datos en sesión para el siguiente paso
        self.request.session['datos_renaper'] = resultado['data']
        self.request.session['datos_api_renaper'] = resultado.get('datos_api', {})
        
        return redirect('legajos:ciudadano_confirmar')


class CiudadanoManualView(LoginRequiredMixin, CreateView):
    """Vista para crear ciudadanos manualmente cuando RENAPER falla"""
    model = Ciudadano
    form_class = CiudadanoForm
    template_name = 'legajos/ciudadano_manual_form.html'
    success_url = reverse_lazy('legajos:ciudadanos')
    
    def get_initial(self):
        """Prellenar DNI y sexo si vienen de RENAPER"""
        initial = super().get_initial()
        cuit = self.request.GET.get('cuit')
        sexo = self.request.GET.get('sexo')
        
        if cuit:
            # Extraer DNI del CUIT
            import re
            cuit_limpio = re.sub(r'[^0-9]', '', cuit)
            if len(cuit_limpio) == 11:
                dni = cuit_limpio[2:10]
                initial['dni'] = dni
        if sexo:
            initial['genero'] = sexo
            
        return initial
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        invalidate_cache_pattern('ciudadanos_list')
        from dashboard.utils import invalidate_dashboard_cache
        invalidate_dashboard_cache()
        
        messages.success(self.request, f'Ciudadano {self.object.nombre} {self.object.apellido} creado exitosamente (carga manual)')
        
        from django.shortcuts import redirect
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class CiudadanoConfirmarView(LoginRequiredMixin, CreateView):
    """Vista para confirmar y completar datos del ciudadano"""
    model = Ciudadano
    form_class = CiudadanoForm
    template_name = 'legajos/ciudadano_confirmar_form.html'
    success_url = reverse_lazy('legajos:ciudadanos')
    
    def dispatch(self, request, *args, **kwargs):
        if 'datos_renaper' not in request.session:
            messages.error(request, 'No hay datos de RENAPER disponibles. Inicie el proceso nuevamente.')
            return redirect('legajos:ciudadano_nuevo')
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        """Prellenar el formulario con datos de RENAPER"""
        datos = self.request.session.get('datos_renaper', {})
        return {
            'dni': datos.get('dni'),
            'nombre': datos.get('nombre'),
            'apellido': datos.get('apellido'),
            'fecha_nacimiento': datos.get('fecha_nacimiento'),
            'genero': datos.get('genero'),
            'domicilio': datos.get('domicilio'),
        }
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datos_api'] = self.request.session.get('datos_api_renaper', {})
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.request.session.pop('datos_renaper', None)
        self.request.session.pop('datos_api_renaper', None)
        
        invalidate_cache_pattern('ciudadanos_list')
        from dashboard.utils import invalidate_dashboard_cache
        invalidate_dashboard_cache()
        
        messages.success(self.request, f'Ciudadano {self.object.nombre} {self.object.apellido} creado exitosamente')
        
        from django.shortcuts import redirect
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class CiudadanoUpdateView(LoginRequiredMixin, UpdateView):
    model = Ciudadano
    form_class = CiudadanoForm
    template_name = 'legajos/ciudadano_edit_form.html'
    
    def get_success_url(self):
        return reverse_lazy('legajos:ciudadano_detalle', kwargs={'pk': self.object.pk})


@method_decorator(cache_view(timeout=300), name='dispatch')
class LegajoListView(LoginRequiredMixin, ListView):
    model = LegajoAtencion
    template_name = 'legajos/legajo_list.html'
    context_object_name = 'legajos'
    paginate_by = 20
    
    def get_queryset(self):
        estado = self.request.GET.get('estado', '')
        queryset = LegajoAtencion.objects.select_related('ciudadano', 'dispositivo')
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('-fecha_apertura')


class LegajoDetailView(LoginRequiredMixin, DetailView):
    model = LegajoAtencion
    template_name = 'legajos/legajo_detail.html'
    context_object_name = 'legajo'


class LegajoCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear legajo directamente"""
    model = LegajoAtencion
    form_class = AdmisionLegajoForm
    template_name = 'legajos/legajo_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ciudadanos'] = Ciudadano.objects.filter(activo=True).order_by('apellido', 'nombre')
        return context
    
    def form_valid(self, form):
        form.instance.responsable = self.request.user
        response = super().form_valid(form)
        
        invalidate_cache_pattern('legajos_list')
        from dashboard.utils import invalidate_dashboard_cache
        invalidate_dashboard_cache()
        
        messages.success(self.request, f'Legajo {self.object.codigo} creado exitosamente.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('legajos:detalle', kwargs={'pk': self.object.pk})


class AdmisionPaso1View(LoginRequiredMixin, FormView):
    """Paso 1: Buscar ciudadano"""
    template_name = 'legajos/admision_paso1.html'
    form_class = BuscarCiudadanoForm
    
    def get(self, request, *args, **kwargs):
        # Si viene con ciudadano preseleccionado, ir directo al paso 2
        ciudadano_id = request.GET.get('ciudadano')
        if ciudadano_id:
            try:
                ciudadano = Ciudadano.objects.get(id=ciudadano_id, activo=True)
                request.session['admision_ciudadano_id'] = ciudadano.id
                return redirect('legajos:admision_paso2')
            except Ciudadano.DoesNotExist:
                messages.error(request, 'Ciudadano no encontrado')
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        dni = form.cleaned_data['dni']
        
        try:
            ciudadano = Ciudadano.objects.get(dni=dni, activo=True)
            self.request.session['admision_ciudadano_id'] = ciudadano.id
            return redirect('legajos:admision_paso2')
        except Ciudadano.DoesNotExist:
            messages.error(self.request, f'No se encontró un ciudadano con DNI {dni}. Debe crear el ciudadano primero.')
            return self.form_invalid(form)


class AdmisionPaso2View(LoginRequiredMixin, CreateView):
    """Paso 2: Datos de admisión"""
    model = LegajoAtencion
    form_class = AdmisionLegajoForm
    template_name = 'legajos/admision_paso2.html'
    
    def dispatch(self, request, *args, **kwargs):
        if 'admision_ciudadano_id' not in request.session:
            messages.error(request, 'Debe seleccionar un ciudadano primero.')
            return redirect('legajos:admision_paso1')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano_id = self.request.session.get('admision_ciudadano_id')
        context['ciudadano'] = get_object_or_404(Ciudadano, id=ciudadano_id)
        
        # Agregar información de debug para dispositivos disponibles
        if self.request.user.is_superuser:
            context['debug_dispositivos'] = True
            context['total_dispositivos'] = DispositivoRed.objects.filter(activo=True).count()
        
        return context
    
    def form_valid(self, form):
        ciudadano_id = self.request.session.get('admision_ciudadano_id')
        form.instance.ciudadano_id = ciudadano_id
        
        # Si no se especificó responsable, usar el usuario actual
        if not form.instance.responsable:
            form.instance.responsable = self.request.user
        
        try:
            response = super().form_valid(form)
            
            # Limpiar sesión y guardar ID del legajo para paso 3
            self.request.session.pop('admision_ciudadano_id', None)
            self.request.session['admision_legajo_id'] = str(self.object.id)
            
            return redirect('legajos:admision_paso3')
        except Exception as e:
            # En caso de error, agregar mensaje y volver a mostrar el formulario
            messages.error(self.request, f'Error al crear el legajo: {str(e)}')
            return self.form_invalid(form)


class AdmisionPaso3View(LoginRequiredMixin, FormView):
    """Paso 3: Consentimiento (opcional)"""
    template_name = 'legajos/admision_paso3.html'
    form_class = ConsentimientoForm
    
    def dispatch(self, request, *args, **kwargs):
        if 'admision_legajo_id' not in request.session:
            messages.error(request, 'Proceso de admisión inválido.')
            return redirect('legajos:admision_paso1')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo_id = self.request.session.get('admision_legajo_id')
        context['legajo'] = get_object_or_404(LegajoAtencion, id=legajo_id)
        return context
    
    def form_valid(self, form):
        legajo_id = self.request.session.get('admision_legajo_id')
        legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
        
        form.instance.ciudadano = legajo.ciudadano
        form.save()
        
        # Limpiar sesión
        self.request.session.pop('admision_legajo_id', None)
        
        messages.success(self.request, f'Legajo {legajo.codigo} creado exitosamente con consentimiento.')
        return redirect('legajos:detalle', pk=legajo.id)
    
    def get(self, request, *args, **kwargs):
        # Permitir saltar este paso
        if request.GET.get('skip') == '1':
            legajo_id = request.session.get('admision_legajo_id')
            legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
            request.session.pop('admision_legajo_id', None)
            messages.success(request, f'Legajo {legajo.codigo} creado exitosamente.')
            return redirect('legajos:detalle', pk=legajo.id)
        
        return super().get(request, *args, **kwargs)


class EvaluacionInicialView(LoginRequiredMixin, UpdateView):
    """Vista para crear/editar evaluación inicial"""
    model = EvaluacionInicial
    form_class = EvaluacionInicialForm
    template_name = 'legajos/evaluacion_form.html'
    
    def get_object(self, queryset=None):
        legajo_id = self.kwargs.get('legajo_id')
        legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
        
        # Crear evaluación si no existe (OneToOne)
        evaluacion, created = EvaluacionInicial.objects.get_or_create(
            legajo=legajo,
            defaults={}
        )
        return evaluacion
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Evaluación inicial guardada exitosamente.')
        return reverse_lazy('legajos:detalle', kwargs={'pk': self.object.legajo.id})


class PlanIntervencionView(LoginRequiredMixin, CreateView):
    """Vista para crear plan de intervención"""
    model = PlanIntervencion
    form_class = PlanIntervencionForm
    template_name = 'legajos/plan_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        if not hasattr(self.legajo, 'evaluacion'):
            messages.error(request, 'Debe completar la evaluación inicial antes de crear un plan.')
            return redirect('legajos:evaluacion', legajo_id=self.legajo.id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context
    
    def form_valid(self, form):
        # Crear el plan sin guardar aún
        plan = form.save(commit=False)
        plan.legajo = self.legajo
        profesional, created = Profesional.objects.get_or_create(
            usuario=self.request.user,
            defaults={'rol': 'Operador'}
        )
        plan.profesional = profesional
        
        # Procesar actividades dinámicas
        actividades = []
        i = 1
        while f'actividad_{i}' in self.request.POST:
            accion = self.request.POST.get(f'actividad_{i}')
            freq = self.request.POST.get(f'frecuencia_{i}')
            responsable = self.request.POST.get(f'responsable_{i}')
            
            if accion:
                actividades.append({
                    'accion': accion,
                    'freq': freq or '',
                    'responsable': responsable or ''
                })
            i += 1
        
        plan.actividades = actividades if actividades else None
        plan.save()
        
        messages.success(self.request, 'Plan de intervención creado exitosamente.')
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('legajos:planes', kwargs={'legajo_id': self.legajo.id})


class SeguimientoCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear seguimiento"""
    model = SeguimientoContacto
    form_class = SeguimientoForm
    template_name = 'legajos/seguimiento_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context
    
    def form_valid(self, form):
        form.instance.legajo = self.legajo
        profesional, created = Profesional.objects.get_or_create(
            usuario=self.request.user,
            defaults={'rol': 'Operador'}
        )
        form.instance.profesional = profesional
        response = super().form_valid(form)
        messages.success(self.request, 'Seguimiento registrado exitosamente.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('legajos:seguimientos', kwargs={'legajo_id': self.legajo.id})


class SeguimientoListView(LoginRequiredMixin, ListView):
    """Vista para listar seguimientos"""
    model = SeguimientoContacto
    template_name = 'legajos/seguimiento_list.html'
    context_object_name = 'seguimientos'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = self.legajo.seguimientos.select_related('profesional__usuario')
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['tipos'] = SeguimientoContacto.TipoContacto.choices
        context['total_seguimientos'] = self.legajo.seguimientos.count()
        context['entrevistas_count'] = self.legajo.seguimientos.filter(tipo='ENTREVISTA').count()
        context['visitas_count'] = self.legajo.seguimientos.filter(tipo='VISITA').count()
        context['llamadas_count'] = self.legajo.seguimientos.filter(tipo='LLAMADA').count()
        return context


class DerivacionCreateView(LoginRequiredMixin, CreateView):
    """Vista para crear derivación"""
    model = Derivacion
    form_class = DerivacionForm
    template_name = 'legajos/derivacion_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['legajo'] = self.legajo
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context
    
    def form_valid(self, form):
        form.instance.legajo = self.legajo
        response = super().form_valid(form)
        messages.success(self.request, 'Derivación creada exitosamente.')
        return response
    
    def get_success_url(self):
        return reverse_lazy('legajos:derivaciones', kwargs={'legajo_id': self.legajo.id})


class EventoCriticoCreateView(LoginRequiredMixin, CreateView):
    """Vista para registrar evento crítico"""
    model = EventoCritico
    form_class = EventoCriticoForm
    template_name = 'legajos/evento_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context
    
    def form_valid(self, form):
        form.instance.legajo = self.legajo
        response = super().form_valid(form)
        messages.warning(self.request, f'Evento crítico registrado: {form.instance.get_tipo_display()}')
        return response
    
    def get_success_url(self):
        return reverse_lazy('legajos:eventos', kwargs={'legajo_id': self.legajo.id})


class DerivacionListView(LoginRequiredMixin, ListView):
    """Vista para listar derivaciones"""
    model = Derivacion
    template_name = 'legajos/derivacion_list.html'
    context_object_name = 'derivaciones'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = self.legajo.derivaciones.select_related('destino')
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['estados'] = Derivacion.Estado.choices
        return context


class LegajoCerrarView(LoginRequiredMixin, FormView):
    """Vista para cerrar legajo"""
    template_name = 'legajos/legajo_cerrar.html'
    form_class = LegajoCerrarForm
    
    def get_object(self):
        return get_object_or_404(LegajoAtencion, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        legajo = self.get_object()
        puede, mensaje = legajo.puede_cerrar()
        context['legajo'] = legajo
        context['puede_cerrar'] = puede
        context['mensaje'] = mensaje
        return context
    
    def form_valid(self, form):
        legajo = self.get_object()
        motivo = form.cleaned_data.get('motivo_cierre', '')
        
        try:
            legajo.cerrar(motivo_cierre=motivo, usuario=self.request.user)
            messages.success(self.request, f'Legajo {legajo.codigo} cerrado exitosamente.')
            return redirect('legajos:detalle', pk=legajo.pk)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)


class LegajoReabrirView(LoginRequiredMixin, FormView):
    """Vista para reabrir legajo"""
    template_name = 'legajos/legajo_reabrir.html'
    
    def get_object(self):
        return get_object_or_404(LegajoAtencion, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.get_object()
        return context
    
    def post(self, request, *args, **kwargs):
        legajo = self.get_object()
        motivo = request.POST.get('motivo_reapertura', '')
        
        try:
            legajo.reabrir(motivo_reapertura=motivo, usuario=request.user)
            messages.success(request, f'Legajo {legajo.codigo} reabierto exitosamente.')
            return redirect('legajos:detalle', pk=legajo.pk)
        except ValidationError as e:
            messages.error(request, str(e))
            return self.get(request, *args, **kwargs)


@method_decorator(cache_view(timeout=600), name='dispatch')
class ReportesView(LoginRequiredMixin, TemplateView):
    """Vista para mostrar reportes y estadísticas"""
    template_name = 'legajos/reportes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # Estadísticas generales
        stats = {
            'total_legajos': LegajoAtencion.objects.count(),
            'legajos_activos': LegajoAtencion.objects.filter(estado__in=['ABIERTO', 'EN_SEGUIMIENTO']).count(),
            'riesgo_alto': LegajoAtencion.objects.filter(nivel_riesgo='ALTO').count(),
            'nuevos_semana': LegajoAtencion.objects.filter(
                fecha_apertura__gte=datetime.now().date() - timedelta(days=7)
            ).count(),
        }
        
        # Estadísticas por estado
        stats['por_estado'] = LegajoAtencion.objects.values('estado').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Estadísticas por nivel de riesgo
        stats['por_riesgo'] = LegajoAtencion.objects.values('nivel_riesgo').annotate(
            total=Count('id')
        ).order_by('-total')
        
        # Estadísticas por dispositivo
        stats['por_dispositivo'] = LegajoAtencion.objects.select_related('dispositivo').values(
            'dispositivo__nombre', 'dispositivo__tipo'
        ).annotate(total=Count('id')).order_by('-total')[:10]
        
        # Actividad por mes (últimos 6 meses)
        from django.db.models import DateTimeField
        from django.db.models.functions import TruncMonth
        
        fecha_limite = datetime.now().date() - timedelta(days=180)
        stats['por_mes'] = LegajoAtencion.objects.filter(
            fecha_apertura__gte=fecha_limite
        ).annotate(
            mes=TruncMonth('fecha_apertura')
        ).values('mes').annotate(total=Count('id')).order_by('-mes')[:6]
        
        # Métricas de calidad
        legajos_con_seguimiento = LegajoAtencion.objects.filter(
            seguimientos__isnull=False
        ).distinct().count()
        
        stats['metricas_calidad'] = {
            'ttr_promedio': self._calcular_ttr_promedio(),
            'adherencia_adecuada': self._calcular_adherencia(),
            'tasa_derivacion': self._calcular_tasa_derivacion(),
            'eventos_por_100': self._calcular_eventos_por_100(),
            'cobertura_seguimiento': round((legajos_con_seguimiento / max(stats['total_legajos'], 1)) * 100, 1)
        }
        
        context['stats'] = stats
        return context
    
    def _calcular_ttr_promedio(self):
        """Tiempo promedio admisión → primer seguimiento"""
        legajos_con_seguimiento = LegajoAtencion.objects.filter(
            seguimientos__isnull=False
        ).distinct()
        
        tiempos = []
        for legajo in legajos_con_seguimiento:
            tiempo = legajo.tiempo_primer_contacto
            if tiempo is not None:
                tiempos.append(tiempo)
        
        return round(sum(tiempos) / len(tiempos), 1) if tiempos else 0
    
    def _calcular_adherencia(self):
        """Porcentaje de seguimientos con adherencia adecuada"""
        total_seguimientos = SeguimientoContacto.objects.count()
        adherencia_adecuada = SeguimientoContacto.objects.filter(
            adherencia='ADECUADA'
        ).count()
        
        return round((adherencia_adecuada / max(total_seguimientos, 1)) * 100, 1)
    
    def _calcular_tasa_derivacion(self):
        """Porcentaje de derivaciones aceptadas"""
        total_derivaciones = Derivacion.objects.count()
        derivaciones_aceptadas = Derivacion.objects.filter(
            estado='ACEPTADA'
        ).count()
        
        return round((derivaciones_aceptadas / max(total_derivaciones, 1)) * 100, 1)
    
    def _calcular_eventos_por_100(self):
        """Eventos críticos por cada 100 legajos"""
        from legajos.models import EventoCritico
        total_legajos = LegajoAtencion.objects.count()
        total_eventos = EventoCritico.objects.count()
        
        return round((total_eventos / max(total_legajos, 1)) * 100, 1)


class DispositivoDerivacionesView(LoginRequiredMixin, ListView):
    """Vista para mostrar derivaciones de un dispositivo específico"""
    model = Derivacion
    template_name = 'legajos/dispositivo_derivaciones.html'
    context_object_name = 'derivaciones'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        self.dispositivo = get_object_or_404(DispositivoRed, pk=kwargs['dispositivo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Derivacion.objects.filter(
            destino=self.dispositivo
        ).select_related('legajo__ciudadano')
        
        estado = self.request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
        
        return queryset.order_by('-creado')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['dispositivo'] = self.dispositivo
        context['estados'] = Derivacion.Estado.choices
        return context


class ExportarCSVView(LoginRequiredMixin, View):
    """Vista para exportar legajos a CSV"""
    
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="legajos_export.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Codigo', 'Ciudadano_DNI', 'Ciudadano_Nombre', 'Ciudadano_Apellido',
            'Dispositivo', 'Estado', 'Nivel_Riesgo', 'Via_Ingreso', 
            'Fecha_Apertura', 'Fecha_Cierre', 'Dias_Admision', 'Plan_Vigente'
        ])
        
        # Aplicar filtros de la request
        queryset = LegajoAtencion.objects.select_related('ciudadano', 'dispositivo')
        
        estado = request.GET.get('estado')
        if estado:
            queryset = queryset.filter(estado=estado)
            
        riesgo = request.GET.get('riesgo')
        if riesgo:
            queryset = queryset.filter(nivel_riesgo=riesgo)
        
        for legajo in queryset:
            writer.writerow([
                legajo.codigo,
                legajo.ciudadano.dni,
                legajo.ciudadano.nombre,
                legajo.ciudadano.apellido,
                legajo.dispositivo.nombre,
                legajo.get_estado_display(),
                legajo.get_nivel_riesgo_display(),
                legajo.get_via_ingreso_display(),
                legajo.fecha_apertura.strftime('%d/%m/%Y'),
                legajo.fecha_cierre.strftime('%d/%m/%Y') if legajo.fecha_cierre else '',
                legajo.dias_desde_admision,
                'Sí' if legajo.plan_vigente else 'No'
            ])
        
        return response


class CerrarAlertaEventoView(LoginRequiredMixin, View):
    """Vista AJAX para cerrar alertas de eventos críticos"""
    
    def post(self, request, *args, **kwargs):
        evento_id = request.POST.get('evento_id')
        
        try:
            evento = EventoCritico.objects.get(id=evento_id)
            
            # Verificar que el usuario sea responsable del legajo
            if evento.legajo.responsable != request.user:
                return JsonResponse({'success': False, 'error': 'No autorizado'})
            
            # Crear registro de alerta vista
            AlertaEventoCritico.objects.get_or_create(
                evento=evento,
                responsable=request.user
            )
            
            return JsonResponse({'success': True})
            
        except EventoCritico.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Evento no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class CambiarResponsableView(LoginRequiredMixin, View):
    """Vista AJAX para cambiar responsable del legajo"""
    
    def get(self, request, *args, **kwargs):
        """Obtener lista de usuarios con rol correspondiente"""
        from django.contrib.auth.models import User
        from django.contrib.auth.models import Group
        
        # Obtener usuarios del grupo Ciudadanos (que pueden ser responsables)
        grupo_ciudadanos = Group.objects.get(name='Ciudadanos')
        usuarios = User.objects.filter(
            groups=grupo_ciudadanos,
            is_active=True
        ).values('id', 'username', 'first_name', 'last_name')
        
        usuarios_list = []
        for usuario in usuarios:
            nombre_completo = f"{usuario['first_name']} {usuario['last_name']}".strip()
            if not nombre_completo:
                nombre_completo = usuario['username']
            usuarios_list.append({
                'id': usuario['id'],
                'nombre': nombre_completo
            })
        
        return JsonResponse({'usuarios': usuarios_list})
    
    def post(self, request, *args, **kwargs):
        """Cambiar responsable del legajo"""
        legajo_id = kwargs.get('pk')
        nuevo_responsable_id = request.POST.get('responsable_id')
        
        try:
            legajo = get_object_or_404(LegajoAtencion, pk=legajo_id)
            
            # Verificar permisos (solo administradores o el responsable actual)
            if not (request.user.groups.filter(name='Administrador').exists() or 
                   legajo.responsable == request.user):
                return JsonResponse({'success': False, 'error': 'No tiene permisos para cambiar el responsable'})
            
            from django.contrib.auth.models import User
            nuevo_responsable = get_object_or_404(User, pk=nuevo_responsable_id)
            
            # Verificar que el nuevo responsable tenga el rol adecuado
            if not nuevo_responsable.groups.filter(name='Ciudadanos').exists():
                return JsonResponse({'success': False, 'error': 'El usuario seleccionado no tiene el rol adecuado'})
            
            responsable_anterior = legajo.responsable
            legajo.responsable = nuevo_responsable
            legajo.save()
            
            # Registrar el cambio en las notas del legajo
            nota_cambio = f"Responsable cambiado de {responsable_anterior.get_full_name() or responsable_anterior.username} a {nuevo_responsable.get_full_name() or nuevo_responsable.username} por {request.user.get_full_name() or request.user.username}"
            if legajo.notas:
                legajo.notas += f"\n\n{nota_cambio}"
            else:
                legajo.notas = nota_cambio
            legajo.save()
            
            return JsonResponse({
                'success': True, 
                'nuevo_responsable': nuevo_responsable.get_full_name() or nuevo_responsable.username
            })
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


# Nuevas vistas de detalle tipo tabla

class EvaluacionListView(LoginRequiredMixin, TemplateView):
    """Vista de detalle para evaluaciones"""
    template_name = 'legajos/evaluacion_list.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['evaluacion'] = getattr(self.legajo, 'evaluacion', None)
        return context


class PlanListView(LoginRequiredMixin, ListView):
    """Vista de detalle para planes de intervención"""
    model = PlanIntervencion
    template_name = 'legajos/plan_list.html'
    context_object_name = 'planes'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return self.legajo.planes.select_related('profesional__usuario').order_by('-creado')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['plan_vigente'] = self.legajo.planes.filter(vigente=True).first()
        return context


class PlanUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar plan de intervención"""
    model = PlanIntervencion
    form_class = PlanIntervencionForm
    template_name = 'legajos/plan_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Plan de intervención actualizado exitosamente.')
        return reverse_lazy('legajos:planes', kwargs={'legajo_id': self.object.legajo.id})


class SeguimientoUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar seguimiento"""
    model = SeguimientoContacto
    form_class = SeguimientoForm
    template_name = 'legajos/seguimiento_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Seguimiento actualizado exitosamente.')
        return reverse_lazy('legajos:seguimientos', kwargs={'legajo_id': self.object.legajo.id})


class DerivacionUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar derivación"""
    model = Derivacion
    form_class = DerivacionForm
    template_name = 'legajos/derivacion_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['legajo'] = self.object.legajo
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Derivación actualizada exitosamente.')
        return reverse_lazy('legajos:derivaciones', kwargs={'legajo_id': self.object.legajo.id})


class EventoListView(LoginRequiredMixin, ListView):
    """Vista de detalle para eventos críticos"""
    model = EventoCritico
    template_name = 'legajos/evento_list.html'
    context_object_name = 'eventos'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = self.legajo.eventos.all()
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset.order_by('-creado')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        context['tipos'] = EventoCritico.TipoEvento.choices
        return context


class EventoUpdateView(LoginRequiredMixin, UpdateView):
    """Vista para editar evento crítico"""
    model = EventoCritico
    form_class = EventoCriticoForm
    template_name = 'legajos/evento_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.object.legajo
        context['editando'] = True
        return context
    
    def get_success_url(self):
        messages.success(self.request, 'Evento crítico actualizado exitosamente.')
        return reverse_lazy('legajos:eventos', kwargs={'legajo_id': self.object.legajo.id})


# Vistas de Legajos Institucionales
class LegajoInstitucionalListView(LoginRequiredMixin, ListView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_list.html'
    context_object_name = 'legajos_institucionales'
    paginate_by = 20
    
    def get_queryset(self):
        return LegajoInstitucional.objects.select_related('institucion', 'responsable_sedronar').order_by('-fecha_apertura')


class LegajoInstitucionalDetailView(LoginRequiredMixin, DetailView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_detail.html'
    context_object_name = 'legajo_institucional'


class LegajoInstitucionalCreateView(LoginRequiredMixin, CreateView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_form.html'
    fields = ['institucion', 'responsable_sedronar', 'observaciones']
    
    def get_initial(self):
        initial = super().get_initial()
        institucion_id = self.request.GET.get('institucion')
        if institucion_id:
            initial['institucion'] = institucion_id
        return initial
    
    def get_success_url(self):
        return reverse_lazy('legajos:legajo_institucional_detalle', kwargs={'pk': self.object.pk})


class LegajoInstitucionalUpdateView(LoginRequiredMixin, UpdateView):
    model = LegajoInstitucional
    template_name = 'legajos/legajo_institucional_form.html'
    fields = ['estado', 'responsable_sedronar', 'observaciones']
    
    def get_success_url(self):
        return reverse_lazy('legajos:legajo_institucional_detalle', kwargs={'pk': self.object.pk})


# Vistas de Instituciones
from core.models import Institucion
from configuracion.forms import InstitucionForm


class InstitucionListView(LoginRequiredMixin, ListView):
    model = Institucion
    template_name = 'configuracion/institucion_list.html'
    context_object_name = 'instituciones'
    paginate_by = 20
    
    def get_queryset(self):
        search = self.request.GET.get('search', '')
        
        if self.request.user.is_superuser:
            queryset = Institucion.objects.filter(activo=True).prefetch_related('encargados')
        else:
            queryset = Institucion.objects.filter(
                encargados=self.request.user,
                activo=True
            ).prefetch_related('encargados')
        
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(cuit__icontains=search)
            )
        
        return queryset.order_by('nombre')


class InstitucionCreateView(LoginRequiredMixin, CreateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('legajos:instituciones')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tiene permisos para crear instituciones.')
            return redirect('legajos:instituciones')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Institución {self.object.nombre} creada exitosamente')
        
        # Redirección forzada con timestamp para evitar cache del navegador
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class InstitucionUpdateView(LoginRequiredMixin, UpdateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('legajos:instituciones')
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.prefetch_related('encargados')
        else:
            return Institucion.objects.filter(encargados=self.request.user).prefetch_related('encargados')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Institución {self.object.nombre} actualizada exitosamente')
        
        # Redirección forzada con timestamp para evitar cache del navegador
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class InstitucionDeleteView(LoginRequiredMixin, DeleteView):
    model = Institucion
    template_name = 'configuracion/institucion_confirm_delete.html'
    success_url = reverse_lazy('legajos:instituciones')
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.prefetch_related('encargados')
        else:
            return Institucion.objects.filter(encargados=self.request.user).prefetch_related('encargados')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Eliminar legajos problemáticos asociados a ciudadanos falsos
        legajos_problematicos = LegajoAtencion.objects.filter(
            dispositivo=self.object,
            ciudadano__dni='00000000'
        )
        
        for legajo in legajos_problematicos:
            # Eliminar el ciudadano falso también
            ciudadano_falso = legajo.ciudadano
            legajo.delete()
            ciudadano_falso.delete()
        
        return super().delete(request, *args, **kwargs)


@require_http_methods(["POST"])
def marcar_etapa_plan(request, pk):
    """Vista AJAX para marcar/desmarcar etapa de plan como completada"""
    try:
        plan = get_object_or_404(PlanIntervencion, pk=pk)
        data = json.loads(request.body)
        indice = data.get('indice')
        completada = data.get('completada', False)
        
        if plan.actividades and 0 <= indice < len(plan.actividades):
            plan.actividades[indice]['completada'] = completada
            plan.save()
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Índice inválido'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def actividades_por_institucion(request, institucion_id):
    """API endpoint para obtener actividades de una institución"""
    from .models import PlanFortalecimiento
    
    actividades = PlanFortalecimiento.objects.filter(
        legajo_institucional__institucion_id=institucion_id,
        estado='ACTIVO'
    ).values('id', 'nombre', 'tipo')
    
    actividades_list = []
    for actividad in actividades:
        actividades_list.append({
            'id': actividad['id'],
            'nombre': actividad['nombre'],
            'tipo_display': dict(PlanFortalecimiento.TipoActividad.choices).get(actividad['tipo'], actividad['tipo'])
        })
    
    return JsonResponse({'actividades': actividades_list})


class InscribirActividadView(LoginRequiredMixin, CreateView):
    """Vista para inscribir ciudadano a actividad del centro"""
    model = InscriptoActividad
    form_class = InscribirActividadForm
    template_name = 'legajos/inscribir_actividad_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['legajo'] = self.legajo
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context
    
    def form_valid(self, form):
        form.instance.ciudadano = self.legajo.ciudadano
        response = super().form_valid(form)
        messages.success(self.request, f'Ciudadano inscrito exitosamente a {form.instance.actividad.nombre}')
        return response
    
    def get_success_url(self):
        return reverse_lazy('legajos:actividades_inscrito', kwargs={'legajo_id': self.legajo.id})


class ActividadesInscritoListView(LoginRequiredMixin, ListView):
    """Vista para listar actividades del ciudadano"""
    model = InscriptoActividad
    template_name = 'legajos/actividades_inscrito_list.html'
    context_object_name = 'inscripciones'
    paginate_by = 20
    
    def dispatch(self, request, *args, **kwargs):
        self.legajo = get_object_or_404(LegajoAtencion, id=kwargs['legajo_id'])
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return InscriptoActividad.objects.filter(
            ciudadano=self.legajo.ciudadano
        ).select_related(
            'actividad__legajo_institucional__institucion'
        ).order_by('-fecha_inscripcion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['legajo'] = self.legajo
        return context