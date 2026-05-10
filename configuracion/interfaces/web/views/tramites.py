from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import DateTimeField, F, OuterRef, Q, Subquery
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.text import slugify
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
    TramiteAdjunto,
    TramiteComentario,
    TramiteHistorial,
)
from tramites.application.services import (
    obtener_estado_inicial,
    obtener_prioridad_base,
    registrar_historial,
    validar_requisitos_runtime_tramite,
    validar_transicion_estado_tramite,
)
from turnos.models import ConfiguracionTurnos, SedeTurno

from ..forms import (
    CampoDinamicoOpcionConfigForm,
    CampoDinamicoTramiteInlineConfigForm,
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
    TramiteSolicitudDatoCampoForm,
)


class TramiteConfigListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = Tramite
    template_name = "configuracion/tramite_list.html"
    context_object_name = "tramites"
    paginate_by = 20
    required_groups = ["Administrador"]

    def get_queryset(self):
        ultima_solicitud_subquery = Subquery(
            TramiteHistorial.objects.filter(
                tramite_id=OuterRef("pk"),
                accion="solicitud_datos_ciudadano",
            )
            .order_by("-fecha", "-id")
            .values("fecha")[:1],
            output_field=DateTimeField(),
        )
        ultima_respuesta_subquery = Subquery(
            TramiteHistorial.objects.filter(
                tramite_id=OuterRef("pk"),
                accion="respuesta_solicitud_datos_ciudadano",
            )
            .order_by("-fecha", "-id")
            .values("fecha")[:1],
            output_field=DateTimeField(),
        )
        queryset = (
            Tramite.objects.select_related(
                "tipo_tramite",
                "estado",
                "prioridad",
                "area_actual",
                "asignado_a",
            )
            .annotate(
                ultima_solicitud_datos=ultima_solicitud_subquery,
                ultima_respuesta_solicitud_datos=ultima_respuesta_subquery,
            )
            .order_by("-fecha_inicio", "-id")
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
        for tramite in context.get("tramites", []):
            if not getattr(tramite, "ultima_solicitud_datos", None):
                tramite.estado_solicitud_datos = "Sin solicitudes"
            elif not getattr(tramite, "ultima_respuesta_solicitud_datos", None) or (
                tramite.ultima_respuesta_solicitud_datos < tramite.ultima_solicitud_datos
            ):
                tramite.estado_solicitud_datos = "Pendiente respuesta ciudadano"
            else:
                tramite.estado_solicitud_datos = "Respondida"
            tramite.estado_badge_class = _estado_badge_class(getattr(getattr(tramite, "estado", None), "nombre", ""))
        context["q"] = self.request.GET.get("q", "").strip()
        context["areas"] = Area.objects.filter(activo=True).order_by("orden", "nombre")
        context["estados"] = EstadoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        context["prioridades"] = PrioridadTramite.objects.filter(activo=True).order_by("nivel", "nombre")
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
            "provincia",
            "municipio",
            "localidad",
            "asignado_a",
            "creado_por",
            "actualizado_por",
            "ciudadano",
        ).prefetch_related("adjuntos", "datos_dinamicos__campo")

    def get_success_url(self):
        return reverse("configuracion:tramite_detalle", kwargs={"pk": self.object.pk})

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

        def _accion_legible(valor):
            texto = (valor or "").strip().replace("_", " ")
            return texto[:1].upper() + texto[1:] if texto else "-"
        def _comentario_legible(valor):
            texto = (valor or "").strip()
            return texto.replace("campo_dinamico:", "")

        context.setdefault("estado_form", TramiteCambioEstadoForm(current_estado_id=self.object.estado_id))
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
        context.setdefault("derivacion_form", TramiteDerivacionForm(initial=derivacion_initial))
        context.setdefault("seguimiento_form", TramiteSeguimientoForm())
        context.setdefault("solicitud_dato_campo_form", TramiteSolicitudDatoCampoForm())
        historial_qs = (
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
        solicitudes_qs = TramiteHistorial.objects.filter(
            tramite=self.object,
            accion="solicitud_datos_ciudadano",
        ).order_by("fecha", "id")
        solicitudes_total = 0
        solicitudes_pendientes = 0
        solicitudes_respondidas = 0
        for solicitud in solicitudes_qs:
            solicitudes_total += 1
            respondida = TramiteHistorial.objects.filter(
                tramite=self.object,
                accion="respuesta_solicitud_datos_ciudadano",
                fecha__gte=solicitud.fecha,
                metadata__solicitud_origen_id=solicitud.id,
            ).exists()
            if not respondida:
                respondida = TramiteHistorial.objects.filter(
                    tramite=self.object,
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
        respuestas_solicitud_qs = TramiteHistorial.objects.filter(
            tramite=self.object,
            accion="respuesta_solicitud_datos_ciudadano",
        ).values_list("fecha", flat=True)
        respuestas_fechas = list(respuestas_solicitud_qs)
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
        context["historial_items"] = historial_qs
        context["historial_estados"] = [item for item in historial_qs if item.accion == "cambio_estado" or item.estado_anterior_id or item.estado_nuevo_id]
        context["historial_derivaciones"] = [item for item in historial_qs if item.accion == "derivacion"]
        comentarios_qs = (
            TramiteComentario.objects.filter(tramite=self.object)
            .select_related("usuario", "ciudadano")
            .order_by("-created_at", "-id")[:100]
        )
        context["comentarios_items"] = comentarios_qs
        context["comentarios_seguimiento_items"] = list(comentarios_qs)
        historial_full_items = [{"tipo": "historial", "fecha": item.fecha, "obj": item} for item in historial_qs]
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
            TramiteAsignacion.objects.filter(tramite=self.object)
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

        contenido = mensaje_html or mensaje_plano
        estado_anterior = self.object.estado
        estado_final = (
            EstadoTramite.objects.filter(activo=True, es_final=True, municipio=self.object.municipio)
            .order_by("orden", "id")
            .first()
            or EstadoTramite.objects.filter(activo=True, es_final=True, municipio__isnull=True).order_by("orden", "id").first()
            or EstadoTramite.objects.filter(activo=True, es_final=True).order_by("orden", "id").first()
        )
        if not estado_final:
            messages.error(request, "No hay un estado final configurado para cerrar el trámite.")
            return self.redirect_with_timestamp()

        comentario = TramiteComentario.objects.create(
            tramite=self.object,
            usuario=request.user,
            comentario=contenido,
            es_interno=False,
            visible_ciudadano=True,
        )

        cantidad_adjuntos = 0
        for uploaded in request.FILES.getlist("respuesta_adjuntos"):
            if not uploaded:
                continue
            adjunto = TramiteAdjunto(
                tramite=self.object,
                nombre_original=uploaded.name,
                tipo_mime=getattr(uploaded, "content_type", "") or "",
                subido_por=request.user if request.user.is_authenticated else None,
                visible_ciudadano=True,
            )
            adjunto.archivo.save(uploaded.name, uploaded, save=False)
            adjunto.save()
            cantidad_adjuntos += 1

        self.object.estado = estado_final
        self.object.fecha_finalizacion = timezone.now()
        self.object.save(update_fields=["estado", "fecha_finalizacion", "updated_at"])

        registrar_historial(
            tramite=self.object,
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
        messages.success(request, "Respuesta enviada y trámite finalizado.")
        return self.redirect_with_timestamp()

    @transaction.atomic
    def _post_cambiar_estado(self, request):
        form = TramiteCambioEstadoForm(request.POST, current_estado_id=self.object.estado_id)
        if not form.is_valid():
            messages.error(request, "No se pudo cambiar el estado. Revisa los datos ingresados.")
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
            messages.error(request, str(exc))
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
            messages.error(request, "No se pudo derivar el tramite. Revisa los datos ingresados.")
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
            messages.error(request, "No se pudo guardar el seguimiento. Revisa los datos ingresados.")
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

    @transaction.atomic
    def _post_solicitar_dato_campo_ciudadano(self, request):
        if not self.object.ciudadano_id:
            messages.error(request, "No se puede solicitar edicion de datos en tramites sin ciudadano asociado.")
            return self.redirect_with_timestamp()
        form = TramiteSolicitudDatoCampoForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(solicitud_dato_campo_form=form))
        campo_objetivo = form.cleaned_data["campo_objetivo"].strip()
        motivo = form.cleaned_data["motivo"].strip()
        metadata = {"ui": "configuracion", "tipo": "solicitud_datos_ciudadano", "campo_objetivo": campo_objetivo}
        comentario = f"Solicitud sobre '{campo_objetivo}': {motivo}"
        registrar_historial(
            tramite=self.object,
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


class TramiteCatalogosConfigView(LoginRequiredMixin, GroupRequiredMixin, TemplateView):
    template_name = "configuracion/tramite_catalogos.html"
    required_groups = ["Administrador"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_tab = self.request.GET.get("tab", "estados")
        filtro_activo = self.request.GET.get("activo", "").strip()
        estados = EstadoTramite.objects.order_by("orden", "nombre", "id")
        prioridades = PrioridadTramite.objects.order_by("nivel", "nombre", "id")
        if filtro_activo in {"1", "0"}:
            activo_bool = filtro_activo == "1"
            estados = estados.filter(activo=activo_bool)
            prioridades = prioridades.filter(activo=activo_bool)
        context["active_tab"] = active_tab
        context["filtro_activo"] = filtro_activo
        context["estados"] = estados
        context["prioridades"] = prioridades
        return context


CampoDinamicoTipoTramiteInlineFormSet = inlineformset_factory(
    TipoTramite,
    CampoDinamicoTramite,
    form=CampoDinamicoTramiteInlineConfigForm,
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


class TramiteTipoConfiguracionListView(LoginRequiredMixin, GroupRequiredMixin, ListView):
    model = TipoTramite
    template_name = "configuracion/tramite_tipo_configuracion_list.html"
    context_object_name = "tipos_tramite"
    paginate_by = 20
    required_groups = ["Administrador"]

    def get_queryset(self):
        agenda_subq = (
            ConfiguracionTurnos.objects.filter(tipo_tramite_id=OuterRef("pk"))
            .order_by("-activo", "id")
            .values("id")[:1]
        )
        queryset = TipoTramite.objects.select_related(
            "area",
            "area__parent",
            "prioridad_default",
            "recurso_turnos",
            "recurso_turnos__configuracion_turnos",
        ).annotate(
            agenda_config_id=Subquery(agenda_subq),
        ).order_by(
            "orden", "nombre", "id"
        )
        q = self.request.GET.get("q", "").strip()
        area = self.request.GET.get("area", "").strip()
        subarea = self.request.GET.get("subarea", "").strip()
        prioridad = self.request.GET.get("prioridad", "").strip()
        activo = self.request.GET.get("activo", "").strip()
        destacado = self.request.GET.get("destacado", "").strip()
        requiere_turno = self.request.GET.get("requiere_turno", "").strip()
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
        if requiere_turno in ("1", "0"):
            queryset = queryset.filter(requiere_turno=(requiere_turno == "1"))
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
            "requiere_turno": self.request.GET.get("requiere_turno", "").strip(),
        }
        context["areas"] = Area.objects.filter(parent__isnull=True).order_by("orden", "nombre")
        context["subareas"] = Area.objects.filter(parent__isnull=False).select_related("parent").order_by(
            "parent__nombre", "orden", "nombre"
        )
        context["prioridades"] = PrioridadTramite.objects.order_by("nivel", "nombre")
        context["back_url"] = reverse("configuracion:tramites_catalogos")
        return context


class _TramiteTipoConfiguracionBaseView(LoginRequiredMixin, GroupRequiredMixin, TimestampedSuccessUrlMixin):
    model = TipoTramite
    form_class = TipoTramiteConfigForm
    template_name = "configuracion/tramite_tipo_configuracion_form.html"
    required_groups = ["Administrador"]
    page_title = ""

    def _get_campos_formset(self, data=None):
        return CampoDinamicoTipoTramiteInlineFormSet(data=data, instance=self.object, prefix="campos")

    def _completar_y_validar_codigos_campos(self, campos_formset):
        forms_activas = []
        for campo_form in campos_formset.forms:
            if not hasattr(campo_form, "cleaned_data"):
                continue
            if campo_form.cleaned_data.get("DELETE"):
                continue
            nombre = (campo_form.cleaned_data.get("nombre") or "").strip()
            if not nombre:
                continue
            forms_activas.append(campo_form)

        ids_editados = [f.instance.pk for f in forms_activas if getattr(f.instance, "pk", None)]
        codigos_usados = set(
            CampoDinamicoTramite.objects.filter(tipo_tramite=self.object)
            .exclude(pk__in=ids_editados)
            .values_list("codigo", flat=True)
        )

        # Primero registrar códigos explícitos y detectar duplicados ingresados en el mismo submit.
        for campo_form in forms_activas:
            codigo = (campo_form.cleaned_data.get("codigo") or "").strip()
            if not codigo:
                continue
            if codigo in codigos_usados:
                campo_form.add_error("codigo", "El código ya existe para este tipo de trámite.")
                continue
            codigos_usados.add(codigo)

        # Luego completar códigos faltantes con base en el nombre.
        for campo_form in forms_activas:
            codigo = (campo_form.cleaned_data.get("codigo") or "").strip()
            if codigo:
                campo_form.instance.codigo = codigo
                continue

            nombre = (campo_form.cleaned_data.get("nombre") or "").strip()
            base = slugify(nombre).replace("-", "_")[:48] or "campo"
            candidato = base
            sufijo = 2
            while candidato in codigos_usados:
                candidato = f"{base[:43]}_{sufijo}"
                sufijo += 1
            campo_form.cleaned_data["codigo"] = candidato
            campo_form.instance.codigo = candidato
            codigos_usados.add(candidato)

        return all(not f.errors for f in forms_activas)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = self.page_title
        context["back_url"] = reverse("configuracion:tramites_configuracion")
        context.setdefault("campos_formset", self._get_campos_formset())
        return context

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save()
        campos_formset = self._get_campos_formset(self.request.POST)
        if not campos_formset.is_valid():
            messages.error(self.request, "No se pudo guardar. Revisa los errores en Campos extra dinamicos.")
            return self.render_to_response(self.get_context_data(form=form, campos_formset=campos_formset))
        if not self._completar_y_validar_codigos_campos(campos_formset):
            messages.error(self.request, "No se pudo guardar. Revisa los errores en códigos de Campos extra dinámicos.")
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
            if campo_obj.tipo_dato != CampoDinamicoTramite.TipoDato.SELECCION:
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
        messages.success(self.request, "Tipo de tramite guardado correctamente.")
        return self.redirect_with_timestamp()


class TramiteTipoConfiguracionCreateView(_TramiteTipoConfiguracionBaseView, CreateView):
    page_title = "Agregar Tipo de Tramite"
    success_url = reverse_lazy("configuracion:tramites_configuracion")

    def get_context_data(self, **kwargs):
        self.object = None
        return super().get_context_data(**kwargs)


class TramiteTipoConfiguracionUpdateView(_TramiteTipoConfiguracionBaseView, UpdateView):
    page_title = "Editar Tipo de Tramite"
    success_url = reverse_lazy("configuracion:tramites_configuracion")


class TramiteTipoConfiguracionDetailView(LoginRequiredMixin, GroupRequiredMixin, DetailView):
    model = TipoTramite
    template_name = "configuracion/tramite_tipo_configuracion_detail.html"
    context_object_name = "tipo_tramite"
    required_groups = ["Administrador"]

    def get_queryset(self):
        return TipoTramite.objects.select_related(
            "area",
            "area__parent",
            "prioridad_default",
            "recurso_turnos",
            "recurso_turnos__configuracion_turnos",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["campos_dinamicos"] = CampoDinamicoTramite.objects.filter(tipo_tramite=self.object).order_by(
            "orden", "nombre", "id"
        )
        agendas_qs = (
            ConfiguracionTurnos.objects.select_related("sede", "recursoturnos")
            .filter(tipo_tramite=self.object)
            .order_by("sede__nombre", "nombre", "id")
        )
        sedes_habilitadas_qs = SedeTurno.objects.filter(tramites_habilitados=self.object).order_by("nombre")
        sedes_agendas_qs = SedeTurno.objects.filter(configuraciones__tipo_tramite=self.object).order_by("nombre")
        context["agendas_turno"] = agendas_qs
        context["sedes_turno"] = (sedes_habilitadas_qs | sedes_agendas_qs).distinct()
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

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if hasattr(self.object, "activo"):
            self.object.activo = False
            self.object.save(update_fields=["activo", "updated_at"])
            messages.success(request, "Registro inactivado correctamente.")
            return HttpResponseRedirect(str(self.success_url))
        return super().post(request, *args, **kwargs)


class TramiteCatalogoDetailBaseView(_TramiteCatalogoBaseView, DetailView):
    template_name = "configuracion/reclamo_catalogo_detail.html"
    context_object_name = "item"
    page_title = ""
    back_url = reverse_lazy("configuracion:tramites_catalogos")

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
    success_url = reverse_lazy("configuracion:tramites_catalogos")


class EstadoTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = EstadoTramite
    form_class = EstadoTramiteConfigForm
    page_title = "Editar Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_catalogos")


class EstadoTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = EstadoTramite
    page_title = "Eliminar Estado de Tramite"
    success_url = reverse_lazy("configuracion:tramites_catalogos")


class EstadoTramiteDetailView(TramiteCatalogoDetailBaseView):
    model = EstadoTramite
    page_title = "Detalle de Estado de Tramite"


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
    success_url = reverse_lazy("configuracion:tramites_catalogos")


class PrioridadTramiteUpdateView(TramiteCatalogoUpdateBaseView):
    model = PrioridadTramite
    form_class = PrioridadTramiteConfigForm
    page_title = "Editar Prioridad de Tramite"
    success_url = reverse_lazy("configuracion:tramites_catalogos")


class PrioridadTramiteDeleteView(TramiteCatalogoDeleteBaseView):
    model = PrioridadTramite
    page_title = "Eliminar Prioridad de Tramite"
    success_url = reverse_lazy("configuracion:tramites_catalogos")


class PrioridadTramiteDetailView(TramiteCatalogoDetailBaseView):
    model = PrioridadTramite
    page_title = "Detalle de Prioridad de Tramite"


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
