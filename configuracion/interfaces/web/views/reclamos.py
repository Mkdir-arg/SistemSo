from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from core.mixins import GroupRequiredMixin, TimestampedSuccessUrlMixin
from reclamos.models import (
    Area,
    CampoDinamicoOpcion,
    CampoDinamicoReclamo,
    EstadoReclamo,
    EstadoReclamoTransicion,
    PrioridadReclamo,
    Reclamo,
    ReclamoAsignacion,
    ReclamoComentario,
    ReclamoHistorial,
    TipoReclamo,
)
from reclamos.services import (
    obtener_estado_inicial,
    obtener_prioridad_base,
    registrar_historial,
    validar_requisitos_runtime_reclamo,
    validar_transicion_estado_reclamo,
)

from ..forms import (
    AreaConfigForm,
    CampoDinamicoOpcionConfigForm,
    CampoDinamicoReclamoConfigForm,
    EstadoReclamoConfigForm,
    EstadoReclamoTransicionConfigForm,
    PrioridadReclamoConfigForm,
    ReclamoCambioEstadoForm,
    ReclamoConfigForm,
    ReclamoDerivacionForm,
    ReclamoSeguimientoForm,
    TipoReclamoConfigForm,
)


class ReclamoConfigListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Reclamo
    template_name = "configuracion/reclamo_list.html"
    context_object_name = "reclamos"
    paginate_by = 20
    required_groups = ["Administrador"]

    def get_queryset(self):
        queryset = (
            Reclamo.objects.select_related(
                "tipo_reclamo",
                "estado",
                "prioridad",
                "area_actual",
                "asignado_a",
            )
            .order_by("-fecha_ingreso", "-id")
        )
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda:
            queryset = queryset.filter(Q(numero__icontains=busqueda) | Q(titulo__icontains=busqueda))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["areas"] = Area.objects.filter(activo=True).order_by("orden", "nombre")
        return context


class ReclamoConfigCreateView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Reclamo
    form_class = ReclamoConfigForm
    template_name = "configuracion/reclamo_form.html"
    success_url = reverse_lazy("configuracion:reclamos_listado")
    required_groups = ["Administrador"]

    def get_initial(self):
        initial = super().get_initial()
        area_actual = self.request.GET.get("area")
        if area_actual and area_actual.isdigit():
            initial["area_actual"] = int(area_actual)
        return initial

    @transaction.atomic
    def form_valid(self, form):
        reclamo = form.save(commit=False)
        tipo_reclamo = reclamo.tipo_reclamo
        municipio = reclamo.municipio

        if not reclamo.estado:
            reclamo.estado = obtener_estado_inicial(municipio=municipio)
        if not reclamo.prioridad:
            reclamo.prioridad = (
                tipo_reclamo.prioridad_default if tipo_reclamo and tipo_reclamo.prioridad_default else None
            ) or obtener_prioridad_base(municipio=municipio)
        if not reclamo.area_actual and tipo_reclamo:
            reclamo.area_actual = tipo_reclamo.area
        if not reclamo.area_responsable and reclamo.area_actual:
            reclamo.area_responsable = reclamo.area_actual
        if not reclamo.fecha_ingreso:
            reclamo.fecha_ingreso = timezone.now()
        if not reclamo.sla_horas and tipo_reclamo and tipo_reclamo.sla_horas:
            reclamo.sla_horas = tipo_reclamo.sla_horas

        if not reclamo.estado:
            form.add_error("estado", "No hay un estado inicial activo configurado.")
            return self.form_invalid(form)
        if not reclamo.prioridad:
            form.add_error("prioridad", "No hay una prioridad base activa configurada.")
            return self.form_invalid(form)
        if not reclamo.area_actual:
            form.add_error("area_actual", "Debe seleccionar un area o definirla en el tipo de reclamo.")
            return self.form_invalid(form)

        if self.request.user.is_authenticated:
            reclamo.creado_por = self.request.user
            reclamo.actualizado_por = self.request.user

        reclamo.save()
        form.save_m2m()

        registrar_historial(
            reclamo=reclamo,
            accion="creacion",
            usuario=self.request.user,
            estado_nuevo=reclamo.estado,
            area_nueva=reclamo.area_actual,
            asignado_nuevo=reclamo.asignado_a,
            visible_ciudadano=True,
            metadata={"origen": reclamo.origen, "ui": "configuracion"},
        )

        messages.success(self.request, f"Reclamo {reclamo.numero} creado correctamente.")
        return self.redirect_with_timestamp()


class ReclamoConfigDetailView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, DetailView):
    model = Reclamo
    template_name = "configuracion/reclamo_detail.html"
    context_object_name = "reclamo"
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Reclamo.objects.select_related(
            "tipo_reclamo",
            "estado",
            "prioridad",
            "area_actual",
            "area_responsable",
            "municipio",
            "asignado_a",
            "creado_por",
            "actualizado_por",
            "ciudadano",
        )

    def get_success_url(self):
        return reverse("configuracion:reclamo_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("estado_form", ReclamoCambioEstadoForm())
        context.setdefault("derivacion_form", ReclamoDerivacionForm())
        context.setdefault("seguimiento_form", ReclamoSeguimientoForm())
        context["historial_items"] = (
            ReclamoHistorial.objects.filter(reclamo=self.object)
            .select_related(
                "usuario",
                "estado_anterior",
                "estado_nuevo",
                "area_anterior",
                "area_nueva",
                "asignado_anterior",
                "asignado_nuevo",
            )
            .order_by("-fecha", "-id")[:100]
        )
        context["comentarios_items"] = (
            ReclamoComentario.objects.filter(reclamo=self.object)
            .select_related("usuario", "ciudadano")
            .order_by("-created_at", "-id")[:100]
        )
        context["asignaciones_items"] = (
            ReclamoAsignacion.objects.filter(reclamo=self.object)
            .select_related("area", "usuario", "asignado_por")
            .order_by("-fecha_asignacion", "-id")[:100]
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        accion = request.POST.get("accion", "").strip()

        if accion == "cambiar_estado":
            return self._post_cambiar_estado(request)
        if accion == "derivar":
            return self._post_derivar(request)
        if accion == "seguimiento":
            return self._post_seguimiento(request)

        messages.error(request, "Accion no valida.")
        return self.redirect_with_timestamp()

    @transaction.atomic
    def _post_cambiar_estado(self, request):
        form = ReclamoCambioEstadoForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(estado_form=form))

        estado_nuevo = form.cleaned_data["estado_nuevo"]
        comentario = form.cleaned_data["comentario"].strip()
        estado_anterior = self.object.estado

        if estado_nuevo == estado_anterior:
            messages.info(request, "El reclamo ya se encuentra en ese estado.")
            return self.redirect_with_timestamp()

        try:
            validar_transicion_estado_reclamo(
                reclamo=self.object,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                usuario=request.user,
                comentario=comentario,
                area_actual=self.object.area_actual,
                asignado_a=self.object.asignado_a,
                area_responsable=self.object.area_responsable,
            )
            validar_requisitos_runtime_reclamo(
                reclamo=self.object,
                tipo_reclamo=self.object.tipo_reclamo,
                estado_objetivo=estado_nuevo,
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.render_to_response(self.get_context_data(estado_form=form))

        self.object.estado = estado_nuevo
        self.object.actualizado_por = request.user
        self.object.save()

        registrar_historial(
            reclamo=self.object,
            accion="cambio_estado",
            usuario=request.user,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            area_nueva=self.object.area_actual,
            asignado_nuevo=self.object.asignado_a,
            comentario=comentario,
            visible_ciudadano=not bool(comentario),
            metadata={"ui": "configuracion"},
        )
        messages.success(request, "Estado actualizado correctamente.")
        return self.redirect_with_timestamp()

    @transaction.atomic
    def _post_derivar(self, request):
        form = ReclamoDerivacionForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(derivacion_form=form))

        area_nueva = form.cleaned_data["area"]
        usuario_nuevo = form.cleaned_data["usuario"]
        motivo = form.cleaned_data["motivo"].strip()

        area_anterior = self.object.area_actual
        asignado_anterior = self.object.asignado_a

        ReclamoAsignacion.objects.filter(reclamo=self.object, activa=True).update(activa=False, fecha_fin=timezone.now())
        ReclamoAsignacion.objects.create(
            reclamo=self.object,
            area=area_nueva,
            usuario=usuario_nuevo,
            motivo=motivo,
            asignado_por=request.user,
            activa=True,
        )

        self.object.area_actual = area_nueva
        self.object.area_responsable = area_nueva
        self.object.asignado_a = usuario_nuevo
        self.object.actualizado_por = request.user
        self.object.save()

        registrar_historial(
            reclamo=self.object,
            accion="derivacion",
            usuario=request.user,
            area_anterior=area_anterior,
            area_nueva=area_nueva,
            asignado_anterior=asignado_anterior,
            asignado_nuevo=usuario_nuevo,
            estado_nuevo=self.object.estado,
            comentario=motivo,
            visible_ciudadano=False,
            metadata={"ui": "configuracion"},
        )
        messages.success(request, "Reclamo derivado correctamente.")
        return self.redirect_with_timestamp()

    @transaction.atomic
    def _post_seguimiento(self, request):
        form = ReclamoSeguimientoForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(seguimiento_form=form))

        comentario = form.cleaned_data["comentario"].strip()
        es_interno = form.cleaned_data["es_interno"]
        visible_ciudadano = form.cleaned_data["visible_ciudadano"]

        ReclamoComentario.objects.create(
            reclamo=self.object,
            usuario=request.user if request.user.is_authenticated else None,
            comentario=comentario,
            es_interno=es_interno,
            visible_ciudadano=visible_ciudadano,
        )

        registrar_historial(
            reclamo=self.object,
            accion="seguimiento",
            usuario=request.user,
            estado_nuevo=self.object.estado,
            area_nueva=self.object.area_actual,
            asignado_nuevo=self.object.asignado_a,
            comentario=comentario,
            visible_ciudadano=visible_ciudadano,
            metadata={"ui": "configuracion", "es_interno": es_interno},
        )
        messages.success(request, "Seguimiento registrado correctamente.")
        return self.redirect_with_timestamp()


class ReclamoCatalogosConfigView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = "configuracion/reclamo_catalogos.html"
    required_groups = ["Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["catalogos"] = [
            {
                "nombre": "Areas",
                "descripcion": "Sectores que reciben y gestionan reclamos.",
                "url_name": "configuracion:reclamos_areas",
                "icono": "fa-building",
            },
            {
                "nombre": "Tipos de Reclamo",
                "descripcion": "Clasificacion operativa y reglas base por tipo.",
                "url_name": "configuracion:reclamos_tipos",
                "icono": "fa-list",
            },
            {
                "nombre": "Estados",
                "descripcion": "Estados del ciclo de vida del reclamo.",
                "url_name": "configuracion:reclamos_estados",
                "icono": "fa-stream",
            },
            {
                "nombre": "Prioridades",
                "descripcion": "Niveles de urgencia y atencion.",
                "url_name": "configuracion:reclamos_prioridades",
                "icono": "fa-flag",
            },
            {
                "nombre": "Transiciones de Estado",
                "descripcion": "Reglas de cambio de estado con permisos por rol y area.",
                "url_name": "configuracion:reclamos_transiciones_estado",
                "icono": "fa-random",
            },
            {
                "nombre": "Campos Dinamicos",
                "descripcion": "Definicion de campos dinamicos por tipo de reclamo.",
                "url_name": "configuracion:reclamos_campos_dinamicos",
                "icono": "fa-wpforms",
            },
            {
                "nombre": "Opciones de Campo",
                "descripcion": "Opciones para campos dinamicos tipo seleccion.",
                "url_name": "configuracion:reclamos_campos_opciones",
                "icono": "fa-list-ul",
            },
        ]
        return context


class _ReclamoCatalogoBaseView(LoginRequiredMixin, GroupRequiredMixin):
    required_groups = ["Administrador"]


class ReclamoCatalogoListBaseView(_ReclamoCatalogoBaseView, ListView):
    template_name = "configuracion/reclamo_catalogo_list.html"
    context_object_name = "items"
    page_title = ""
    create_url_name = ""
    edit_url_name = ""
    delete_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["create_url_name"] = self.create_url_name
        context["edit_url_name"] = self.edit_url_name
        context["delete_url_name"] = self.delete_url_name
        context["back_url"] = reverse_lazy("configuracion:reclamos_configuracion")
        return context


class ReclamoCatalogoCreateBaseView(_ReclamoCatalogoBaseView, TimestampedSuccessUrlMixin, CreateView):
    template_name = "configuracion/reclamo_catalogo_form.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_url"] = self.success_url
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class ReclamoCatalogoUpdateBaseView(_ReclamoCatalogoBaseView, TimestampedSuccessUrlMixin, UpdateView):
    template_name = "configuracion/reclamo_catalogo_form.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_url"] = self.success_url
        return context

    def form_valid(self, form):
        super().form_valid(form)
        return self.redirect_with_timestamp()


class ReclamoCatalogoDeleteBaseView(_ReclamoCatalogoBaseView, DeleteView):
    template_name = "configuracion/reclamo_catalogo_confirm_delete.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_url"] = self.success_url
        return context


class AreaReclamoListView(ReclamoCatalogoListBaseView):
    model = Area
    page_title = "Areas de Reclamo"
    create_url_name = "configuracion:reclamos_areas_crear"
    edit_url_name = "configuracion:reclamos_areas_editar"
    delete_url_name = "configuracion:reclamos_areas_eliminar"


class AreaReclamoCreateView(ReclamoCatalogoCreateBaseView):
    model = Area
    form_class = AreaConfigForm
    page_title = "Nueva Area de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_areas")


class AreaReclamoUpdateView(ReclamoCatalogoUpdateBaseView):
    model = Area
    form_class = AreaConfigForm
    page_title = "Editar Area de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_areas")


class AreaReclamoDeleteView(ReclamoCatalogoDeleteBaseView):
    model = Area
    page_title = "Eliminar Area de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_areas")


class TipoReclamoListView(ReclamoCatalogoListBaseView):
    model = TipoReclamo
    page_title = "Tipos de Reclamo"
    create_url_name = "configuracion:reclamos_tipos_crear"
    edit_url_name = "configuracion:reclamos_tipos_editar"
    delete_url_name = "configuracion:reclamos_tipos_eliminar"


class TipoReclamoCreateView(ReclamoCatalogoCreateBaseView):
    model = TipoReclamo
    form_class = TipoReclamoConfigForm
    page_title = "Nuevo Tipo de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_tipos")


class TipoReclamoUpdateView(ReclamoCatalogoUpdateBaseView):
    model = TipoReclamo
    form_class = TipoReclamoConfigForm
    page_title = "Editar Tipo de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_tipos")


class TipoReclamoDeleteView(ReclamoCatalogoDeleteBaseView):
    model = TipoReclamo
    page_title = "Eliminar Tipo de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_tipos")


class EstadoReclamoListView(ReclamoCatalogoListBaseView):
    model = EstadoReclamo
    page_title = "Estados de Reclamo"
    create_url_name = "configuracion:reclamos_estados_crear"
    edit_url_name = "configuracion:reclamos_estados_editar"
    delete_url_name = "configuracion:reclamos_estados_eliminar"


class EstadoReclamoCreateView(ReclamoCatalogoCreateBaseView):
    model = EstadoReclamo
    form_class = EstadoReclamoConfigForm
    page_title = "Nuevo Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_estados")


class EstadoReclamoUpdateView(ReclamoCatalogoUpdateBaseView):
    model = EstadoReclamo
    form_class = EstadoReclamoConfigForm
    page_title = "Editar Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_estados")


class EstadoReclamoDeleteView(ReclamoCatalogoDeleteBaseView):
    model = EstadoReclamo
    page_title = "Eliminar Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_estados")


class PrioridadReclamoListView(ReclamoCatalogoListBaseView):
    model = PrioridadReclamo
    page_title = "Prioridades de Reclamo"
    create_url_name = "configuracion:reclamos_prioridades_crear"
    edit_url_name = "configuracion:reclamos_prioridades_editar"
    delete_url_name = "configuracion:reclamos_prioridades_eliminar"


class PrioridadReclamoCreateView(ReclamoCatalogoCreateBaseView):
    model = PrioridadReclamo
    form_class = PrioridadReclamoConfigForm
    page_title = "Nueva Prioridad de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_prioridades")


class PrioridadReclamoUpdateView(ReclamoCatalogoUpdateBaseView):
    model = PrioridadReclamo
    form_class = PrioridadReclamoConfigForm
    page_title = "Editar Prioridad de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_prioridades")


class PrioridadReclamoDeleteView(ReclamoCatalogoDeleteBaseView):
    model = PrioridadReclamo
    page_title = "Eliminar Prioridad de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_prioridades")


class EstadoReclamoTransicionListView(ReclamoCatalogoListBaseView):
    model = EstadoReclamoTransicion
    page_title = "Transiciones de Estado de Reclamo"
    create_url_name = "configuracion:reclamos_transiciones_estado_crear"
    edit_url_name = "configuracion:reclamos_transiciones_estado_editar"
    delete_url_name = "configuracion:reclamos_transiciones_estado_eliminar"


class EstadoReclamoTransicionCreateView(ReclamoCatalogoCreateBaseView):
    model = EstadoReclamoTransicion
    form_class = EstadoReclamoTransicionConfigForm
    page_title = "Nueva Transicion de Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_transiciones_estado")


class EstadoReclamoTransicionUpdateView(ReclamoCatalogoUpdateBaseView):
    model = EstadoReclamoTransicion
    form_class = EstadoReclamoTransicionConfigForm
    page_title = "Editar Transicion de Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_transiciones_estado")


class EstadoReclamoTransicionDeleteView(ReclamoCatalogoDeleteBaseView):
    model = EstadoReclamoTransicion
    page_title = "Eliminar Transicion de Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_transiciones_estado")


class CampoDinamicoReclamoListView(ReclamoCatalogoListBaseView):
    model = CampoDinamicoReclamo
    page_title = "Campos Dinamicos de Reclamo"
    create_url_name = "configuracion:reclamos_campos_dinamicos_crear"
    edit_url_name = "configuracion:reclamos_campos_dinamicos_editar"
    delete_url_name = "configuracion:reclamos_campos_dinamicos_eliminar"


class CampoDinamicoReclamoCreateView(ReclamoCatalogoCreateBaseView):
    model = CampoDinamicoReclamo
    form_class = CampoDinamicoReclamoConfigForm
    page_title = "Nuevo Campo Dinamico de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_campos_dinamicos")


class CampoDinamicoReclamoUpdateView(ReclamoCatalogoUpdateBaseView):
    model = CampoDinamicoReclamo
    form_class = CampoDinamicoReclamoConfigForm
    page_title = "Editar Campo Dinamico de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_campos_dinamicos")


class CampoDinamicoReclamoDeleteView(ReclamoCatalogoDeleteBaseView):
    model = CampoDinamicoReclamo
    page_title = "Eliminar Campo Dinamico de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_campos_dinamicos")


class CampoDinamicoOpcionListView(ReclamoCatalogoListBaseView):
    model = CampoDinamicoOpcion
    page_title = "Opciones de Campo Dinamico"
    create_url_name = "configuracion:reclamos_campos_opciones_crear"
    edit_url_name = "configuracion:reclamos_campos_opciones_editar"
    delete_url_name = "configuracion:reclamos_campos_opciones_eliminar"


class CampoDinamicoOpcionCreateView(ReclamoCatalogoCreateBaseView):
    model = CampoDinamicoOpcion
    form_class = CampoDinamicoOpcionConfigForm
    page_title = "Nueva Opcion de Campo Dinamico"
    success_url = reverse_lazy("configuracion:reclamos_campos_opciones")


class CampoDinamicoOpcionUpdateView(ReclamoCatalogoUpdateBaseView):
    model = CampoDinamicoOpcion
    form_class = CampoDinamicoOpcionConfigForm
    page_title = "Editar Opcion de Campo Dinamico"
    success_url = reverse_lazy("configuracion:reclamos_campos_opciones")


class CampoDinamicoOpcionDeleteView(ReclamoCatalogoDeleteBaseView):
    model = CampoDinamicoOpcion
    page_title = "Eliminar Opcion de Campo Dinamico"
    success_url = reverse_lazy("configuracion:reclamos_campos_opciones")
