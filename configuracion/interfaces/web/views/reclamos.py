from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import DateTimeField, F, OuterRef, Q, Subquery
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from datetime import timedelta
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
    ReclamoAdjunto,
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
    CampoDinamicoOpcionConfigForm,
    CampoDinamicoReclamoInlineConfigForm,
    CampoDinamicoReclamoConfigForm,
    EstadoReclamoConfigForm,
    EstadoReclamoTransicionConfigForm,
    PrioridadReclamoConfigForm,
    ReclamoCambioEstadoForm,
    ReclamoConfigForm,
    ReclamoDerivacionForm,
    ReclamoSolicitudDatoCampoForm,
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
        ultima_solicitud_subquery = Subquery(
            ReclamoHistorial.objects.filter(
                reclamo_id=OuterRef("pk"),
                accion="solicitud_datos_ciudadano",
            )
            .order_by("-fecha", "-id")
            .values("fecha")[:1],
            output_field=DateTimeField(),
        )
        ultima_respuesta_subquery = Subquery(
            ReclamoHistorial.objects.filter(
                reclamo_id=OuterRef("pk"),
                accion="respuesta_solicitud_datos_ciudadano",
            )
            .order_by("-fecha", "-id")
            .values("fecha")[:1],
            output_field=DateTimeField(),
        )
        queryset = (
            Reclamo.objects.select_related(
                "tipo_reclamo",
                "estado",
                "prioridad",
                "area_actual",
                "asignado_a",
            )
            .annotate(
                ultima_solicitud_datos=ultima_solicitud_subquery,
                ultima_respuesta_solicitud_datos=ultima_respuesta_subquery,
            )
            .order_by("-fecha_ingreso", "-id")
        )
        busqueda = self.request.GET.get("q", "").strip()
        area = self.request.GET.get("area", "").strip()
        estado = self.request.GET.get("estado", "").strip()
        prioridad = self.request.GET.get("prioridad", "").strip()
        estado_solicitud_datos = self.request.GET.get("estado_solicitud_datos", "").strip()
        if busqueda:
            queryset = queryset.filter(Q(numero__icontains=busqueda) | Q(titulo__icontains=busqueda))
        if area.isdigit():
            queryset = queryset.filter(area_actual_id=int(area))
        if estado.isdigit():
            queryset = queryset.filter(estado_id=int(estado))
        if prioridad.isdigit():
            queryset = queryset.filter(prioridad_id=int(prioridad))
        if estado_solicitud_datos == "sin_solicitudes":
            queryset = queryset.filter(ultima_solicitud_datos__isnull=True)
        elif estado_solicitud_datos == "pendiente":
            queryset = queryset.filter(ultima_solicitud_datos__isnull=False).filter(
                Q(ultima_respuesta_solicitud_datos__isnull=True)
                | Q(ultima_respuesta_solicitud_datos__lt=F("ultima_solicitud_datos"))
            )
        elif estado_solicitud_datos == "respondida":
            queryset = queryset.filter(ultima_solicitud_datos__isnull=False).filter(
                ultima_respuesta_solicitud_datos__gte=F("ultima_solicitud_datos")
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        def _estado_badge_class(nombre_estado):
            txt = str(nombre_estado or "").strip().lower()
            if any(k in txt for k in ["final", "aprob", "resuelto", "complet", "cerrad"]):
                return "bg-emerald-100 text-emerald-800 border border-emerald-200"
            if any(k in txt for k in ["revision", "proceso", "curso", "analisis", "gestion", "derivado"]):
                return "bg-sky-100 text-sky-800 border border-sky-200"
            if any(k in txt for k in ["pend", "espera"]):
                return "bg-amber-100 text-amber-800 border border-amber-200"
            if any(k in txt for k in ["rechaz", "cancel", "anulad", "vencid", "desestim"]):
                return "bg-rose-100 text-rose-800 border border-rose-200"
            return "bg-slate-100 text-slate-700 border border-slate-200"
        for reclamo in context.get("reclamos", []):
            if not getattr(reclamo, "ultima_solicitud_datos", None):
                reclamo.estado_solicitud_datos = "Sin solicitudes"
            elif not getattr(reclamo, "ultima_respuesta_solicitud_datos", None) or (
                reclamo.ultima_respuesta_solicitud_datos < reclamo.ultima_solicitud_datos
            ):
                reclamo.estado_solicitud_datos = "Pendiente respuesta ciudadano"
            else:
                reclamo.estado_solicitud_datos = "Respondida"
            reclamo.estado_badge_class = _estado_badge_class(getattr(getattr(reclamo, "estado", None), "nombre", ""))
        context["q"] = self.request.GET.get("q", "").strip()
        context["areas"] = Area.objects.filter(activo=True).order_by("orden", "nombre")
        context["estados"] = EstadoReclamo.objects.filter(activo=True).order_by("orden", "nombre")
        context["prioridades"] = PrioridadReclamo.objects.filter(activo=True).order_by("nivel", "nombre")
        context["estados_solicitud_datos"] = [
            ("sin_solicitudes", "Sin solicitudes"),
            ("pendiente", "Pendiente respuesta ciudadano"),
            ("respondida", "Respondida"),
        ]
        context["filtros"] = {
            "area": self.request.GET.get("area", "").strip(),
            "estado": self.request.GET.get("estado", "").strip(),
            "prioridad": self.request.GET.get("prioridad", "").strip(),
            "estado_solicitud_datos": self.request.GET.get("estado_solicitud_datos", "").strip(),
        }
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
            area_obj = Area.objects.filter(pk=int(area_actual), activo=True).first()
            if area_obj:
                if area_obj.parent_id:
                    initial["area_principal"] = area_obj.parent_id
                    initial["subarea"] = area_obj.id
                    initial["area_actual"] = area_obj.id
                else:
                    initial["area_principal"] = area_obj.id
                    initial["area_actual"] = area_obj.id
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
            "provincia",
            "municipio",
            "localidad",
            "asignado_a",
            "creado_por",
            "actualizado_por",
            "ciudadano",
        ).prefetch_related(
            "adjuntos",
            "datos_dinamicos__campo",
        )

    def get_success_url(self):
        return reverse("configuracion:reclamo_detalle", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        def _estado_badge_class(nombre_estado):
            txt = str(nombre_estado or "").strip().lower()
            if any(k in txt for k in ["final", "aprob", "resuelto", "complet", "cerrad"]):
                return "bg-emerald-100 text-emerald-800 border border-emerald-200"
            if any(k in txt for k in ["revision", "proceso", "curso", "analisis", "gestion", "derivado"]):
                return "bg-sky-100 text-sky-800 border border-sky-200"
            if any(k in txt for k in ["pend", "espera"]):
                return "bg-amber-100 text-amber-800 border border-amber-200"
            if any(k in txt for k in ["rechaz", "cancel", "anulad", "vencid", "desestim"]):
                return "bg-rose-100 text-rose-800 border border-rose-200"
            return "bg-slate-100 text-slate-700 border border-slate-200"

        context.setdefault("estado_form", ReclamoCambioEstadoForm(current_estado_id=self.object.estado_id))
        area_actual = self.object.area_actual
        derivacion_initial = {}
        if area_actual:
            if area_actual.parent_id:
                derivacion_initial["area_principal"] = area_actual.parent_id
                derivacion_initial["subarea"] = area_actual.id
                derivacion_initial["area"] = area_actual.id
            else:
                derivacion_initial["area_principal"] = area_actual.id
                derivacion_initial["area"] = area_actual.id
        context.setdefault("derivacion_form", ReclamoDerivacionForm(initial=derivacion_initial))
        context.setdefault("seguimiento_form", ReclamoSeguimientoForm())
        context.setdefault("solicitud_dato_campo_form", ReclamoSolicitudDatoCampoForm())
        historial_qs = (
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
        solicitudes_qs = ReclamoHistorial.objects.filter(
            reclamo=self.object,
            accion="solicitud_datos_ciudadano",
        ).order_by("fecha", "id")
        solicitudes_total = 0
        solicitudes_pendientes = 0
        solicitudes_respondidas = 0
        for solicitud in solicitudes_qs:
            solicitudes_total += 1
            respondida = ReclamoHistorial.objects.filter(
                reclamo=self.object,
                accion="respuesta_solicitud_datos_ciudadano",
                fecha__gte=solicitud.fecha,
                metadata__solicitud_origen_id=solicitud.id,
            ).exists()
            if not respondida:
                respondida = ReclamoHistorial.objects.filter(
                    reclamo=self.object,
                    accion="respuesta_solicitud_datos_ciudadano",
                    fecha__gte=solicitud.fecha,
                ).exists()
            if respondida:
                solicitudes_respondidas += 1
            else:
                solicitudes_pendientes += 1
        if solicitudes_total == 0:
            estado_solicitud_modificacion = "Sin solicitudes"
        elif solicitudes_pendientes > 0:
            estado_solicitud_modificacion = "Pendiente respuesta ciudadano"
        else:
            estado_solicitud_modificacion = "Respondida"
        respuestas_solicitud_qs = ReclamoHistorial.objects.filter(
            reclamo=self.object,
            accion="respuesta_solicitud_datos_ciudadano",
        ).values_list("fecha", flat=True)
        respuestas_fechas = list(respuestas_solicitud_qs)

        def _accion_legible(valor):
            return str(valor or "").strip().replace("_", " ").capitalize()

        def _comentario_legible(valor):
            txt = str(valor or "").strip()
            return txt.replace("campo_dinamico:", "")

        context["historial_items"] = historial_qs
        for item in historial_qs:
            item.accion_label = _accion_legible(getattr(item, "accion", ""))
            item.comentario_label = _comentario_legible(getattr(item, "comentario", ""))
            item.estado_nuevo_badge_class = _estado_badge_class(getattr(getattr(item, "estado_nuevo", None), "nombre", ""))
            item.estado_anterior_badge_class = _estado_badge_class(getattr(getattr(item, "estado_anterior", None), "nombre", ""))
            if item.accion == "solicitud_datos_ciudadano":
                item.solicitud_datos_estado = (
                    "Respondida"
                    if any(fecha_resp >= item.fecha for fecha_resp in respuestas_fechas)
                    else "Pendiente"
                )
            if item.accion == "respuesta_solicitud_datos_ciudadano":
                meta = getattr(item, "metadata", None) or {}
                valores = meta.get("campos_valores") or []
                normalizados = []
                for v in valores:
                    campo = (v.get("campo") or "").strip() if isinstance(v, dict) else ""
                    tipo = (v.get("tipo") or "texto").strip() if isinstance(v, dict) else "texto"
                    valor = v.get("valor") if isinstance(v, dict) else ""
                    url = (v.get("url") or "").strip() if isinstance(v, dict) else ""
                    normalizados.append({"campo": campo, "tipo": tipo, "valor": valor, "url": url})
                if not normalizados:
                    for nombre_campo in (meta.get("campos_actualizados") or []):
                        dato = self.object.datos_dinamicos.select_related("campo").filter(campo__nombre__iexact=nombre_campo).first()
                        if not dato:
                            continue
                        valor = str(getattr(dato, "valor", "") or "")
                        normalizados.append(
                            {
                                "campo": dato.campo.nombre,
                                "tipo": "archivo" if dato.campo.tipo_dato == "archivo" else "texto",
                                "valor": valor,
                                "url": "",
                            }
                        )
                item.campos_valores = normalizados
        context["historial_estados"] = [item for item in historial_qs if item.accion == "cambio_estado" or item.estado_anterior_id or item.estado_nuevo_id]
        context["historial_derivaciones"] = [item for item in historial_qs if item.accion == "derivacion"]
        context["historial_observaciones"] = [item for item in historial_qs if item.accion == "seguimiento"]
        comentarios_qs = (
            ReclamoComentario.objects.filter(reclamo=self.object)
            .select_related("usuario", "ciudadano")
            .order_by("-created_at", "-id")[:100]
        )
        context["comentarios_items"] = comentarios_qs
        context["comentarios_seguimiento_items"] = list(comentarios_qs)
        historial_full_items = [
            {"tipo": "historial", "fecha": item.fecha, "obj": item}
            for item in historial_qs
        ]
        comentarios_extra_historial = []
        for comentario in comentarios_qs:
            tiene_historial_equivalente = any(
                h.accion == "seguimiento"
                and (h.usuario_id == comentario.usuario_id)
                and (h.comentario or "").strip() == (comentario.comentario or "").strip()
                and abs((h.fecha - comentario.created_at).total_seconds()) <= 10
                for h in historial_qs
            )
            if not tiene_historial_equivalente:
                comentarios_extra_historial.append(comentario)

        historial_full_items.extend(
            {"tipo": "comentario", "fecha": item.created_at, "obj": item}
            for item in comentarios_extra_historial
        )
        historial_full_items.sort(key=lambda x: (x["fecha"], getattr(x["obj"], "id", 0)), reverse=True)
        context["historial_full_items"] = historial_full_items[:200]
        context["adjuntos_items"] = self.object.adjuntos.filter(activo=True).order_by("-created_at", "-id")
        context["datos_dinamicos_items"] = (
            self.object.datos_dinamicos.select_related("campo").filter(campo__activo=True).order_by("campo__orden", "id")
        )
        context["asignaciones_items"] = (
            ReclamoAsignacion.objects.filter(reclamo=self.object)
            .select_related("area", "usuario", "asignado_por")
            .order_by("-fecha_asignacion", "-id")[:100]
        )
        context["estado_solicitud_modificacion"] = estado_solicitud_modificacion
        context["solicitudes_modificacion_total"] = solicitudes_total
        context["solicitudes_modificacion_pendientes"] = solicitudes_pendientes
        context["solicitudes_modificacion_respondidas"] = solicitudes_respondidas
        context["estado_badge_class"] = _estado_badge_class(getattr(self.object.estado, "nombre", ""))
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
        if accion == "solicitar_dato_campo_ciudadano":
            return self._post_solicitar_dato_campo_ciudadano(request)
        if accion == "respuesta_ciudadano":
            return self._post_respuesta_ciudadano(request)

        messages.error(request, "Accion no valida.")
        return self.redirect_with_timestamp()

    @transaction.atomic
    def _post_respuesta_ciudadano(self, request):
        mensaje_html = (request.POST.get("respuesta_html") or "").strip()
        mensaje_plano = (request.POST.get("respuesta_texto") or "").strip()
        if not mensaje_html and not mensaje_plano and not request.FILES.getlist("respuesta_adjuntos"):
            messages.error(request, "Debes cargar un mensaje o al menos un archivo.")
            return self.redirect_with_timestamp()

        estado_anterior = self.object.estado
        estado_final = EstadoReclamo.objects.filter(activo=True, es_final=True).order_by("orden", "id").first()
        if not estado_final:
            messages.error(request, "No hay un estado final configurado para cerrar el reclamo.")
            return self.redirect_with_timestamp()

        comentario = ReclamoComentario.objects.create(
            reclamo=self.object,
            usuario=request.user,
            comentario=mensaje_html or mensaje_plano,
            es_interno=False,
            visible_ciudadano=True,
        )

        cantidad_adjuntos = 0
        for uploaded in request.FILES.getlist("respuesta_adjuntos"):
            if not uploaded:
                continue
            adjunto = ReclamoAdjunto(
                reclamo=self.object,
                nombre_original=uploaded.name,
                tipo_mime=getattr(uploaded, "content_type", "") or "",
                subido_por=request.user if request.user.is_authenticated else None,
                visible_ciudadano=True,
            )
            adjunto.archivo.save(uploaded.name, uploaded, save=False)
            adjunto.save()
            cantidad_adjuntos += 1

        self.object.estado = estado_final
        self.object.fecha_resolucion = timezone.now()
        self.object.save(update_fields=["estado", "fecha_resolucion", "updated_at"])

        registrar_historial(
            reclamo=self.object,
            accion="respuesta_operador_ciudadano",
            usuario=request.user if request.user.is_authenticated else None,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_final,
            area_nueva=self.object.area_actual,
            comentario=mensaje_plano or "Se envio respuesta al ciudadano.",
            visible_ciudadano=True,
            metadata={
                "ui": "configuracion",
                "tipo": "respuesta_ciudadano",
                "comentario_id": comentario.id,
                "adjuntos_nuevos": cantidad_adjuntos,
                "finalizado": True,
            },
        )
        messages.success(request, "Respuesta enviada y reclamo finalizado.")
        return self.redirect_with_timestamp()

    @transaction.atomic
    def _post_cambiar_estado(self, request):
        form = ReclamoCambioEstadoForm(request.POST, current_estado_id=self.object.estado_id)
        if not form.is_valid():
            messages.error(request, "No se pudo cambiar el estado. Revisa los datos ingresados.")
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
            messages.error(request, str(exc))
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

    @transaction.atomic
    def _post_solicitar_dato_campo_ciudadano(self, request):
        if self.object.es_anonimo or not self.object.ciudadano_id:
            messages.error(request, "No se puede solicitar edicion de datos en reclamos anonimos.")
            return self.redirect_with_timestamp()

        form = ReclamoSolicitudDatoCampoForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(solicitud_dato_campo_form=form))

        campo_objetivo = form.cleaned_data["campo_objetivo"].strip()
        motivo = form.cleaned_data["motivo"].strip()
        metadata = {
            "ui": "configuracion",
            "tipo": "solicitud_datos_ciudadano",
            "campo_objetivo": campo_objetivo,
        }

        comentario = f"Solicitud sobre '{campo_objetivo}': {motivo}"

        registrar_historial(
            reclamo=self.object,
            accion="solicitud_datos_ciudadano",
            usuario=request.user,
            estado_nuevo=self.object.estado,
            area_nueva=self.object.area_actual,
            asignado_nuevo=self.object.asignado_a,
            comentario=comentario,
            visible_ciudadano=True,
            metadata=metadata,
        )
        messages.success(request, "Solicitud de datos registrada correctamente.")
        return self.redirect_with_timestamp()


class ReclamoCatalogosConfigView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = "configuracion/reclamo_catalogos.html"
    required_groups = ["Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_tab = self.request.GET.get("tab", "estados")
        filtro_activo = self.request.GET.get("activo", "").strip()

        estados = EstadoReclamo.objects.order_by("orden", "nombre", "id")
        prioridades = PrioridadReclamo.objects.order_by("nivel", "nombre", "id")
        if filtro_activo in {"1", "0"}:
            activo_bool = filtro_activo == "1"
            estados = estados.filter(activo=activo_bool)
            prioridades = prioridades.filter(activo=activo_bool)

        context["active_tab"] = active_tab
        context["filtro_activo"] = filtro_activo
        context["estados"] = estados
        context["prioridades"] = prioridades
        return context


CampoDinamicoTipoReclamoInlineFormSet = inlineformset_factory(
    TipoReclamo,
    CampoDinamicoReclamo,
    form=CampoDinamicoReclamoInlineConfigForm,
    fields=[
        "nombre",
        "codigo",
        "descripcion",
        "tipo_dato",
        "obligatorio",
        "orden",
        "placeholder",
        "ayuda",
        "valor_default",
        "longitud_maxima",
        "activo",
    ],
    extra=1,
    can_delete=True,
)


class ReclamoTipoConfiguracionListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = TipoReclamo
    template_name = "configuracion/reclamo_tipo_configuracion_list.html"
    context_object_name = "tipos_reclamo"
    paginate_by = 20
    required_groups = ["Administrador"]

    def get_queryset(self):
        queryset = TipoReclamo.objects.select_related("area", "prioridad_default").order_by(
            "orden", "nombre", "id"
        )
        q = self.request.GET.get("q", "").strip()
        area = self.request.GET.get("area", "").strip()
        subarea = self.request.GET.get("subarea", "").strip()
        prioridad = self.request.GET.get("prioridad", "").strip()
        activo = self.request.GET.get("activo", "").strip()
        destacado = self.request.GET.get("destacado", "").strip()

        if q:
            queryset = queryset.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        if subarea.isdigit():
            queryset = queryset.filter(area_id=int(subarea))
        if area.isdigit():
            queryset = queryset.filter(Q(area__parent_id=int(area)) | Q(area_id=int(area)))
        if prioridad.isdigit():
            queryset = queryset.filter(prioridad_default_id=int(prioridad))
        if activo in ("1", "0"):
            queryset = queryset.filter(activo=(activo == "1"))
        if destacado in ("1", "0"):
            queryset = queryset.filter(destacado=(destacado == "1"))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "").strip()
        context["filtros"] = {
            "area": self.request.GET.get("area", "").strip(),
            "subarea": self.request.GET.get("subarea", "").strip(),
            "prioridad": self.request.GET.get("prioridad", "").strip(),
            "activo": self.request.GET.get("activo", "").strip(),
            "destacado": self.request.GET.get("destacado", "").strip(),
        }
        context["areas"] = Area.objects.filter(parent__isnull=True).order_by("orden", "nombre")
        context["subareas"] = Area.objects.filter(parent__isnull=False).select_related("parent").order_by(
            "parent__nombre", "orden", "nombre"
        )
        context["prioridades"] = PrioridadReclamo.objects.order_by("nivel", "nombre")
        context["back_url"] = reverse("configuracion:reclamos_catalogos")
        return context


class _ReclamoTipoConfiguracionBaseView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin):
    model = TipoReclamo
    form_class = TipoReclamoConfigForm
    template_name = "configuracion/reclamo_tipo_configuracion_form.html"
    required_groups = ["Administrador"]
    page_title = ""

    def _get_campos_formset(self, data=None):
        return CampoDinamicoTipoReclamoInlineFormSet(data=data, instance=self.object, prefix="campos")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_url"] = reverse("configuracion:reclamos_configuracion")
        context.setdefault("campos_formset", self._get_campos_formset())
        return context

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        campos_formset = self._get_campos_formset(self.request.POST)
        if not campos_formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form, campos_formset=campos_formset))
        campos_formset.instance = self.object
        campos_formset.save()
        for campo_form in campos_formset.forms:
            if not hasattr(campo_form, "cleaned_data"):
                continue
            if campo_form.cleaned_data.get("DELETE"):
                continue
            campo_obj = campo_form.instance
            if not campo_obj.pk:
                continue
            if campo_obj.tipo_dato != CampoDinamicoReclamo.TipoDato.SELECCION:
                campo_obj.opciones.update(activo=False)
                continue

            opciones_texto = (campo_form.cleaned_data.get("opciones_texto") or "").strip()
            etiquetas = [linea.strip() for linea in opciones_texto.splitlines() if linea.strip()]
            etiquetas_unicas = []
            seen = set()
            for etiqueta in etiquetas:
                key = etiqueta.lower()
                if key in seen:
                    continue
                seen.add(key)
                etiquetas_unicas.append(etiqueta)

            valores_activos = []
            for idx, etiqueta in enumerate(etiquetas_unicas):
                valor = etiqueta
                valores_activos.append(valor)
                CampoDinamicoOpcion.objects.update_or_create(
                    campo=campo_obj,
                    valor=valor,
                    defaults={"etiqueta": etiqueta, "orden": idx, "activo": True},
                )
            campo_obj.opciones.exclude(valor__in=valores_activos).update(activo=False)
        messages.success(self.request, "Tipo de reclamo guardado correctamente.")
        return self.redirect_with_timestamp()


class ReclamoTipoConfiguracionCreateView(_ReclamoTipoConfiguracionBaseView, CreateView):
    page_title = "Agregar Tipo de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_configuracion")

    def get_context_data(self, **kwargs):
        self.object = None
        return super().get_context_data(**kwargs)


class ReclamoTipoConfiguracionUpdateView(_ReclamoTipoConfiguracionBaseView, UpdateView):
    page_title = "Editar Tipo de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_configuracion")


class ReclamoTipoConfiguracionDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = TipoReclamo
    template_name = "configuracion/reclamo_tipo_configuracion_detail.html"
    context_object_name = "tipo_reclamo"
    required_groups = ["Administrador"]

    def get_queryset(self):
        return TipoReclamo.objects.select_related("area", "prioridad_default")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campos_dinamicos"] = CampoDinamicoReclamo.objects.filter(tipo_reclamo=self.object).order_by(
            "orden", "nombre", "id"
        )
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, "activo"):
            self.object.activo = False
            self.object.save(update_fields=["activo", "updated_at"])
            messages.success(request, "Registro inactivado correctamente.")
            return HttpResponseRedirect(str(self.success_url))
        return super().post(request, *args, **kwargs)


class ReclamoCatalogoDetailBaseView(_ReclamoCatalogoBaseView, DetailView):
    template_name = "configuracion/reclamo_catalogo_detail.html"
    context_object_name = "item"
    page_title = ""
    back_url = reverse_lazy("configuracion:reclamos_catalogos")

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
        context["page_title"] = self.page_title
        context["back_url"] = self.back_url
        return context


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
    success_url = reverse_lazy("configuracion:reclamos_catalogos")


class EstadoReclamoUpdateView(ReclamoCatalogoUpdateBaseView):
    model = EstadoReclamo
    form_class = EstadoReclamoConfigForm
    page_title = "Editar Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_catalogos")


class EstadoReclamoDeleteView(ReclamoCatalogoDeleteBaseView):
    model = EstadoReclamo
    page_title = "Eliminar Estado de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_catalogos")


class EstadoReclamoDetailView(ReclamoCatalogoDetailBaseView):
    model = EstadoReclamo
    page_title = "Detalle de Estado de Reclamo"


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
    success_url = reverse_lazy("configuracion:reclamos_catalogos")


class PrioridadReclamoUpdateView(ReclamoCatalogoUpdateBaseView):
    model = PrioridadReclamo
    form_class = PrioridadReclamoConfigForm
    page_title = "Editar Prioridad de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_catalogos")


class PrioridadReclamoDeleteView(ReclamoCatalogoDeleteBaseView):
    model = PrioridadReclamo
    page_title = "Eliminar Prioridad de Reclamo"
    success_url = reverse_lazy("configuracion:reclamos_catalogos")


class PrioridadReclamoDetailView(ReclamoCatalogoDetailBaseView):
    model = PrioridadReclamo
    page_title = "Detalle de Prioridad de Reclamo"


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
