from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from core.models import Provincia, Municipio, Localidad, Institucion
from legajos.models import LegajoInstitucional, PersonalInstitucion, EvaluacionInstitucional, PlanFortalecimiento, IndicadorInstitucional, StaffActividad
from .forms import ProvinciaForm, MunicipioForm, LocalidadForm, InstitucionForm, PlanFortalecimientoForm
from .views_extra import InscriptoEditarView, ActividadEditarView, StaffEditarView, StaffDesasignarView, AsistenciaView, TomarAsistenciaView

# Alias para compatibilidad
DispositivoRed = Institucion
DispositivoForm = InstitucionForm


class ProvinciaListView(LoginRequiredMixin, ListView):
    model = Provincia
    template_name = 'configuracion/provincia_list.html'
    context_object_name = 'provincias'
    paginate_by = 20


class ProvinciaCreateView(LoginRequiredMixin, CreateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'configuracion/provincia_form.html'
    success_url = reverse_lazy('configuracion:provincias')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class ProvinciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'configuracion/provincia_form.html'
    success_url = reverse_lazy('configuracion:provincias')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class ProvinciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Provincia
    template_name = 'configuracion/provincia_confirm_delete.html'
    success_url = reverse_lazy('configuracion:provincias')


class MunicipioListView(LoginRequiredMixin, ListView):
    model = Municipio
    template_name = 'configuracion/municipio_list.html'
    context_object_name = 'municipios'
    paginate_by = 20


class MunicipioCreateView(LoginRequiredMixin, CreateView):
    model = Municipio
    form_class = MunicipioForm
    template_name = 'configuracion/municipio_form.html'
    success_url = reverse_lazy('configuracion:municipios')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class MunicipioUpdateView(LoginRequiredMixin, UpdateView):
    model = Municipio
    form_class = MunicipioForm
    template_name = 'configuracion/municipio_form.html'
    success_url = reverse_lazy('configuracion:municipios')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class MunicipioDeleteView(LoginRequiredMixin, DeleteView):
    model = Municipio
    template_name = 'configuracion/municipio_confirm_delete.html'
    success_url = reverse_lazy('configuracion:municipios')


class LocalidadListView(LoginRequiredMixin, ListView):
    model = Localidad
    template_name = 'configuracion/localidad_list.html'
    context_object_name = 'localidades'
    paginate_by = 20


class LocalidadCreateView(LoginRequiredMixin, CreateView):
    model = Localidad
    form_class = LocalidadForm
    template_name = 'configuracion/localidad_form.html'
    success_url = reverse_lazy('configuracion:localidades')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class LocalidadUpdateView(LoginRequiredMixin, UpdateView):
    model = Localidad
    form_class = LocalidadForm
    template_name = 'configuracion/localidad_form.html'
    success_url = reverse_lazy('configuracion:localidades')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


class LocalidadDeleteView(LoginRequiredMixin, DeleteView):
    model = Localidad
    template_name = 'configuracion/localidad_confirm_delete.html'
    success_url = reverse_lazy('configuracion:localidades')


class InstitucionListView(LoginRequiredMixin, ListView):
    model = Institucion
    template_name = 'configuracion/institucion_list.html'
    context_object_name = 'instituciones'
    paginate_by = 20
    
    def get_queryset(self):
        from django.db.models import Q
        search = self.request.GET.get('search', '')
        
        if self.request.user.is_superuser:
            queryset = Institucion.objects.filter(
                estado_registro='APROBADO'
            ).select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')
        else:
            queryset = Institucion.objects.filter(
                encargados=self.request.user,
                estado_registro='APROBADO'
            ).select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')
        
        if search:
            queryset = queryset.filter(
                Q(nombre__icontains=search) |
                Q(cuit__icontains=search)
            )
        
        return queryset.order_by('nombre')


# Alias para compatibilidad
DispositivoListView = InstitucionListView


class InstitucionCreateView(LoginRequiredMixin, CreateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('configuracion:instituciones')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            from django.contrib import messages
            messages.error(request, 'No tiene permisos para crear instituciones.')
            return redirect('configuracion:instituciones')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        from django.contrib import messages
        response = super().form_valid(form)
        messages.success(self.request, f'Institución {self.object.nombre} creada exitosamente')
        import time
        return redirect(f"{self.success_url}?t={int(time.time())}")


# Alias para compatibilidad
DispositivoCreateView = InstitucionCreateView


class InstitucionUpdateView(LoginRequiredMixin, UpdateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('configuracion:instituciones')
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')
        else:
            return Institucion.objects.filter(encargados=self.request.user).select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')


# Alias para compatibilidad
DispositivoUpdateView = InstitucionUpdateView


class InstitucionDeleteView(LoginRequiredMixin, DeleteView):
    model = Institucion
    template_name = 'configuracion/institucion_confirm_delete.html'
    success_url = reverse_lazy('configuracion:instituciones')
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')
        else:
            return Institucion.objects.filter(encargados=self.request.user).select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')


class InstitucionDetailView(LoginRequiredMixin, DetailView):
    model = Institucion
    template_name = 'configuracion/institucion_detail.html'
    context_object_name = 'institucion'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        institucion = self.get_object()
        
        # Obtener o crear legajo institucional
        legajo, created = LegajoInstitucional.objects.get_or_create(
            institucion=institucion,
            defaults={'estado_global': 'ACTIVO'}
        )
        
        context['legajo'] = legajo
        
        # Generar solapas dinámicas
        solapas = []
        
        # Solapa estática: Resumen
        solapas.append({
            'id': 'resumen',
            'nombre': 'Resumen',
            'icono': 'dashboard',
            'color': None,
            'estatica': True,
            'orden': 0
        })
        
        # Solapas estáticas adicionales
        solapas.append({
            'id': 'personal',
            'nombre': 'Personal',
            'icono': 'people',
            'color': None,
            'estatica': True,
            'orden': 10
        })
        
        solapas.append({
            'id': 'evaluaciones',
            'nombre': 'Evaluaciones',
            'icono': 'assessment',
            'color': None,
            'estatica': True,
            'orden': 20
        })
        
        solapas.append({
            'id': 'documentos',
            'nombre': 'Documentos',
            'icono': 'folder',
            'color': None,
            'estatica': True,
            'orden': 30
        })
        
        # Solapas dinámicas por programa
        from legajos.models_institucional import InstitucionPrograma, ProgramaInstitucional, DerivacionInstitucional, CasoInstitucional
        programas_activos = InstitucionPrograma.objects.filter(
            institucion=institucion,
            activo=True
        ).select_related('programa').order_by('programa__orden')
        
        for ip in programas_activos:
            programa = ip.programa
            
            # Contar derivaciones pendientes
            derivaciones_pendientes = DerivacionInstitucional.objects.filter(
                institucion_programa=ip,
                estado='PENDIENTE'
            ).count()
            
            # Contar casos activos
            casos_activos = CasoInstitucional.objects.filter(
                institucion_programa=ip,
                estado__in=['ACTIVO', 'EN_SEGUIMIENTO']
            ).count()
            
            solapas.append({
                'id': f'programa_{programa.tipo}',
                'nombre': programa.nombre,
                'icono': programa.icono,
                'color': programa.color,
                'estatica': False,
                'orden': 100 + programa.orden,
                'institucion_programa_id': ip.id,
                'badge_derivaciones': derivaciones_pendientes,
                'badge_casos': casos_activos,
            })
        
        # Ordenar solapas
        solapas.sort(key=lambda x: x['orden'])
        
        context['solapas'] = solapas
        context['personal'] = PersonalInstitucion.objects.filter(legajo_institucional=legajo).select_related('legajo_institucional')
        context['evaluaciones'] = EvaluacionInstitucional.objects.filter(legajo_institucional=legajo).select_related('evaluador').order_by('-fecha_evaluacion')
        context['planes'] = PlanFortalecimiento.objects.filter(legajo_institucional=legajo).prefetch_related('staff__personal').order_by('-fecha_inicio')
        context['indicadores'] = IndicadorInstitucional.objects.filter(legajo_institucional=legajo).select_related('legajo_institucional').order_by('-periodo')
        
        # Métricas consolidadas
        context['total_programas_activos'] = programas_activos.count()
        context['total_derivaciones_pendientes'] = sum(s.get('badge_derivaciones', 0) for s in solapas if not s['estatica'])
        context['total_casos_activos'] = sum(s.get('badge_casos', 0) for s in solapas if not s['estatica'])
        
        return context




class PersonalInstitucionCreateView(LoginRequiredMixin, CreateView):
    model = PersonalInstitucion
    fields = ['nombre', 'apellido', 'dni', 'tipo', 'titulo_profesional', 'matricula', 'activo']
    template_name = 'configuracion/personal_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        legajo, created = LegajoInstitucional.objects.get_or_create(
            institucion=institucion,
            defaults={'estado': 'ACTIVO'}
        )
        form.instance.legajo_institucional = legajo
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class EvaluacionInstitucionCreateView(LoginRequiredMixin, CreateView):
    model = EvaluacionInstitucional
    fields = ['fecha_evaluacion', 'observaciones']
    template_name = 'configuracion/evaluacion_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        legajo, created = LegajoInstitucional.objects.get_or_create(
            institucion=institucion,
            defaults={'estado': 'ACTIVO'}
        )
        form.instance.legajo_institucional = legajo
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class PlanFortalecimientoCreateView(LoginRequiredMixin, CreateView):
    model = PlanFortalecimiento
    form_class = PlanFortalecimientoForm
    template_name = 'configuracion/plan_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        legajo, created = LegajoInstitucional.objects.get_or_create(
            institucion=institucion,
            defaults={'estado': 'ACTIVO'}
        )
        form.instance.legajo_institucional = legajo
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class IndicadorInstitucionCreateView(LoginRequiredMixin, CreateView):
    model = IndicadorInstitucional
    fields = ['periodo', 'observaciones']
    template_name = 'configuracion/indicador_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        legajo, created = LegajoInstitucional.objects.get_or_create(
            institucion=institucion,
            defaults={'estado': 'ACTIVO'}
        )
        form.instance.legajo_institucional = legajo
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class ActividadDetailView(LoginRequiredMixin, DetailView):
    model = PlanFortalecimiento
    template_name = 'configuracion/actividad_detail.html'
    context_object_name = 'actividad'
    
    def get_context_data(self, **kwargs):
        from django.db.models import Count, Q
        context = super().get_context_data(**kwargs)
        actividad = self.get_object()
        
        # Obtener staff de la actividad
        context['staff'] = StaffActividad.objects.filter(actividad=actividad).select_related('personal', 'actividad')
        
        # Obtener derivaciones a esta actividad (solo pendientes y rechazadas)
        from legajos.models import Derivacion, InscriptoActividad, RegistroAsistencia
        context['derivaciones'] = Derivacion.objects.filter(actividad_destino=actividad).exclude(estado='ACEPTADA').select_related('legajo__ciudadano', 'destino').order_by('-creado')
        
        # Obtener nómina de la actividad (inscritos) con contadores de asistencia
        nomina = InscriptoActividad.objects.filter(actividad=actividad).select_related('ciudadano', 'actividad').annotate(
            cantidad_presentes=Count('asistencias', filter=Q(asistencias__estado='PRESENTE')),
            cantidad_ausentes=Count('asistencias', filter=Q(asistencias__estado='AUSENTE'))
        ).order_by('-fecha_inscripcion')
        
        context['nomina'] = nomina
        
        return context


class StaffActividadCreateView(LoginRequiredMixin, CreateView):
    model = StaffActividad
    template_name = 'configuracion/staff_form.html'
    
    def get_form_class(self):
        from .forms import StaffActividadForm
        return StaffActividadForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        actividad = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        kwargs['legajo_institucional'] = actividad.legajo_institucional
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .forms import PersonalInstitucionForm
        context['personal_form'] = PersonalInstitucionForm()
        context['actividad'] = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        return context
    
    def post(self, request, *args, **kwargs):
        from .forms import StaffActividadForm, PersonalInstitucionForm
        from legajos.models import HistorialStaff
        from django.contrib import messages
        import logging
        
        logger = logging.getLogger(__name__)
        actividad = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        
        staff_form = StaffActividadForm(request.POST, legajo_institucional=actividad.legajo_institucional)
        personal_form = PersonalInstitucionForm(request.POST)
        
        logger.info(f"POST data: {request.POST}")
        logger.info(f"Staff form valid: {staff_form.is_valid()}")
        if not staff_form.is_valid():
            logger.error(f"Staff form errors: {staff_form.errors}")
        
        if staff_form.is_valid():
            tipo_asignacion = staff_form.cleaned_data.get('tipo_asignacion')
            logger.info(f"Tipo asignacion: {tipo_asignacion}")
            
            if tipo_asignacion == 'nuevo':
                logger.info(f"Personal form valid: {personal_form.is_valid()}")
                if not personal_form.is_valid():
                    logger.error(f"Personal form errors: {personal_form.errors}")
                
                if personal_form.is_valid():
                    personal = personal_form.save(commit=False)
                    personal.legajo_institucional = actividad.legajo_institucional
                    personal.activo = True
                    personal.save()
                    
                    # Crear usuario del sistema
                    usuario_creado = personal.crear_usuario()
                    
                    staff = staff_form.save(commit=False)
                    staff.actividad = actividad
                    staff.personal = personal
                    staff.save()
                    
                    HistorialStaff.objects.create(
                        staff=staff,
                        accion='ASIGNACION',
                        usuario=request.user,
                        descripcion=f'{personal.nombre} {personal.apellido} creado y asignado como {staff.rol_en_actividad}'
                    )
                    
                    messages.success(request, f'Personal {personal.nombre} {personal.apellido} creado y asignado. Usuario: {usuario_creado.username} (password: {personal.dni})')
                    return redirect('configuracion:actividad_detalle', pk=actividad.pk)
            else:
                if staff_form.cleaned_data.get('personal'):
                    staff = staff_form.save(commit=False)
                    staff.actividad = actividad
                    staff.save()
                    
                    HistorialStaff.objects.create(
                        staff=staff,
                        accion='ASIGNACION',
                        usuario=request.user,
                        descripcion=f'{staff.personal.nombre} {staff.personal.apellido} asignado como {staff.rol_en_actividad}'
                    )
                    
                    messages.success(request, f'Personal {staff.personal.nombre} {staff.personal.apellido} asignado correctamente')
                    return redirect('configuracion:actividad_detalle', pk=actividad.pk)
        
        context = self.get_context_data()
        context['form'] = staff_form
        context['personal_form'] = personal_form
        return self.render_to_response(context)


class DerivacionAceptarView(LoginRequiredMixin, UpdateView):
    model = None
    
    def post(self, request, *args, **kwargs):
        from legajos.models import Derivacion, HistorialDerivacion, InscriptoActividad
        from django.utils import timezone
        from django.contrib import messages
        
        derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
        actividad = derivacion.actividad_destino
        
        # Validar cupo disponible
        inscritos_activos = InscriptoActividad.objects.filter(
            actividad=actividad,
            estado__in=['INSCRITO', 'ACTIVO']
        ).count()
        
        if inscritos_activos >= actividad.cupo_ciudadanos:
            messages.error(request, f'No se puede aceptar la derivación. Cupo completo ({actividad.cupo_ciudadanos} lugares)')
            return redirect('configuracion:actividad_detalle', pk=actividad.pk)
        
        estado_anterior = derivacion.estado
        derivacion.estado = 'ACEPTADA'
        derivacion.fecha_aceptacion = timezone.now().date()
        derivacion.save()
        
        # Inscribir automáticamente al ciudadano en la actividad
        InscriptoActividad.objects.get_or_create(
            actividad=actividad,
            ciudadano=derivacion.legajo.ciudadano,
            defaults={'estado': 'ACTIVO'}
        )
        
        HistorialDerivacion.objects.create(
            derivacion=derivacion,
            accion='ACEPTACION',
            usuario=request.user,
            descripcion=f'Derivación aceptada por {request.user.username}',
            estado_anterior=estado_anterior
        )
        
        messages.success(request, f'Derivación aceptada. Ciudadano inscrito en la actividad.')
        return redirect('configuracion:actividad_detalle', pk=actividad.pk)


class DerivacionRechazarView(LoginRequiredMixin, UpdateView):
    model = None
    
    def post(self, request, *args, **kwargs):
        from legajos.models import Derivacion, HistorialDerivacion
        derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
        estado_anterior = derivacion.estado
        motivo = request.POST.get('motivo', 'Rechazada')
        derivacion.estado = 'RECHAZADA'
        derivacion.respuesta = motivo
        derivacion.save()
        
        HistorialDerivacion.objects.create(
            derivacion=derivacion,
            accion='RECHAZO',
            usuario=request.user,
            descripcion=f'Derivación rechazada por {request.user.username}: {motivo}',
            estado_anterior=estado_anterior
        )
        
        return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)


class InscriptoEditarView(LoginRequiredMixin, UpdateView):
    model = None
    fields = ['estado', 'observaciones']
    template_name = 'configuracion/inscripto_form.html'
    
    def get_object(self):
        from legajos.models import InscriptoActividad
        return get_object_or_404(InscriptoActividad, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscripto'] = self.get_object()
        return context
    
    def post(self, request, *args, **kwargs):
        from legajos.models import InscriptoActividad, HistorialInscripto
        from django.utils import timezone
        from django.contrib import messages
        
        inscripto = self.get_object()
        nuevo_estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones', '')
        
        if nuevo_estado and nuevo_estado != inscripto.estado:
            estado_anterior = inscripto.estado
            inscripto.estado = nuevo_estado
            
            if nuevo_estado in ['FINALIZADO', 'ABANDONADO']:
                inscripto.fecha_finalizacion = timezone.now().date()
            
            inscripto.observaciones = observaciones
            inscripto.save()
            
            # Registrar en historial
            accion_map = {
                'FINALIZADO': 'FINALIZACION',
                'ABANDONADO': 'ABANDONO',
                'ACTIVO': 'ACTIVACION'
            }
            
            HistorialInscripto.objects.create(
                inscripto=inscripto,
                accion=accion_map.get(nuevo_estado, 'INSCRIPCION'),
                usuario=request.user,
                descripcion=f'Estado cambiado a {inscripto.get_estado_display()}. {observaciones}',
                estado_anterior=estado_anterior
            )
            
            messages.success(request, f'Estado del inscripto actualizado a {inscripto.get_estado_display()}')
        
        return redirect('configuracion:actividad_detalle', pk=inscripto.actividad.pk)


class ActividadEditarView(LoginRequiredMixin, UpdateView):
    model = PlanFortalecimiento
    fields = ['nombre', 'descripcion', 'cupo_ciudadanos', 'fecha_inicio', 'fecha_fin', 'estado']
    template_name = 'configuracion/actividad_editar_form.html'
    
    def form_valid(self, form):
        from legajos.models import HistorialActividad
        from django.contrib import messages
        
        # Obtener datos anteriores
        actividad_anterior = PlanFortalecimiento.objects.get(pk=self.object.pk)
        cambios = []
        
        if actividad_anterior.nombre != form.cleaned_data['nombre']:
            cambios.append(f"Nombre: '{actividad_anterior.nombre}' → '{form.cleaned_data['nombre']}'")
        if actividad_anterior.cupo_ciudadanos != form.cleaned_data['cupo_ciudadanos']:
            cambios.append(f"Cupo: {actividad_anterior.cupo_ciudadanos} → {form.cleaned_data['cupo_ciudadanos']}")
        if actividad_anterior.estado != form.cleaned_data['estado']:
            cambios.append(f"Estado: {actividad_anterior.get_estado_display()} → {form.instance.get_estado_display()}")
        
        response = super().form_valid(form)
        
        if cambios:
            accion = 'SUSPENSION' if form.cleaned_data['estado'] == 'SUSPENDIDO' else \
                    'FINALIZACION' if form.cleaned_data['estado'] == 'FINALIZADO' else 'MODIFICACION'
            
            HistorialActividad.objects.create(
                actividad=self.object,
                accion=accion,
                usuario=self.request.user,
                descripcion=f"Actividad modificada: {'; '.join(cambios)}"
            )
            
            messages.success(self.request, 'Actividad actualizada correctamente')
        
        return response
    
    def get_success_url(self):
        return reverse_lazy('configuracion:actividad_detalle', kwargs={'pk': self.object.pk})


def buscar_personal_ajax(request, actividad_pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    actividad = get_object_or_404(PlanFortalecimiento, pk=actividad_pk)
    query = request.GET.get('q', '').strip()
    
    personal = PersonalInstitucion.objects.filter(
        legajo_institucional=actividad.legajo_institucional,
        activo=True
    )
    
    if query:
        personal = personal.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(dni__icontains=query)
        )
    
    resultados = [{
        'id': p.id,
        'text': f"{p.apellido}, {p.nombre} - DNI: {p.dni}"
    } for p in personal.order_by('apellido', 'nombre')]
    
    return JsonResponse({'results': resultados})


