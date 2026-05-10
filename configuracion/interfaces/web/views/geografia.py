from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from core.mixins import GroupRequiredMixin, TimestampedSuccessUrlMixin
from core.models import Localidad, Municipio, Provincia
from reclamos.models import Area

from configuracion.interfaces.web.forms import (
    AreaRaizConfigForm,
    LocalidadForm,
    MunicipioForm,
    ProvinciaForm,
    SubareaConfigForm,
)


class ProvinciaListView(LoginRequiredMixin, ListView):
    model = Provincia
    template_name = 'configuracion/provincia_list.html'
    context_object_name = 'provincias'
    paginate_by = 20


class ProvinciaCreateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'configuracion/provincia_form.html'
    success_url = reverse_lazy('configuracion:provincias')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class ProvinciaUpdateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Provincia
    form_class = ProvinciaForm
    template_name = 'configuracion/provincia_form.html'
    success_url = reverse_lazy('configuracion:provincias')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class ProvinciaDeleteView(LoginRequiredMixin, DeleteView):
    model = Provincia
    template_name = 'configuracion/provincia_confirm_delete.html'
    success_url = reverse_lazy('configuracion:provincias')


class MunicipioListView(LoginRequiredMixin, ListView):
    model = Municipio
    template_name = 'configuracion/municipio_list.html'
    context_object_name = 'municipios'
    paginate_by = 20


class MunicipioCreateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Municipio
    form_class = MunicipioForm
    template_name = 'configuracion/municipio_form.html'
    success_url = reverse_lazy('configuracion:municipios')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class MunicipioUpdateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Municipio
    form_class = MunicipioForm
    template_name = 'configuracion/municipio_form.html'
    success_url = reverse_lazy('configuracion:municipios')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class MunicipioDeleteView(LoginRequiredMixin, DeleteView):
    model = Municipio
    template_name = 'configuracion/municipio_confirm_delete.html'
    success_url = reverse_lazy('configuracion:municipios')


class LocalidadListView(LoginRequiredMixin, ListView):
    model = Localidad
    template_name = 'configuracion/localidad_list.html'
    context_object_name = 'localidades'
    paginate_by = 20


class LocalidadCreateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Localidad
    form_class = LocalidadForm
    template_name = 'configuracion/localidad_form.html'
    success_url = reverse_lazy('configuracion:localidades')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class LocalidadUpdateView(LoginRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Localidad
    form_class = LocalidadForm
    template_name = 'configuracion/localidad_form.html'
    success_url = reverse_lazy('configuracion:localidades')

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class LocalidadDeleteView(LoginRequiredMixin, DeleteView):
    model = Localidad
    template_name = 'configuracion/localidad_confirm_delete.html'
    success_url = reverse_lazy('configuracion:localidades')


class AreaConfigListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Area
    template_name = "configuracion/area_raiz_list.html"
    context_object_name = "items"
    required_groups = ["Administrador"]

    def get_queryset(self):
        queryset = Area.objects.filter(parent__isnull=True).order_by("orden", "nombre", "id")
        activo = self.request.GET.get("activo", "").strip()
        if activo in {"1", "0"}:
            queryset = queryset.filter(activo=(activo == "1"))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Areas"
        context["create_url_name"] = "configuracion:areas_crear"
        context["edit_url_name"] = "configuracion:areas_editar"
        context["delete_url_name"] = "configuracion:areas_eliminar"
        context["subareas_url"] = reverse_lazy("configuracion:subareas")
        context["back_url"] = reverse_lazy("configuracion:provincias")
        context["filtro_activo"] = self.request.GET.get("activo", "").strip()
        return context


class AreaConfigCreateView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Area
    form_class = AreaRaizConfigForm
    template_name = "configuracion/area_form.html"
    success_url = reverse_lazy("configuracion:areas")
    required_groups = ["Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nueva Area"
        context["back_url"] = self.success_url
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class AreaConfigUpdateView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Area
    form_class = AreaRaizConfigForm
    template_name = "configuracion/area_form.html"
    success_url = reverse_lazy("configuracion:areas")
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Area.objects.filter(parent__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar Area"
        context["back_url"] = self.success_url
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class AreaConfigDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Area
    template_name = "configuracion/reclamo_catalogo_confirm_delete.html"
    success_url = reverse_lazy("configuracion:areas")
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Area.objects.filter(parent__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Eliminar Area"
        context["back_url"] = self.success_url
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save(update_fields=["activo", "updated_at"])
        messages.success(request, "Area inactivada correctamente.")
        return HttpResponseRedirect(str(self.success_url))


class AreaConfigDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Area
    template_name = "configuracion/area_detail.html"
    context_object_name = "item"
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Area.objects.filter(parent__isnull=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detail_rows = []
        for field in self.object._meta.fields:
            raw_value = getattr(self.object, field.name, None)
            if field.is_relation:
                value = str(raw_value) if raw_value else "-"
            elif raw_value in ("", None):
                value = "-"
            else:
                value = raw_value
            detail_rows.append({"label": field.verbose_name, "value": value})
        context["detail_rows"] = detail_rows
        context["page_title"] = "Detalle de Area"
        context["back_url"] = reverse_lazy("configuracion:areas")
        return context


class SubareaConfigListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Area
    template_name = "configuracion/subarea_list.html"
    context_object_name = "items"
    required_groups = ["Administrador"]

    def get_queryset(self):
        queryset = Area.objects.filter(parent__isnull=False).select_related("parent").order_by(
            "parent__nombre", "orden", "nombre", "id"
        )
        activo = self.request.GET.get("activo", "").strip()
        if activo in {"1", "0"}:
            queryset = queryset.filter(activo=(activo == "1"))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filtro_activo"] = self.request.GET.get("activo", "").strip()
        return context


class SubareaConfigCreateView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Area
    form_class = SubareaConfigForm
    template_name = "configuracion/subarea_form.html"
    success_url = reverse_lazy("configuracion:subareas")
    required_groups = ["Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Nueva Subarea"
        context["back_url"] = self.success_url
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class SubareaConfigUpdateView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, UpdateView):
    model = Area
    form_class = SubareaConfigForm
    template_name = "configuracion/subarea_form.html"
    success_url = reverse_lazy("configuracion:subareas")
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Area.objects.filter(parent__isnull=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Editar Subarea"
        context["back_url"] = self.success_url
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class SubareaConfigDeleteView(LoginRequiredMixin, GroupRequiredMixin, DeleteView):
    model = Area
    template_name = "configuracion/reclamo_catalogo_confirm_delete.html"
    success_url = reverse_lazy("configuracion:subareas")
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Area.objects.filter(parent__isnull=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Eliminar Subarea"
        context["back_url"] = self.success_url
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.activo = False
        self.object.save(update_fields=["activo", "updated_at"])
        messages.success(request, "Subarea inactivada correctamente.")
        return HttpResponseRedirect(str(self.success_url))


class SubareaConfigDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = Area
    template_name = "configuracion/subarea_detail.html"
    context_object_name = "item"
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Area.objects.filter(parent__isnull=False).select_related("parent")
