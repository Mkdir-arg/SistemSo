from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView, UpdateView

from core.mixins import GroupRequiredMixin, TimestampedSuccessUrlMixin
from reclamos.models import Area
from tramites.models import (
    CampoDinamicoOpcion,
    CampoDinamicoTramite,
    EstadoTramite,
    EstadoTramiteTransicion,
    PrioridadTramite,
    RequisitoTramite,
    TipoTramite,
    Tramite,
    TramiteAsignacion,
    TramiteComentario,
    TramiteHistorial,
)
from tramites.services import (
    obtener_estado_inicial,
    obtener_prioridad_base,
    registrar_historial,
    validar_requisitos_runtime_tramite,
    validar_transicion_estado_tramite,
)

from ..forms import (
    AreaTramiteConfigForm,
    CampoDinamicoOpcionConfigForm,
    CampoDinamicoTramiteConfigForm,
    EstadoTramiteConfigForm,
    EstadoTramiteTransicionConfigForm,
    PrioridadTramiteConfigForm,
    RequisitoTramiteConfigForm,
    TipoTramiteConfigForm,
    TramiteCambioEstadoForm,
    TramiteConfigForm,
    TramiteDerivacionForm,
    TramiteSeguimientoForm,
)


class TramiteConfigListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Tramite
    template_name = "configuracion/tramite_list.html"
    context_object_name = "tramites"
    paginate_by = 20
    required_groups = ["Administrador"]

    def get_queryset(self):
        queryset = (
            Tramite.objects.select_related(
                "tipo_tramite",
                "estado",
                "prioridad",
                "area_actual",
                "asignado_a",
            )
            .order_by("-fecha_inicio", "-id")
        )
        busqueda = self.request.GET.get("q", "").strip()
        if busqueda:
            queryset = queryset.filter(Q(numero__icontains=busqueda) | Q(titulo__icontains=busqueda))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        return context


class TramiteConfigCreateView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, CreateView):
    model = Tramite
    form_class = TramiteConfigForm
    template_name = "configuracion/tramite_form.html"
    success_url = reverse_lazy("configuracion:tramites_listado")
    required_groups = ["Administrador"]

    @transaction.atomic
    def form_valid(self, form):
        tramite = form.save(commit=False)
        tipo_tramite = tramite.tipo_tramite
        municipio = tramite.municipio

        if not tramite.estado:
            tramite.estado = obtener_estado_inicial(municipio=municipio)
        if not tramite.prioridad:
            tramite.prioridad = (
                tipo_tramite.prioridad_default if tipo_tramite and tipo_tramite.prioridad_default else None
            ) or obtener_prioridad_base(municipio=municipio)
        if not tramite.area_actual and tipo_tramite:
            tramite.area_actual = tipo_tramite.area
        if not tramite.area_responsable and tramite.area_actual:
            tramite.area_responsable = tramite.area_actual
        if not tramite.fecha_inicio:
            tramite.fecha_inicio = timezone.now()
        if not tramite.sla_horas and tipo_tramite and tipo_tramite.sla_horas:
            tramite.sla_horas = tipo_tramite.sla_horas

        if not tramite.estado:
            form.add_error("estado", "No hay un estado inicial activo configurado.")
            return self.form_invalid(form)
        if not tramite.prioridad:
            form.add_error("prioridad", "No hay una prioridad base activa configurada.")
            return self.form_invalid(form)
        if not tramite.area_actual:
            form.add_error("area_actual", "Debe seleccionar un area o definirla en el tipo de tramite.")
            return self.form_invalid(form)

        if self.request.user.is_authenticated:
            tramite.creado_por = self.request.user
            tramite.actualizado_por = self.request.user

        tramite.save()
        form.save_m2m()

        registrar_historial(
            tramite=tramite,
            accion="creacion",
            usuario=self.request.user,
            estado_nuevo=tramite.estado,
            area_nueva=tramite.area_actual,
            asignado_nuevo=tramite.asignado_a,
            visible_ciudadano=True,
            metadata={"origen": tramite.origen, "ui": "configuracion"},
        )

        messages.success(self.request, f"Tramite {tramite.numero} creado correctamente.")
        return self.redirect_with_timestamp()


class TramiteConfigDetailView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin, DetailView):
    model = Tramite
    template_name = "configuracion/tramite_detail.html"
    context_object_name = "tramite"
    required_groups = ["Administrador"]

    def get_queryset(self):
        return Tramite.objects.select_related(
            "tipo_tramite",
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
        return reverse("configuracion:tramite_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("estado_form", TramiteCambioEstadoForm())
        context.setdefault("derivacion_form", TramiteDerivacionForm())
        context.setdefault("seguimiento_form", TramiteSeguimientoForm())
        context["historial_items"] = (
            TramiteHistorial.objects.filter(tramite=self.object)
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
            TramiteComentario.objects.filter(tramite=self.object)
            .select_related("usuario", "ciudadano")
            .order_by("-created_at", "-id")[:100]
        )
        context["asignaciones_items"] = (
            TramiteAsignacion.objects.filter(tramite=self.object)
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
        form = TramiteCambioEstadoForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(estado_form=form))

        estado_nuevo = form.cleaned_data["estado_nuevo"]
        comentario = form.cleaned_data["comentario"].strip()
        estado_anterior = self.object.estado

        if estado_nuevo == estado_anterior:
            messages.info(request, "El tramite ya se encuentra en ese estado.")
            return self.redirect_with_timestamp()

        try:
            validar_transicion_estado_tramite(
                tramite=self.object,
                estado_anterior=estado_anterior,
                estado_nuevo=estado_nuevo,
                usuario=request.user,
                comentario=comentario,
                area_actual=self.object.area_actual,
                asignado_a=self.object.asignado_a,
                area_responsable=self.object.area_responsable,
            )
            validar_requisitos_runtime_tramite(
                tramite=self.object,
                tipo_tramite=self.object.tipo_tramite,
                estado_objetivo=estado_nuevo,
            )
        except ValueError as exc:
            form.add_error(None, str(exc))
            return self.render_to_response(self.get_context_data(estado_form=form))

        self.object.estado = estado_nuevo
        self.object.actualizado_por = request.user
        self.object.save()

        registrar_historial(
            tramite=self.object,
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
        form = TramiteDerivacionForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(derivacion_form=form))

        area_nueva = form.cleaned_data["area"]
        usuario_nuevo = form.cleaned_data["usuario"]
        motivo = form.cleaned_data["motivo"].strip()

        area_anterior = self.object.area_actual
        asignado_anterior = self.object.asignado_a

        TramiteAsignacion.objects.filter(tramite=self.object, activa=True).update(activa=False, fecha_fin=timezone.now())
        TramiteAsignacion.objects.create(
            tramite=self.object,
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
            tramite=self.object,
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
        messages.success(request, "Tramite derivado correctamente.")
        return self.redirect_with_timestamp()

    @transaction.atomic
    def _post_seguimiento(self, request):
        form = TramiteSeguimientoForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(seguimiento_form=form))

        comentario = form.cleaned_data["comentario"].strip()
        es_interno = form.cleaned_data["es_interno"]
        visible_ciudadano = form.cleaned_data["visible_ciudadano"]

        TramiteComentario.objects.create(
            tramite=self.object,
            usuario=request.user if request.user.is_authenticated else None,
            comentario=comentario,
            es_interno=es_interno,
            visible_ciudadano=visible_ciudadano,
        )

        registrar_historial(
            tramite=self.object,
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


class TramiteCatalogosConfigView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = "configuracion/tramite_catalogos.html"
    required_groups = ["Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["catalogos"] = [
            {
                "nombre": "Areas",
                "descripcion": "Areas operativas para derivacion de tramites.",
                "url_name": "configuracion:tramites_areas",
                "icono": "fa-building",
            },
            {
                "nombre": "Tipos de Tramite",
                "descripcion": "Catalogo principal de tramites disponibles.",
                "url_name": "configuracion:tramites_tipos",
                "icono": "fa-list",
            },
            {
                "nombre": "Estados",
                "descripcion": "Estados posibles del circuito del tramite.",
                "url_name": "configuracion:tramites_estados",
                "icono": "fa-stream",
            },
            {
                "nombre": "Prioridades",
                "descripcion": "Niveles de prioridad para atencion operativa.",
                "url_name": "configuracion:tramites_prioridades",
                "icono": "fa-flag",
            },
            {
                "nombre": "Transiciones de Estado",
                "descripcion": "Reglas de cambio de estado con permisos por rol y area.",
                "url_name": "configuracion:tramites_transiciones_estado",
                "icono": "fa-random",
            },
            {
                "nombre": "Requisitos",
                "descripcion": "Requisitos por tipo de tramite.",
                "url_name": "configuracion:tramites_requisitos",
                "icono": "fa-check-square",
            },
            {
                "nombre": "Campos Dinamicos",
                "descripcion": "Definicion de campos dinamicos por tipo de tramite.",
                "url_name": "configuracion:tramites_campos_dinamicos",
                "icono": "fa-wpforms",
            },
            {
                "nombre": "Opciones de Campo",
                "descripcion": "Opciones para campos dinamicos tipo seleccion.",
                "url_name": "configuracion:tramites_campos_opciones",
                "icono": "fa-list-ul",
            },
        ]
        return context


class _TramiteCatalogoBaseView(LoginRequiredMixin, GroupRequiredMixin):
    required_groups = ["Administrador"]


class TramiteCatalogoListBaseView(_TramiteCatalogoBaseView, ListView):
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
        context["back_url"] = reverse_lazy("configuracion:tramites_configuracion")
        return context


class TramiteCatalogoCreateBaseView(_TramiteCatalogoBaseView, TimestampedSuccessUrlMixin, CreateView):
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


class TramiteCatalogoUpdateBaseView(_TramiteCatalogoBaseView, TimestampedSuccessUrlMixin, UpdateView):
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


class TramiteCatalogoDeleteBaseView(_TramiteCatalogoBaseView, DeleteView):
    template_name = "configuracion/reclamo_catalogo_confirm_delete.html"
    page_title = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_url"] = self.success_url
        return context


class AreaTramiteListView(TramiteCatalogoListBaseView):
    model = Area
    page_title = "Areas de Tramite"
    create_url_name = "configuracion:tramites_areas_crear"
    edit_url_name = "configuracion:tramites_areas_editar"
    delete_url_name = "configuracion:tramites_areas_eliminar"


class AreaTramiteCreateView(TramiteCatalogoCreateBaseView):
    model = Area
    form_class = AreaTramiteConfigForm
    page_title = "Nueva Area de Tramite"
    success_url = reverse_lazy("configuracion:tramites_areas")


class AreaTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = Area
    form_class = AreaTramiteConfigForm
    page_title = "Editar Area de Tramite"
    success_url = reverse_lazy("configuracion:tramites_areas")


class AreaTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = Area
    page_title = "Eliminar Area de Tramite"
    success_url = reverse_lazy("configuracion:tramites_areas")


class TipoTramiteListView(TramiteCatalogoListBaseView):
    model = TipoTramite
    page_title = "Tipos de Tramite"
    create_url_name = "configuracion:tramites_tipos_crear"
    edit_url_name = "configuracion:tramites_tipos_editar"
    delete_url_name = "configuracion:tramites_tipos_eliminar"


class TipoTramiteCreateView(TramiteCatalogoCreateBaseView):
    model = TipoTramite
    form_class = TipoTramiteConfigForm
    page_title = "Nuevo Tipo de Tramite"
    success_url = reverse_lazy("configuracion:tramites_tipos")


class TipoTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = TipoTramite
    form_class = TipoTramiteConfigForm
    page_title = "Editar Tipo de Tramite"
    success_url = reverse_lazy("configuracion:tramites_tipos")


class TipoTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = TipoTramite
    page_title = "Eliminar Tipo de Tramite"
    success_url = reverse_lazy("configuracion:tramites_tipos")


class EstadoTramiteListView(TramiteCatalogoListBaseView):
    model = EstadoTramite
    page_title = "Estados de Tramite"
    create_url_name = "configuracion:tramites_estados_crear"
    edit_url_name = "configuracion:tramites_estados_editar"
    delete_url_name = "configuracion:tramites_estados_eliminar"


class EstadoTramiteCreateView(TramiteCatalogoCreateBaseView):
    model = EstadoTramite
    form_class = EstadoTramiteConfigForm
    page_title = "Nuevo Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_estados")


class EstadoTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = EstadoTramite
    form_class = EstadoTramiteConfigForm
    page_title = "Editar Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_estados")


class EstadoTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = EstadoTramite
    page_title = "Eliminar Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_estados")


class PrioridadTramiteListView(TramiteCatalogoListBaseView):
    model = PrioridadTramite
    page_title = "Prioridades de Tramite"
    create_url_name = "configuracion:tramites_prioridades_crear"
    edit_url_name = "configuracion:tramites_prioridades_editar"
    delete_url_name = "configuracion:tramites_prioridades_eliminar"


class PrioridadTramiteCreateView(TramiteCatalogoCreateBaseView):
    model = PrioridadTramite
    form_class = PrioridadTramiteConfigForm
    page_title = "Nueva Prioridad de Tramite"
    success_url = reverse_lazy("configuracion:tramites_prioridades")


class PrioridadTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = PrioridadTramite
    form_class = PrioridadTramiteConfigForm
    page_title = "Editar Prioridad de Tramite"
    success_url = reverse_lazy("configuracion:tramites_prioridades")


class PrioridadTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = PrioridadTramite
    page_title = "Eliminar Prioridad de Tramite"
    success_url = reverse_lazy("configuracion:tramites_prioridades")


class EstadoTramiteTransicionListView(TramiteCatalogoListBaseView):
    model = EstadoTramiteTransicion
    page_title = "Transiciones de Estado de Tramite"
    create_url_name = "configuracion:tramites_transiciones_estado_crear"
    edit_url_name = "configuracion:tramites_transiciones_estado_editar"
    delete_url_name = "configuracion:tramites_transiciones_estado_eliminar"


class EstadoTramiteTransicionCreateView(TramiteCatalogoCreateBaseView):
    model = EstadoTramiteTransicion
    form_class = EstadoTramiteTransicionConfigForm
    page_title = "Nueva Transicion de Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_transiciones_estado")


class EstadoTramiteTransicionUpdateView(TramiteCatalogoUpdateBaseView):
    model = EstadoTramiteTransicion
    form_class = EstadoTramiteTransicionConfigForm
    page_title = "Editar Transicion de Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_transiciones_estado")


class EstadoTramiteTransicionDeleteView(TramiteCatalogoDeleteBaseView):
    model = EstadoTramiteTransicion
    page_title = "Eliminar Transicion de Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_transiciones_estado")


class RequisitoTramiteListView(TramiteCatalogoListBaseView):
    model = RequisitoTramite
    page_title = "Requisitos de Tramite"
    create_url_name = "configuracion:tramites_requisitos_crear"
    edit_url_name = "configuracion:tramites_requisitos_editar"
    delete_url_name = "configuracion:tramites_requisitos_eliminar"


class RequisitoTramiteCreateView(TramiteCatalogoCreateBaseView):
    model = RequisitoTramite
    form_class = RequisitoTramiteConfigForm
    page_title = "Nuevo Requisito de Tramite"
    success_url = reverse_lazy("configuracion:tramites_requisitos")


class RequisitoTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = RequisitoTramite
    form_class = RequisitoTramiteConfigForm
    page_title = "Editar Requisito de Tramite"
    success_url = reverse_lazy("configuracion:tramites_requisitos")


class RequisitoTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = RequisitoTramite
    page_title = "Eliminar Requisito de Tramite"
    success_url = reverse_lazy("configuracion:tramites_requisitos")


class CampoDinamicoTramiteListView(TramiteCatalogoListBaseView):
    model = CampoDinamicoTramite
    page_title = "Campos Dinamicos de Tramite"
    create_url_name = "configuracion:tramites_campos_dinamicos_crear"
    edit_url_name = "configuracion:tramites_campos_dinamicos_editar"
    delete_url_name = "configuracion:tramites_campos_dinamicos_eliminar"


class CampoDinamicoTramiteCreateView(TramiteCatalogoCreateBaseView):
    model = CampoDinamicoTramite
    form_class = CampoDinamicoTramiteConfigForm
    page_title = "Nuevo Campo Dinamico de Tramite"
    success_url = reverse_lazy("configuracion:tramites_campos_dinamicos")


class CampoDinamicoTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = CampoDinamicoTramite
    form_class = CampoDinamicoTramiteConfigForm
    page_title = "Editar Campo Dinamico de Tramite"
    success_url = reverse_lazy("configuracion:tramites_campos_dinamicos")


class CampoDinamicoTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = CampoDinamicoTramite
    page_title = "Eliminar Campo Dinamico de Tramite"
    success_url = reverse_lazy("configuracion:tramites_campos_dinamicos")


class CampoDinamicoOpcionListView(TramiteCatalogoListBaseView):
    model = CampoDinamicoOpcion
    page_title = "Opciones de Campo Dinamico"
    create_url_name = "configuracion:tramites_campos_opciones_crear"
    edit_url_name = "configuracion:tramites_campos_opciones_editar"
    delete_url_name = "configuracion:tramites_campos_opciones_eliminar"


class CampoDinamicoOpcionCreateView(TramiteCatalogoCreateBaseView):
    model = CampoDinamicoOpcion
    form_class = CampoDinamicoOpcionConfigForm
    page_title = "Nueva Opcion de Campo Dinamico"
    success_url = reverse_lazy("configuracion:tramites_campos_opciones")


class CampoDinamicoOpcionUpdateView(TramiteCatalogoUpdateBaseView):
    model = CampoDinamicoOpcion
    form_class = CampoDinamicoOpcionConfigForm
    page_title = "Editar Opcion de Campo Dinamico"
    success_url = reverse_lazy("configuracion:tramites_campos_opciones")


class CampoDinamicoOpcionDeleteView(TramiteCatalogoDeleteBaseView):
    model = CampoDinamicoOpcion
    page_title = "Eliminar Opcion de Campo Dinamico"
    success_url = reverse_lazy("configuracion:tramites_campos_opciones")
