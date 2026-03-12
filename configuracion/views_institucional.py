from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import TimestampedSuccessUrlMixin
from core.models import Institucion
from legajos.models import (
    EvaluacionInstitucional,
    IndicadorInstitucional,
    PersonalInstitucion,
    PlanFortalecimiento,
)

from .forms import InstitucionForm, PlanFortalecimientoForm
from .selectors_instituciones import build_institucion_detail_context, get_instituciones_queryset_for_user
from .services_actividades import ConfiguracionInstitucionalService


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


DispositivoListView = InstitucionListView
DispositivoRed = Institucion
DispositivoForm = InstitucionForm


class InstitucionCreateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('configuracion:instituciones')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'No tiene permisos para crear instituciones.')
            return redirect('configuracion:instituciones')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        messages.success(self.request, f'Institución {self.object.nombre} creada exitosamente')
        return self.redirect_with_timestamp()


DispositivoCreateView = InstitucionCreateView


class InstitucionUpdateView(LoginRequiredMixin, UpdateView):
    model = Institucion
    form_class = InstitucionForm
    template_name = 'configuracion/institucion_form.html'
    success_url = reverse_lazy('configuracion:instituciones')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')
        return Institucion.objects.filter(encargados=self.request.user).select_related(
            'provincia',
            'municipio',
            'localidad',
        ).prefetch_related('encargados')


DispositivoUpdateView = InstitucionUpdateView


class InstitucionDeleteView(LoginRequiredMixin, DeleteView):
    model = Institucion
    template_name = 'configuracion/institucion_confirm_delete.html'
    success_url = reverse_lazy('configuracion:instituciones')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Institucion.objects.select_related('provincia', 'municipio', 'localidad').prefetch_related('encargados')
        return Institucion.objects.filter(encargados=self.request.user).select_related(
            'provincia',
            'municipio',
            'localidad',
        ).prefetch_related('encargados')


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


def documento_subir(request, pk):
    if request.method == 'POST':
        messages.info(request, 'La funcionalidad de documentos estará disponible próximamente')
    return redirect('configuracion:institucion_detalle', pk=pk)
