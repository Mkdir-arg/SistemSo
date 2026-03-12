from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.models import Institucion, Localidad, Municipio, Provincia
from legajos.models import (
    Derivacion,
    EvaluacionInstitucional,
    IndicadorInstitucional,
    PersonalInstitucion,
    PlanFortalecimiento,
    StaffActividad,
)

from .forms import (
    ActividadEditarForm,
    DerivacionRechazoForm,
    InscriptoEstadoForm,
    InstitucionForm,
    LocalidadForm,
    MunicipioForm,
    PersonalInstitucionForm,
    PlanFortalecimientoForm,
    ProvinciaForm,
    StaffActividadForm,
)
from .selectors_instituciones import (
    build_actividad_detail_context,
    build_institucion_detail_context,
    get_instituciones_queryset_for_user,
    search_personal_for_actividad,
)
from .services_actividades import (
    ConfiguracionInstitucionalService,
    ConfiguracionWorkflowError,
)
from .views_extra import (
    AsistenciaView,
    StaffDesasignarView,
    StaffEditarView,
    TomarAsistenciaView,
)

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
        return get_instituciones_queryset_for_user(
            self.request.user,
            search=self.request.GET.get('search', ''),
        )


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
        ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        context.update(build_institucion_detail_context(institucion))
        return context




class PersonalInstitucionCreateView(LoginRequiredMixin, CreateView):
    model = PersonalInstitucion
    fields = ['nombre', 'apellido', 'dni', 'tipo', 'titulo_profesional', 'matricula', 'activo']
    template_name = 'configuracion/personal_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class EvaluacionInstitucionCreateView(LoginRequiredMixin, CreateView):
    model = EvaluacionInstitucional
    fields = ['fecha_evaluacion', 'observaciones']
    template_name = 'configuracion/evaluacion_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class PlanFortalecimientoCreateView(LoginRequiredMixin, CreateView):
    model = PlanFortalecimiento
    form_class = PlanFortalecimientoForm
    template_name = 'configuracion/plan_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class IndicadorInstitucionCreateView(LoginRequiredMixin, CreateView):
    model = IndicadorInstitucional
    fields = ['periodo', 'observaciones']
    template_name = 'configuracion/indicador_form.html'
    
    def form_valid(self, form):
        institucion = get_object_or_404(Institucion, pk=self.kwargs['institucion_pk'])
        form.instance.legajo_institucional = (
            ConfiguracionInstitucionalService.ensure_legajo_institucional(institucion)
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('configuracion:institucion_detalle', kwargs={'pk': self.kwargs['institucion_pk']})


class ActividadDetailView(LoginRequiredMixin, DetailView):
    model = PlanFortalecimiento
    template_name = 'configuracion/actividad_detail.html'
    context_object_name = 'actividad'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_actividad_detail_context(self.get_object()))
        return context


class StaffActividadCreateView(LoginRequiredMixin, CreateView):
    model = StaffActividad
    template_name = 'configuracion/staff_form.html'
    
    def get_form_class(self):
        return StaffActividadForm
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        actividad = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        kwargs['legajo_institucional'] = actividad.legajo_institucional
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('personal_form', PersonalInstitucionForm())
        context['actividad'] = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        return context
    
    def post(self, request, *args, **kwargs):
        actividad = get_object_or_404(PlanFortalecimiento, pk=self.kwargs['actividad_pk'])
        self.object = None
        staff_form = StaffActividadForm(request.POST, legajo_institucional=actividad.legajo_institucional)
        personal_form = PersonalInstitucionForm(request.POST)

        if staff_form.is_valid():
            tipo_asignacion = staff_form.cleaned_data['tipo_asignacion']
            if tipo_asignacion == 'nuevo' and not personal_form.is_valid():
                context = self.get_context_data(form=staff_form, personal_form=personal_form)
                return self.render_to_response(context)

            try:
                staff, usuario_creado = ConfiguracionInstitucionalService.assign_staff_to_actividad(
                    actividad,
                    rol_en_actividad=staff_form.cleaned_data['rol_en_actividad'],
                    activo=staff_form.cleaned_data['activo'],
                    usuario=request.user,
                    personal=staff_form.cleaned_data.get('personal'),
                    personal_data=(
                        personal_form.cleaned_data
                        if tipo_asignacion == 'nuevo'
                        else None
                    ),
                )
            except (ConfiguracionWorkflowError, ValidationError) as exc:
                target_form = personal_form if tipo_asignacion == 'nuevo' else staff_form
                target_form.add_error(None, str(exc))
                context = self.get_context_data(form=staff_form, personal_form=personal_form)
                return self.render_to_response(context)

            if usuario_creado:
                messages.success(
                    request,
                    (
                        f"Personal {staff.personal.nombre} {staff.personal.apellido} creado y asignado. "
                        f"Usuario: {usuario_creado.username} (password: {staff.personal.dni})"
                    ),
                )
            else:
                messages.success(
                    request,
                    f'Personal {staff.personal.nombre} {staff.personal.apellido} asignado correctamente',
                )
            return redirect('configuracion:actividad_detalle', pk=actividad.pk)

        context = self.get_context_data()
        context['form'] = staff_form
        context['personal_form'] = personal_form
        return self.render_to_response(context)


class DerivacionAceptarView(LoginRequiredMixin, UpdateView):
    model = None
    
    def post(self, request, *args, **kwargs):
        try:
            derivacion, _ = ConfiguracionInstitucionalService.aceptar_derivacion(
                kwargs['pk'],
                request.user,
            )
        except ConfiguracionWorkflowError as exc:
            derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
            messages.error(request, str(exc))
            return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)

        messages.success(
            request,
            'Derivación aceptada. Ciudadano inscrito en la actividad.',
        )
        return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)


class DerivacionRechazarView(LoginRequiredMixin, UpdateView):
    model = None
    
    def post(self, request, *args, **kwargs):
        form = DerivacionRechazoForm(request.POST)
        if not form.is_valid():
            messages.error(request, 'No se pudo rechazar la derivación.')
            derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
            return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)

        try:
            derivacion = ConfiguracionInstitucionalService.rechazar_derivacion(
                kwargs['pk'],
                request.user,
                form.cleaned_data['motivo'],
            )
        except ConfiguracionWorkflowError as exc:
            derivacion = get_object_or_404(Derivacion, pk=kwargs['pk'])
            messages.error(request, str(exc))
            return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)

        messages.success(request, 'Derivación rechazada correctamente.')
        return redirect('configuracion:actividad_detalle', pk=derivacion.actividad_destino.pk)


class InscriptoEditarView(LoginRequiredMixin, UpdateView):
    model = None
    form_class = InscriptoEstadoForm
    template_name = 'configuracion/inscripto_form.html'
    
    def get_object(self):
        from legajos.models import InscriptoActividad
        return get_object_or_404(InscriptoActividad, pk=self.kwargs['pk'])
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['inscripto'] = self.get_object()
        return context

    def get_form(self, form_class=None):
        return self.form_class(instance=self.get_object(), **self.get_form_kwargs())
    
    def post(self, request, *args, **kwargs):
        inscripto = self.get_object()
        form = self.form_class(request.POST, instance=inscripto)
        if not form.is_valid():
            return self.render_to_response(
                self.get_context_data(form=form, inscripto=inscripto)
            )

        changed = ConfiguracionInstitucionalService.update_inscripto_estado(
            inscripto,
            estado=form.cleaned_data['estado'],
            observaciones=form.cleaned_data['observaciones'],
            usuario=request.user,
        )
        if changed:
            messages.success(
                request,
                f'Estado del inscripto actualizado a {inscripto.get_estado_display()}',
            )
        return redirect('configuracion:actividad_detalle', pk=inscripto.actividad.pk)


class ActividadEditarView(LoginRequiredMixin, UpdateView):
    model = PlanFortalecimiento
    form_class = ActividadEditarForm
    template_name = 'configuracion/actividad_editar_form.html'
    
    def form_valid(self, form):
        self.object = form.instance
        cambios = ConfiguracionInstitucionalService.update_actividad(
            self.object,
            form.cleaned_data,
            self.request.user,
        )
        if cambios:
            messages.success(self.request, 'Actividad actualizada correctamente')
        return redirect(self.get_success_url())
    
    def get_success_url(self):
        return reverse_lazy('configuracion:actividad_detalle', kwargs={'pk': self.object.pk})


def buscar_personal_ajax(request, actividad_pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'No autorizado'}, status=401)
    
    actividad = get_object_or_404(PlanFortalecimiento, pk=actividad_pk)
    query = request.GET.get('q', '').strip()
    
    personal = search_personal_for_actividad(actividad, query=query)
    resultados = [{
        'id': p.id,
        'text': f"{p.apellido}, {p.nombre} - DNI: {p.dni}"
    } for p in personal]
    
    return JsonResponse({'results': resultados})


def documento_subir(request, pk):
    from django.contrib import messages
    if request.method == 'POST':
        messages.info(request, 'La funcionalidad de documentos estará disponible próximamente')
    return redirect('configuracion:institucion_detalle', pk=pk)
