import os
import re
import unicodedata
import uuid
from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import (
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from portal.interfaces.web.forms import CiudadanoConfirmarTurnoForm
from portal.models import TurnoCiudadano
from reclamos.models import Area, CampoDinamicoReclamo, Reclamo, ReclamoAdjunto, ReclamoComentario, ReclamoDatoDinamico, TipoReclamo, ReclamoHistorial
from reclamos.services import (
    guardar_datos_dinamicos as guardar_datos_dinamicos_reclamo,
    obtener_estado_inicial as obtener_estado_inicial_reclamo,
    obtener_prioridad_base as obtener_prioridad_base_reclamo,
    registrar_historial as registrar_historial_reclamo,
    validar_y_preparar_datos_dinamicos as validar_datos_dinamicos_reclamo,
)
from tramites.models import (
    CampoDinamicoTramite,
    RequisitoTramite,
    TipoTramite,
    Tramite,
    TramiteAdjunto,
    TramiteComentario,
    TramiteDatoDinamico,
    TramiteHistorial,
)
from tramites.application.services import (
    guardar_datos_dinamicos as guardar_datos_dinamicos_tramite,
    obtener_estado_inicial as obtener_estado_inicial_tramite,
    obtener_prioridad_base as obtener_prioridad_base_tramite,
    registrar_historial as registrar_historial_tramite,
    validar_y_preparar_datos_dinamicos as validar_datos_dinamicos_tramite,
)
from turnos.models import ConfiguracionTurnos

from .forms import (
    CiudadanoCambioEmailForm,
    CiudadanoCambioPasswordForm,
    CiudadanoEditarDatosForm,
    CiudadanoEnviarMensajeForm,
    CiudadanoNuevaConsultaForm,
    CiudadanoPasswordResetForm,
    ReclamoDetalleForm,
    RegistroStep1Form,
    RegistroStep2Form,
    TramiteDetalleForm,
)

from portal.interfaces.web.forms import CiudadanoLoginForm
from portal.infrastructure.selectors.ciudadano_perfil import (
    get_ciudadano_perfil_context,
    get_ciudadano_programa_derivaciones,
    get_ciudadano_programa_detalle_or_404,
    get_ciudadano_programas_context,
)
from portal.infrastructure.selectors.public import get_portal_home_context
from portal.infrastructure.selectors.turnos_ciudadano import (
    get_recurso_turnos_activo_or_404,
    get_recursos_turnos_activos,
    get_turno_ciudadano_or_404,
    get_turnos_ciudadano_contexto,
)
from portal.infrastructure.services.turnos_ciudadano import (
    TurnoNoDisponibleError,
    cancelar_turno_ciudadano,
    reservar_turno_ciudadano,
)
from portal.turnos_utils import get_calendario_mensual, get_slots_disponibles
from portal.interfaces.web.views.ciudadano_auth import (
    _get_client_ip,
    _get_safe_next,
    limpiar_login_fallido,
    login_bloqueado,
    registrar_login_fallido,
)

def _get_ciudadano_from_user(user):
    if not getattr(user, "is_authenticated", False):
        return None
    return getattr(user, "ciudadano_perfil", None)


def _is_ciudadano_user(user):
    return getattr(user, "is_authenticated", False) and user.groups.filter(name="Ciudadanos").exists()


def _require_ciudadano_or_login(request):
    if _is_ciudadano_user(request.user):
        return None
    login_url = f"{reverse('portal_ciudadano:login')}?next={request.get_full_path()}"
    return redirect(login_url)


def _get_tramite_abierto_mismo_tipo(ciudadano, tipo_tramite):
    if not ciudadano or not tipo_tramite:
        return None
    return (
        Tramite.objects.select_related("estado")
        .filter(
            ciudadano=ciudadano,
            tipo_tramite=tipo_tramite,
            activo=True,
        )
        .exclude(estado__es_final=True)
        .order_by("-fecha_inicio", "-id")
        .first()
    )


def _get_turno_activo_mismo_tipo(ciudadano, tipo_tramite):
    if not ciudadano or not tipo_tramite:
        return None
    estados_vigentes = [TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO]
    hoy = date.today()
    return (
        TurnoCiudadano.objects.filter(
            ciudadano=ciudadano,
            estado__in=estados_vigentes,
            fecha__gte=hoy,
        )
        .filter(
            Q(configuracion__tipo_tramite=tipo_tramite)
            | Q(recurso__configuracion_turnos__tipo_tramite=tipo_tramite)
        )
        .order_by("fecha", "hora_inicio")
        .first()
    )


def _format_historial_accion(raw):
    texto = (raw or "").strip().replace("_", " ")
    if not texto:
        return "-"
    return texto[:1].upper() + texto[1:]


def _format_historial_comentario(raw):
    texto = (raw or "").strip()
    if not texto:
        return ""
    texto = texto.replace("campo_dinamico:", "")
    return texto


def _display_actor_name(user):
    if not user:
        return "Sistema"
    full_name = (user.get_full_name() or "").strip()
    if full_name:
        return full_name
    username = (getattr(user, "username", "") or "").strip()
    return username or "Sistema"


def _format_solicitud_datos_notif_text(raw):
    texto = (raw or "").strip()
    if not texto:
        return "Revisá el detalle y completá la información solicitada."
    # Limpia prefijos técnicos de campos dinámicos en notificaciones.
    return re.sub(r"campo_dinamico:([^']+)", r"\1", texto)


def _normalize_html_links(raw_html):
    html = str(raw_html or "")
    if not html:
        return ""

    def _repl(match):
        quote = match.group(1)
        href = (match.group(2) or "").strip()
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#", "/")):
            return f'href={quote}{href}{quote}'
        if href.startswith("www."):
            return f'href={quote}https://{href}{quote}'
        return f'href={quote}{href}{quote}'

    html = re.sub(r'href\s*=\s*(["\'])([^"\']+)\1', _repl, html, flags=re.IGNORECASE)

    def _anchor_repl(match):
        attrs = match.group(1) or ""
        new_attrs = attrs
        if not re.search(r'\btarget\s*=', new_attrs, flags=re.IGNORECASE):
            new_attrs += ' target="_blank"'
        if not re.search(r'\brel\s*=', new_attrs, flags=re.IGNORECASE):
            new_attrs += ' rel="noopener noreferrer"'
        return f"<a{new_attrs}>"

    html = re.sub(r"<a\b([^>]*)>", _anchor_repl, html, flags=re.IGNORECASE)
    return html


def _estado_badge_class(nombre_estado):
    txt = (nombre_estado or "").strip().lower()
    txt = "".join(c for c in unicodedata.normalize("NFD", txt) if unicodedata.category(c) != "Mn")
    if any(k in txt for k in ["final", "aprob", "resuelto", "complet", "cerrad"]):
        return "badge-ok"
    if any(k in txt for k in ["revision", "proceso", "curso", "analisis", "gestion", "derivado"]):
        return "badge-info"
    if any(k in txt for k in ["pend", "espera"]):
        return "badge-warn"
    if any(k in txt for k in ["rechaz", "cancel", "anulad", "vencid", "desestim"]):
        return "badge-danger"
    return "badge-neutral"


class PortalCiudadanoHomeView(TemplateView):
    template_name = "portal_ciudadano/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_portal_home_context())
        return context


class PortalCiudadanoChatView(TemplateView):
    template_name = "portal_ciudadano/chat.html"


class PortalCiudadanoLoginView(TemplateView):
    template_name = "portal_ciudadano/login.html"

    @staticmethod
    def _should_show_anonymous_claim_option(request, next_url):
        explicit_flag = str(request.GET.get("anonimo_reclamo", "")).strip().lower() in {"1", "true", "si", "yes"}
        next_is_claim_flow = str(next_url or "").startswith("/portal-ciudadano/reclamos/")
        return explicit_flag or next_is_claim_flow

    @staticmethod
    def _build_anonymous_claim_url(next_url):
        if next_url and next_url.startswith("/portal-ciudadano/reclamos/"):
            separator = "&" if "?" in next_url else "?"
            return f"{next_url}{separator}anonimo_reclamo=1"
        return f"{reverse('portal_ciudadano:reclamos')}?anonimo=1"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name="Ciudadanos").exists():
            return redirect("portal_ciudadano:mi_perfil")
        next_url = _get_safe_next(request)
        if next_url:
            request.session["portal_next"] = next_url
        return self.render_to_response(
            {
                "form": CiudadanoLoginForm(),
                "next": next_url,
                "mostrar_boton_reclamo_anonimo": self._should_show_anonymous_claim_option(request, next_url),
                "anonimo_reclamo_url": self._build_anonymous_claim_url(next_url),
            }
        )

    def post(self, request, *args, **kwargs):
        ip = _get_client_ip(request)
        next_url = _get_safe_next(request)
        mostrar_boton_reclamo_anonimo = self._should_show_anonymous_claim_option(request, next_url)
        if login_bloqueado(ip):
            messages.error(request, "Demasiados intentos fallidos. Intenta de nuevo en 5 minutos.")
            return self.render_to_response(
                {
                    "form": CiudadanoLoginForm(),
                    "bloqueado": True,
                    "next": next_url,
                    "mostrar_boton_reclamo_anonimo": mostrar_boton_reclamo_anonimo,
                    "anonimo_reclamo_url": self._build_anonymous_claim_url(next_url),
                }
            )

        form = CiudadanoLoginForm(request, data=request.POST)
        if form.is_valid():
            limpiar_login_fallido(ip)
            login(request, form.get_user())
            request.session.pop("portal_next", None)
            if next_url:
                return redirect(next_url)
            return redirect("portal_ciudadano:mi_perfil")

        registrar_login_fallido(ip)
        return self.render_to_response(
            {
                "form": form,
                "next": next_url,
                "mostrar_boton_reclamo_anonimo": mostrar_boton_reclamo_anonimo,
                "anonimo_reclamo_url": self._build_anonymous_claim_url(next_url),
            }
        )


class PortalCiudadanoLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("portal_ciudadano:login")


class PortalCiudadanoAuthTemplateView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.groups.filter(name="Ciudadanos").exists():
            login_url = f"{reverse('portal_ciudadano:login')}?next={request.get_full_path()}"
            return redirect(login_url)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = getattr(self.request.user, "ciudadano_perfil", None)
        if not ciudadano:
            return context
        estados_cancelados_turno = [
            TurnoCiudadano.Estado.CANCELADO_SISTEMA,
            TurnoCiudadano.Estado.REPROGRAMADO_SISTEMA,
        ]
        qs_notifs = TurnoCiudadano.objects.filter(
            ciudadano=ciudadano,
            fecha__gte=date.today(),
            estado__in=estados_cancelados_turno,
        ).select_related("recurso__configuracion_turnos__tipo_tramite", "recurso__configuracion_turnos__sede")
        vistos = set(self.request.session.get("pc_notifs_turnos_vistas", []))
        notificaciones_base = list(
            qs_notifs
            .select_related("recurso__configuracion_turnos__tipo_tramite", "recurso__configuracion_turnos__sede")
            .order_by("-modificado", "-id")
        )
        notificaciones = []
        for turno in notificaciones_base:
            if getattr(turno, "fecha", None) and turno.fecha < date.today():
                continue
            # Si ya existe un nuevo turno vigente del mismo trámite, no se notifica más esta cancelación.
            tipo_tramite_id = None
            cfg = getattr(turno, "config_efectiva", None)
            if cfg and getattr(cfg, "tipo_tramite_id", None):
                tipo_tramite_id = cfg.tipo_tramite_id
            if not tipo_tramite_id:
                recurso_cfg = getattr(getattr(turno, "recurso", None), "configuracion_turnos", None)
                if recurso_cfg and getattr(recurso_cfg, "tipo_tramite_id", None):
                    tipo_tramite_id = recurso_cfg.tipo_tramite_id
            if tipo_tramite_id:
                marca = getattr(turno, "modificado", None) or getattr(turno, "creado", None) or timezone.now()
                existe_reemplazo = TurnoCiudadano.objects.filter(
                    ciudadano=ciudadano,
                    fecha__gte=date.today(),
                    estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
                    creado__gte=marca,
                ).filter(
                    Q(configuracion__tipo_tramite_id=tipo_tramite_id)
                    | Q(recurso__configuracion_turnos__tipo_tramite_id=tipo_tramite_id)
                ).exists()
                if existe_reemplazo:
                    continue
            motivo = (turno.notas_backoffice or "").strip()
            lineas = [ln.strip() for ln in motivo.splitlines() if ln.strip()]
            motivo_legible = "Sin detalle informado."
            for ln in reversed(lineas):
                if "[CANCELACION_SISTEMA]" in ln:
                    motivo_legible = ln.split("[CANCELACION_SISTEMA]", 1)[1].strip() or motivo_legible
                    break
                if "[RECHAZO_SISTEMA]" in ln:
                    motivo_legible = ln.split("[RECHAZO_SISTEMA]", 1)[1].strip() or motivo_legible
                    break
            if motivo_legible == "Sin detalle informado." and lineas:
                motivo_legible = lineas[-1]
            turno.motivo_notificacion_cancelacion = motivo_legible
            notificaciones.append(turno)
        turnos_count = len([t for t in notificaciones if t.pk not in vistos])
        turnos_notifs = []
        for turno in notificaciones[:5]:
            partes_subtitulo = []
            if getattr(turno, "fecha", None):
                try:
                    partes_subtitulo.append(turno.fecha.strftime("%d/%m/%Y"))
                except Exception:
                    pass
            if getattr(turno, "hora_inicio", None):
                try:
                    partes_subtitulo.append(turno.hora_inicio.strftime("%H:%M"))
                except Exception:
                    pass
            if getattr(turno, "codigo_turno", None):
                partes_subtitulo.append(turno.codigo_turno)

            cfg = getattr(turno, "config_efectiva", None)
            tipo_nombre = ""
            if cfg and getattr(cfg, "tipo_tramite", None):
                tipo_nombre = cfg.tipo_tramite.nombre or ""
            if not tipo_nombre:
                recurso_cfg = getattr(getattr(turno, "recurso", None), "configuracion_turnos", None)
                if recurso_cfg and getattr(recurso_cfg, "tipo_tramite", None):
                    tipo_nombre = recurso_cfg.tipo_tramite.nombre or ""

            motivo_txt = (turno.motivo_notificacion_cancelacion or "").strip() or "Sin detalle informado."
            if not partes_subtitulo and not tipo_nombre and not motivo_txt:
                continue

            turnos_notifs.append(
                {
                    "kind": "turno_cancelado_sistema",
                    "title": "Turno cancelado por sistema",
                    "subtitle": " - ".join(partes_subtitulo),
                    "detail": tipo_nombre or "Trámite",
                    "extra": f"Motivo: {motivo_txt}",
                    "url": reverse("portal_ciudadano:turnos"),
                    "pk": f"turno-{turno.pk}",
                    "sort_fecha": getattr(turno, "modificado", None) or getattr(turno, "creado", None),
                    "seen": turno.pk in vistos,
                }
            )

        vistos_solicitudes_raw = set(self.request.session.get("pc_notifs_solicitudes_vistas", []))
        vistos_reclamo_hist_ids = set()
        vistos_tramite_hist_ids = set()
        vistos_reclamo_final_hist_ids = set()
        vistos_tramite_final_hist_ids = set()
        for token in vistos_solicitudes_raw:
            token_str = str(token)
            if token_str.startswith("r:"):
                val = token_str.split(":", 1)[1]
                if val.isdigit():
                    vistos_reclamo_hist_ids.add(int(val))
            elif token_str.startswith("t:"):
                val = token_str.split(":", 1)[1]
                if val.isdigit():
                    vistos_tramite_hist_ids.add(int(val))
            elif token_str.startswith("fr:"):
                val = token_str.split(":", 1)[1]
                if val.isdigit():
                    vistos_reclamo_final_hist_ids.add(int(val))
            elif token_str.startswith("ft:"):
                val = token_str.split(":", 1)[1]
                if val.isdigit():
                    vistos_tramite_final_hist_ids.add(int(val))
        reclamos_solicitudes_qs = (
            ReclamoHistorial.objects.filter(
                reclamo__ciudadano=ciudadano,
                reclamo__activo=True,
                visible_ciudadano=True,
                accion="solicitud_datos_ciudadano",
            )
            .select_related("usuario", "reclamo")
            .order_by("-fecha", "-id")
        )
        tramites_solicitudes_qs = (
            TramiteHistorial.objects.filter(
                tramite__ciudadano=ciudadano,
                tramite__activo=True,
                visible_ciudadano=True,
                accion="solicitud_datos_ciudadano",
            )
            .select_related("usuario", "tramite")
            .order_by("-fecha", "-id")
        )
        solicitudes_notifs = []
        solicitudes_unseen_count = 0
        for h in reclamos_solicitudes_qs:
            ya_respondida = ReclamoHistorial.objects.filter(
                reclamo_id=h.reclamo_id,
                accion="respuesta_solicitud_datos_ciudadano",
                fecha__gte=h.fecha,
            ).exists()
            if ya_respondida:
                continue
            solicitudes_notifs.append(
                {
                    "kind": "solicitud_datos",
                    "title": "Actualizacion de datos solicitada",
                    "subtitle": h.reclamo.tipo_reclamo.nombre if getattr(h.reclamo, "tipo_reclamo", None) else "-",
                    "detail": "",
                    "extra": f"Nro: {h.reclamo.numero}" if getattr(h.reclamo, "numero", None) else "",
                    "url": reverse("portal_ciudadano:detalle_reclamo", kwargs={"pk": h.reclamo_id}),
                    "pk": f"solicitud-{h.pk}",
                    "historial_id": h.pk,
                    "sort_fecha": h.fecha,
                    "seen": h.pk in vistos_reclamo_hist_ids,
                }
            )
            if h.pk not in vistos_reclamo_hist_ids:
                solicitudes_unseen_count += 1
        for h in tramites_solicitudes_qs:
            ya_respondida = TramiteHistorial.objects.filter(
                tramite_id=h.tramite_id,
                accion="respuesta_solicitud_datos_ciudadano",
                fecha__gte=h.fecha,
            ).exists()
            if ya_respondida:
                continue
            solicitudes_notifs.append(
                {
                    "kind": "solicitud_datos",
                    "title": "Actualizacion de datos solicitada",
                    "subtitle": h.tramite.tipo_tramite.nombre if getattr(h.tramite, "tipo_tramite", None) else "-",
                    "detail": "",
                    "extra": f"Nro: {h.tramite.numero}" if getattr(h.tramite, "numero", None) else "",
                    "url": reverse("portal_ciudadano:detalle_tramite", kwargs={"pk": h.tramite_id}),
                    "pk": f"solicitud-{h.pk}",
                    "historial_id": h.pk,
                    "sort_fecha": h.fecha,
                    "seen": h.pk in vistos_tramite_hist_ids,
                }
            )
            if h.pk not in vistos_tramite_hist_ids:
                solicitudes_unseen_count += 1

        finalizados_notifs = []
        finalizados_unseen_count = 0
        reclamos_finalizados_qs = (
            ReclamoHistorial.objects.filter(
                reclamo__ciudadano=ciudadano,
                reclamo__activo=True,
                visible_ciudadano=True,
                accion="respuesta_operador_ciudadano",
            )
            .select_related("reclamo")
            .order_by("-fecha", "-id")
        )
        tramites_finalizados_qs = (
            TramiteHistorial.objects.filter(
                tramite__ciudadano=ciudadano,
                tramite__activo=True,
                visible_ciudadano=True,
                accion="respuesta_operador_ciudadano",
            )
            .select_related("tramite")
            .order_by("-fecha", "-id")
        )
        seen_reclamo_final = set()
        for h in reclamos_finalizados_qs:
            if h.reclamo_id in seen_reclamo_final:
                continue
            seen_reclamo_final.add(h.reclamo_id)
            if h.pk in vistos_reclamo_final_hist_ids:
                continue
            finalizados_notifs.append(
                {
                    "kind": "solicitud_finalizada",
                    "title": "Solicitud finalizada",
                    "subtitle": h.reclamo.tipo_reclamo.nombre if getattr(h.reclamo, "tipo_reclamo", None) else "-",
                    "detail": "",
                    "extra": f"Nro: {h.reclamo.numero}" if getattr(h.reclamo, "numero", None) else "",
                    "url": reverse("portal_ciudadano:detalle_reclamo", kwargs={"pk": h.reclamo_id}),
                    "pk": f"final-reclamo-{h.pk}",
                    "historial_id": h.pk,
                    "sort_fecha": h.fecha,
                    "seen": False,
                }
            )
            finalizados_unseen_count += 1
        seen_tramite_final = set()
        for h in tramites_finalizados_qs:
            if h.tramite_id in seen_tramite_final:
                continue
            seen_tramite_final.add(h.tramite_id)
            if h.pk in vistos_tramite_final_hist_ids:
                continue
            finalizados_notifs.append(
                {
                    "kind": "solicitud_finalizada",
                    "title": "Solicitud finalizada",
                    "subtitle": h.tramite.tipo_tramite.nombre if getattr(h.tramite, "tipo_tramite", None) else "-",
                    "detail": "",
                    "extra": f"Nro: {h.tramite.numero}" if getattr(h.tramite, "numero", None) else "",
                    "url": reverse("portal_ciudadano:detalle_tramite", kwargs={"pk": h.tramite_id}),
                    "pk": f"final-tramite-{h.pk}",
                    "historial_id": h.pk,
                    "sort_fecha": h.fecha,
                    "seen": False,
                }
            )
            finalizados_unseen_count += 1

        solicitudes_count = solicitudes_unseen_count + finalizados_unseen_count

        notificaciones_portal = sorted(
            (turnos_notifs + solicitudes_notifs + finalizados_notifs),
            key=lambda x: x.get("sort_fecha") or timezone.now(),
            reverse=True,
        )[:5]
        context["turnos_cancelados_count"] = turnos_count
        context["turnos_cancelados_notificaciones"] = notificaciones
        context["portal_notificaciones"] = notificaciones_portal
        context["portal_notificaciones_count"] = turnos_count + solicitudes_count
        return context


@require_POST
def portal_ciudadano_notificaciones_turnos_leidas(request):
    if not _is_ciudadano_user(request.user):
        return JsonResponse({"ok": False}, status=403)
    ciudadano = _get_ciudadano_from_user(request.user)
    if not ciudadano:
        return JsonResponse({"ok": False}, status=403)
    estados_cancelados_turno = [
        TurnoCiudadano.Estado.CANCELADO_SISTEMA,
        TurnoCiudadano.Estado.REPROGRAMADO_SISTEMA,
    ]
    ids = list(
        TurnoCiudadano.objects.filter(
            ciudadano=ciudadano,
            fecha__gte=date.today(),
            estado__in=estados_cancelados_turno,
        ).values_list("id", flat=True)
    )
    vistos = set(request.session.get("pc_notifs_turnos_vistas", []))
    vistos.update(ids)
    request.session["pc_notifs_turnos_vistas"] = list(vistos)
    solicitudes_reclamo_ids = list(
        ReclamoHistorial.objects.filter(
            reclamo__ciudadano=ciudadano,
            reclamo__activo=True,
            visible_ciudadano=True,
            accion="solicitud_datos_ciudadano",
        ).values_list("id", flat=True)
    )
    solicitudes_tramite_ids = list(
        TramiteHistorial.objects.filter(
            tramite__ciudadano=ciudadano,
            tramite__activo=True,
            visible_ciudadano=True,
            accion="solicitud_datos_ciudadano",
        ).values_list("id", flat=True)
    )
    vistas_solicitudes = set(request.session.get("pc_notifs_solicitudes_vistas", []))
    vistas_solicitudes.update({f"r:{pk}" for pk in solicitudes_reclamo_ids})
    vistas_solicitudes.update({f"t:{pk}" for pk in solicitudes_tramite_ids})
    final_reclamo_ids = list(
        ReclamoHistorial.objects.filter(
            reclamo__ciudadano=ciudadano,
            reclamo__activo=True,
            visible_ciudadano=True,
            accion="respuesta_operador_ciudadano",
        ).values_list("id", flat=True)
    )
    final_tramite_ids = list(
        TramiteHistorial.objects.filter(
            tramite__ciudadano=ciudadano,
            tramite__activo=True,
            visible_ciudadano=True,
            accion="respuesta_operador_ciudadano",
        ).values_list("id", flat=True)
    )
    vistas_solicitudes.update({f"fr:{pk}" for pk in final_reclamo_ids})
    vistas_solicitudes.update({f"ft:{pk}" for pk in final_tramite_ids})
    request.session["pc_notifs_solicitudes_vistas"] = list(vistas_solicitudes)
    request.session.modified = True
    return JsonResponse({"ok": True})


class PortalCiudadanoMiPerfilView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/mi_perfil.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = self.request.user.ciudadano_perfil
        genero = (getattr(ciudadano, "genero", "") or "").upper()
        if genero == "M":
            saludo_bienvenida = "Bienvenido"
        elif genero == "F":
            saludo_bienvenida = "Bienvenida"
        else:
            saludo_bienvenida = "Bienvenido/a"
        context["ciudadano"] = ciudadano
        context["saludo_bienvenida"] = saludo_bienvenida
        context.update(get_ciudadano_perfil_context(user=self.request.user, ciudadano=ciudadano))
        return context


class PortalCiudadanoMisSolicitudesView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/mis_solicitudes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = self.request.user.ciudadano_perfil
        query = (self.request.GET.get("q") or "").strip()
        tab = (self.request.GET.get("tab") or "reclamos").strip().lower()
        if tab not in {"reclamos", "tramites"}:
            tab = "reclamos"
        estado = (self.request.GET.get("estado") or "").strip()

        reclamos = (
            Reclamo.objects.filter(ciudadano=ciudadano, activo=True)
            .select_related("tipo_reclamo", "estado", "prioridad")
            .order_by("-fecha_ingreso", "-id")
        )
        tramites = (
            Tramite.objects.filter(ciudadano=ciudadano, activo=True)
            .select_related("tipo_tramite", "estado", "prioridad")
            .order_by("-fecha_inicio", "-id")
        )

        if query:
            reclamos = reclamos.filter(Q(numero__icontains=query) | Q(titulo__icontains=query))
            tramites = tramites.filter(Q(numero__icontains=query) | Q(titulo__icontains=query))

        if estado:
            if tab == "reclamos":
                reclamos = reclamos.filter(estado__nombre__iexact=estado)
            else:
                tramites = tramites.filter(estado__nombre__iexact=estado)

        for item in reclamos:
            item.estado_badge_class = _estado_badge_class(getattr(getattr(item, "estado", None), "nombre", ""))
        for item in tramites:
            item.estado_badge_class = _estado_badge_class(getattr(getattr(item, "estado", None), "nombre", ""))

        if tab == "reclamos":
            estados_disponibles = sorted(
                {
                    e
                    for e in Reclamo.objects.filter(ciudadano=ciudadano, activo=True)
                    .values_list("estado__nombre", flat=True)
                    .distinct()
                    if e
                }
            )
        else:
            estados_disponibles = sorted(
                {
                    e
                    for e in Tramite.objects.filter(ciudadano=ciudadano, activo=True)
                    .values_list("estado__nombre", flat=True)
                    .distinct()
                    if e
                }
            )

        context.update(
            {
                "ciudadano": ciudadano,
                "reclamos": reclamos,
                "tramites": tramites,
                "filtro_q": query,
                "active_tab": tab,
                "filtro_estado": estado,
                "estados_disponibles": estados_disponibles,
                "show_reclamos": tab == "reclamos",
                "show_tramites": tab == "tramites",
                "reclamos_count": Reclamo.objects.filter(ciudadano=ciudadano, activo=True).count(),
                "tramites_count": Tramite.objects.filter(ciudadano=ciudadano, activo=True).count(),
            }
        )
        return context


def portal_ciudadano_mis_programas(request):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    ciudadano = request.user.ciudadano_perfil
    context = {"ciudadano": ciudadano}
    context.update(get_ciudadano_programas_context(ciudadano))
    return render(request, "portal_ciudadano/programas.html", context)


def portal_ciudadano_programa_detalle(request, pk):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    ciudadano = request.user.ciudadano_perfil
    inscripcion = get_ciudadano_programa_detalle_or_404(ciudadano, pk)
    return render(
        request,
        "portal_ciudadano/programa_detalle.html",
        {
            "ciudadano": ciudadano,
            "inscripcion": inscripcion,
            "derivaciones": get_ciudadano_programa_derivaciones(ciudadano, inscripcion.programa),
        },
    )


def portal_ciudadano_mis_turnos(request):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    ciudadano = request.user.ciudadano_perfil
    context = {"ciudadano": ciudadano}
    context.update(get_turnos_ciudadano_contexto(ciudadano))
    return render(request, "portal_ciudadano/turnos.html", context)


def portal_ciudadano_solicitar_turno(request):
    modo = (request.GET.get("modo") or "sede").strip().lower()
    if modo not in {"sede", "fecha"}:
        modo = "sede"

    ciudadano = _get_ciudadano_from_user(request.user)
    recursos = list(get_recursos_turnos_activos())
    recursos_por_tipo = {}
    for recurso in recursos:
        recursos_por_tipo.setdefault(recurso.get_tipo_display(), []).append(recurso)

    return render(
        request,
        "portal_ciudadano/turnos_solicitar.html",
        {
            "ciudadano": ciudadano,
            "modo": modo,
            "recursos": recursos,
            "recursos_por_tipo": recursos_por_tipo,
            "today_iso": date.today().isoformat(),
        },
    )


def portal_ciudadano_turno_calendario(request, recurso_id):
    ciudadano = _get_ciudadano_from_user(request.user)
    recurso = get_recurso_turnos_activo_or_404(recurso_id)
    hoy = date.today()
    anio = int(request.GET.get("anio", hoy.year))
    mes = int(request.GET.get("mes", hoy.month))
    calendario = get_calendario_mensual(recurso, anio, mes)
    mes_anterior = {"anio": anio - 1, "mes": 12} if mes == 1 else {"anio": anio, "mes": mes - 1}
    mes_siguiente = {"anio": anio + 1, "mes": 1} if mes == 12 else {"anio": anio, "mes": mes + 1}

    return render(
        request,
        "portal_ciudadano/turnos_calendario.html",
        {
            "ciudadano": ciudadano,
            "recurso": recurso,
            "calendario": calendario,
            "anio": anio,
            "mes": mes,
            "mes_nombre": date(anio, mes, 1).strftime("%B %Y").capitalize(),
            "mes_anterior": mes_anterior,
            "mes_siguiente": mes_siguiente,
            "primer_dia_offset": range(date(anio, mes, 1).weekday()),
        },
    )


def portal_ciudadano_turno_slots(request, recurso_id):
    recurso = get_recurso_turnos_activo_or_404(recurso_id)
    try:
        fecha = date.fromisoformat(request.GET.get("fecha"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Fecha inválida"}, status=400)
    if fecha < date.today():
        return JsonResponse({"error": "No se pueden solicitar turnos para fechas pasadas"}, status=400)
    slots = get_slots_disponibles(recurso, fecha)
    return JsonResponse(
        {
            "slots": [
                {
                    "hora_inicio": slot["hora_inicio"].strftime("%H:%M"),
                    "hora_fin": slot["hora_fin"].strftime("%H:%M"),
                    "disponible": slot["disponible"],
                }
                for slot in slots
            ]
        }
    )


def portal_ciudadano_turnos_disponibles_por_fecha(request):
    try:
        fecha = date.fromisoformat(request.GET.get("fecha"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "Fecha invalida"}, status=400)

    hoy = date.today()
    if fecha < hoy:
        return JsonResponse({"error": "No se pueden solicitar turnos para fechas pasadas"}, status=400)

    tipo = None
    tipo_id_raw = (request.GET.get("tipo_id") or "").strip()
    if tipo_id_raw.isdigit():
        tipo = TipoTramite.objects.filter(id=int(tipo_id_raw), activo=True).first()
        if not tipo:
            return JsonResponse({"error": "Tipo de tramite invalido"}, status=400)

    max_dias = 10
    cfg_qs = ConfiguracionTurnos.objects.filter(activo=True)
    if tipo:
        cfg_qs = cfg_qs.filter(tipo_tramite=tipo)
    cfg_max = (
        cfg_qs.exclude(anticipacion_maxima_dias__isnull=True)
        .order_by("-anticipacion_maxima_dias")
        .values_list("anticipacion_maxima_dias", flat=True)
        .first()
    )
    if cfg_max:
        max_dias = int(cfg_max)

    fecha_max = hoy + timedelta(days=max_dias)
    if fecha > fecha_max:
        return JsonResponse(
            {
                "error": f"La fecha seleccionada supera el maximo permitido ({max_dias} dias).",
                "max_fecha": fecha_max.isoformat(),
            },
            status=400,
        )

    recursos = get_recursos_turnos_activos()
    if tipo:
        recursos = recursos.filter(configuracion_turnos__tipo_tramite=tipo, configuracion_turnos__activo=True)
    recursos_disponibles = []
    for recurso in recursos:
        cfg = getattr(recurso, "configuracion_turnos", None)
        if cfg and getattr(cfg, "anticipacion_maxima_dias", None) is not None:
            try:
                max_recurso = int(cfg.anticipacion_maxima_dias)
            except (TypeError, ValueError):
                max_recurso = None
            if max_recurso is not None and fecha > (hoy + timedelta(days=max_recurso)):
                continue
        slots_disponibles = []
        for slot in get_slots_disponibles(recurso, fecha):
            if not slot["disponible"]:
                continue
            slots_disponibles.append(
                {
                    "hora_inicio": slot["hora_inicio"].strftime("%H:%M"),
                    "hora_fin": slot["hora_fin"].strftime("%H:%M"),
                    "cupo_restante": int(slot.get("cupo_restante", 0)),
                    "confirmar_url": (
                        reverse("portal_ciudadano:confirmar_turno", kwargs={"recurso_id": recurso.id})
                        + f"?fecha={fecha.isoformat()}&hora_inicio={slot['hora_inicio'].strftime('%H:%M')}"
                        + f"&hora_fin={slot['hora_fin'].strftime('%H:%M')}"
                    ),
                }
            )
        recursos_disponibles.append(
            {
                "id": recurso.id,
                "nombre": recurso.nombre,
                "sede_nombre": (
                    recurso.configuracion_turnos.sede.nombre
                    if getattr(recurso, "configuracion_turnos", None)
                    and getattr(recurso.configuracion_turnos, "sede", None)
                    else recurso.nombre
                ),
                "tipo": recurso.get_tipo_display(),
                "direccion": recurso.direccion,
                "slots": slots_disponibles,
            }
        )

    return JsonResponse(
        {
            "fecha": fecha.isoformat(),
            "recursos": recursos_disponibles,
        }
    )


def portal_ciudadano_agenda_sede(request, recurso_id):
    recurso = get_recurso_turnos_activo_or_404(recurso_id)
    dias_default = 10
    if getattr(recurso, "configuracion_turnos_id", None):
        cfg = getattr(recurso, "configuracion_turnos", None)
        if cfg and getattr(cfg, "anticipacion_maxima_dias", None):
            dias_default = int(cfg.anticipacion_maxima_dias)
    dias = max(1, min(int(request.GET.get("dias", dias_default) or dias_default), 90))
    hoy = date.today()
    agenda = []
    for i in range(dias):
        fecha = hoy + timedelta(days=i)
        slots = []
        for slot in get_slots_disponibles(recurso, fecha):
            if not slot["disponible"]:
                continue
            hora_inicio = slot["hora_inicio"].strftime("%H:%M")
            hora_fin = slot["hora_fin"].strftime("%H:%M")
            params = f"fecha={fecha.isoformat()}&hora_inicio={hora_inicio}&hora_fin={hora_fin}"
            slots.append(
                {
                    "hora_inicio": hora_inicio,
                    "hora_fin": hora_fin,
                    "cupo_restante": int(slot.get("cupo_restante", 0)),
                    "confirmar_url": reverse("portal_ciudadano:confirmar_turno", kwargs={"recurso_id": recurso.id}) + f"?{params}",
                }
            )
        if slots:
            agenda.append({"fecha": fecha.isoformat(), "slots": slots})
    return JsonResponse(
        {
            "recurso": {
                "id": recurso.id,
                "nombre": recurso.nombre,
                "direccion": recurso.direccion,
            },
            "agenda": agenda,
        }
    )


def portal_ciudadano_agenda_general(request):
    dias_default = 10
    cfg_max = (
        ConfiguracionTurnos.objects.filter(activo=True)
        .order_by("-anticipacion_maxima_dias")
        .values_list("anticipacion_maxima_dias", flat=True)
        .first()
    )
    if cfg_max:
        dias_default = int(cfg_max)
    dias = max(1, min(int(request.GET.get("dias", dias_default) or dias_default), 90))
    hoy = date.today()
    recursos = get_recursos_turnos_activos()
    resultado = []
    for i in range(dias):
        fecha = hoy + timedelta(days=i)
        recursos_fecha = []
        for recurso in recursos:
            slots = []
            for slot in get_slots_disponibles(recurso, fecha):
                if not slot["disponible"]:
                    continue
                hora_inicio = slot["hora_inicio"].strftime("%H:%M")
                hora_fin = slot["hora_fin"].strftime("%H:%M")
                params = f"fecha={fecha.isoformat()}&hora_inicio={hora_inicio}&hora_fin={hora_fin}"
                slots.append(
                    {
                        "hora_inicio": hora_inicio,
                        "hora_fin": hora_fin,
                        "cupo_restante": int(slot.get("cupo_restante", 0)),
                        "confirmar_url": reverse("portal_ciudadano:confirmar_turno", kwargs={"recurso_id": recurso.id}) + f"?{params}",
                    }
                )
            if slots:
                recursos_fecha.append(
                    {
                        "id": recurso.id,
                        "nombre": recurso.nombre,
                        "sede_nombre": (
                            recurso.configuracion_turnos.sede.nombre
                            if getattr(recurso, "configuracion_turnos", None)
                            and getattr(recurso.configuracion_turnos, "sede", None)
                            else recurso.nombre
                        ),
                        "direccion": recurso.direccion,
                        "slots": slots,
                    }
                )
        if recursos_fecha:
            resultado.append({"fecha": fecha.isoformat(), "recursos": recursos_fecha})
    return JsonResponse({"agenda": resultado})


def portal_ciudadano_confirmar_turno(request, recurso_id):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    ciudadano = request.user.ciudadano_perfil
    recurso = get_recurso_turnos_activo_or_404(recurso_id)
    form = CiudadanoConfirmarTurnoForm(request.POST or None, initial=request.GET or None)
    volver_url = request.META.get("HTTP_REFERER") or reverse("portal_ciudadano:tramites")
    if "/portal-ciudadano/turnos/solicitar/" in str(volver_url) and "/calendario/" in str(volver_url):
        volver_url = reverse("portal_ciudadano:tramites")

    tipo_tramite = None
    if getattr(recurso, "configuracion_turnos", None) and getattr(recurso.configuracion_turnos, "tipo_tramite", None):
        tipo_tramite = recurso.configuracion_turnos.tipo_tramite

    bloqueo_mensaje = ""
    aviso_reemplazo_turno = ""
    aviso_turno_detalle = {}
    turno_activo_mismo_tipo = None
    if tipo_tramite:
        tramite_abierto = _get_tramite_abierto_mismo_tipo(ciudadano, tipo_tramite)
        if tramite_abierto:
            bloqueo_mensaje = (
                f"Ya tenes un tramite iniciado de este tipo ({tramite_abierto.numero}). "
                "No podes solicitar otro turno para el mismo tramite."
            )
        else:
            turno_activo_mismo_tipo = _get_turno_activo_mismo_tipo(ciudadano, tipo_tramite)
            if turno_activo_mismo_tipo:
                sede_turno_vigente = ""
                if getattr(turno_activo_mismo_tipo, "config_efectiva", None) and getattr(
                    turno_activo_mismo_tipo.config_efectiva, "sede", None
                ):
                    sede_turno_vigente = turno_activo_mismo_tipo.config_efectiva.sede.nombre
                elif getattr(turno_activo_mismo_tipo, "recurso", None):
                    sede_turno_vigente = turno_activo_mismo_tipo.recurso.nombre
                aviso_turno_detalle = {
                    "codigo": turno_activo_mismo_tipo.codigo_turno,
                    "sede": sede_turno_vigente or "-",
                    "fecha": turno_activo_mismo_tipo.fecha.strftime("%d/%m/%Y"),
                    "hora_inicio": turno_activo_mismo_tipo.hora_inicio.strftime("%H:%M"),
                    "hora_fin": turno_activo_mismo_tipo.hora_fin.strftime("%H:%M"),
                }
                aviso_reemplazo_turno = (
                    "Ya tenes un turno vigente para este tramite. "
                    "Si confirmas este nuevo turno, el anterior se cancelara automaticamente."
                )

    if bloqueo_mensaje and request.method == "POST":
        messages.error(request, bloqueo_mensaje)
        return redirect(request.get_full_path())

    if request.method == "POST" and form.is_valid():
        try:
            turno = reservar_turno_ciudadano(
                ciudadano=ciudadano,
                recurso=recurso,
                fecha=form.cleaned_data["fecha"],
                hora_inicio=form.cleaned_data["hora_inicio"],
                hora_fin=form.cleaned_data["hora_fin"],
                motivo=form.cleaned_data["motivo"],
            )
        except TurnoNoDisponibleError as exc:
            messages.error(request, str(exc))
            return redirect(volver_url)
        if turno_activo_mismo_tipo and turno_activo_mismo_tipo.id != turno.id:
            turno_activo_mismo_tipo.estado = TurnoCiudadano.Estado.REPROGRAMADO_CIUDADANO
            turno_activo_mismo_tipo.save(update_fields=["estado", "modificado"])
            turno.reemplaza_turno = turno_activo_mismo_tipo
            turno.save(update_fields=["reemplaza_turno", "modificado"])
            turno_activo_mismo_tipo.reemplazado_por_turno = turno
            turno_activo_mismo_tipo.save(update_fields=["reemplazado_por_turno", "modificado"])
        return redirect("portal_ciudadano:turno_confirmado", pk=turno.pk)

    if request.method == "POST" and not form.is_valid():
        messages.error(request, "Datos del turno invalidos. Intenta de nuevo.")
        return redirect(volver_url)

    fecha_fmt = request.GET.get("fecha") or "-"
    hora_inicio_fmt = request.GET.get("hora_inicio") or "-"
    if form.is_valid():
        fecha_val = form.cleaned_data.get("fecha")
        hora_val = form.cleaned_data.get("hora_inicio")
        if fecha_val:
            fecha_fmt = fecha_val.strftime("%d/%m/%Y")
        if hora_val:
            hora_inicio_fmt = hora_val.strftime("%H:%M")

    sede_nombre = recurso.nombre
    if getattr(recurso, "configuracion_turnos", None) and getattr(recurso.configuracion_turnos, "sede", None):
        sede_nombre = recurso.configuracion_turnos.sede.nombre

    tramite_nombre = tipo_tramite.nombre if tipo_tramite else ""

    return render(
        request,
        "portal_ciudadano/turnos_confirmar.html",
        {
            "ciudadano": ciudadano,
            "recurso": recurso,
            "sede_nombre": sede_nombre,
            "tramite_nombre": tramite_nombre,
            "fecha": fecha_fmt,
            "hora_inicio": hora_inicio_fmt,
            "hora_fin": request.GET.get("hora_fin"),
            "form": form,
            "volver_url": volver_url,
            "bloqueo_mensaje": bloqueo_mensaje,
            "aviso_reemplazo_turno": aviso_reemplazo_turno,
            "aviso_turno_detalle": aviso_turno_detalle,
        },
    )

def portal_ciudadano_turno_confirmado(request, pk):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    ciudadano = request.user.ciudadano_perfil
    return render(
        request,
        "portal_ciudadano/turnos_confirmado.html",
        {"ciudadano": ciudadano, "turno": get_turno_ciudadano_or_404(ciudadano, pk)},
    )


def portal_ciudadano_cancelar_turno(request, pk):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    ciudadano = request.user.ciudadano_perfil
    turno = get_turno_ciudadano_or_404(ciudadano, pk)
    if request.method == "POST":
        if cancelar_turno_ciudadano(turno):
            messages.success(request, f'Tu turno del {turno.fecha.strftime("%d/%m/%Y")} fue cancelado.')
        return redirect("portal_ciudadano:turnos")
    return render(request, "portal_ciudadano/turnos_cancelar.html", {"ciudadano": ciudadano, "turno": turno})


class PortalCiudadanoReclamoDetalleSolicitudView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/solicitud_detalle.html"

    @staticmethod
    def _get_reclamo_ciudadano(ciudadano, pk):
        return get_object_or_404(
            Reclamo.objects.select_related(
                "tipo_reclamo",
                "estado",
                "prioridad",
                "area_actual",
                "area_responsable",
                "municipio",
                "localidad",
                "provincia",
            ).prefetch_related(
                "datos_dinamicos__campo",
                "adjuntos",
                "historial__estado_nuevo",
                "historial__area_nueva",
                "historial__usuario",
            ),
            pk=pk,
            ciudadano=ciudadano,
            activo=True,
        )

    @staticmethod
    def _extract_campo_objetivo(solicitud):
        campo_objetivo = ((getattr(solicitud, "metadata", None) or {}).get("campo_objetivo") or "").strip()
        if campo_objetivo:
            return campo_objetivo
        comentario_src = (getattr(solicitud, "comentario", "") or "").strip()
        if "campo_dinamico:" in comentario_src:
            try:
                return "campo_dinamico:" + comentario_src.split("campo_dinamico:", 1)[1].split("'", 1)[0]
            except Exception:
                return ""
        return ""

    @classmethod
    def _get_solicitudes_datos_pendientes(cls, reclamo):
        solicitudes = list(
            reclamo.historial.filter(accion="solicitud_datos_ciudadano", visible_ciudadano=True).order_by("-fecha", "-id")
        )
        pendientes = []
        for solicitud in solicitudes:
            respuesta = (
                reclamo.historial.filter(
                    accion="respuesta_solicitud_datos_ciudadano",
                    fecha__gte=solicitud.fecha,
                    metadata__solicitud_origen_id=solicitud.id,
                )
                .order_by("-fecha", "-id")
                .first()
            )
            if respuesta:
                continue
            pendientes.append(solicitud)
        return pendientes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = self.request.user.ciudadano_perfil
        reclamo = self._get_reclamo_ciudadano(ciudadano, kwargs["pk"])
        solicitudes_datos_pendientes = self._get_solicitudes_datos_pendientes(reclamo)
        for solicitud in solicitudes_datos_pendientes:
            solicitud.comentario_label = _format_historial_comentario(getattr(solicitud, "comentario", ""))
            solicitud.campo_objetivo = self._extract_campo_objetivo(solicitud)
            solicitud.es_campo_dinamico = solicitud.campo_objetivo.startswith("campo_dinamico:")
            solicitud.input_name = f"valor_solicitud_{solicitud.id}"
            solicitud.input_type = "text"
            if solicitud.es_campo_dinamico:
                nombre_campo = solicitud.campo_objetivo.split(":", 1)[1].strip()
                campo = CampoDinamicoReclamo.objects.filter(
                    tipo_reclamo=reclamo.tipo_reclamo,
                    nombre__iexact=nombre_campo,
                    activo=True,
                ).first()
                solicitud.campo_dinamico = campo
                if campo and campo.tipo_dato == CampoDinamicoReclamo.TipoDato.ARCHIVO:
                    solicitud.input_type = "file"
            elif solicitud.campo_objetivo == "adjuntos_imagenes":
                solicitud.input_type = "file"
        historial = list(reclamo.historial.filter(visible_ciudadano=True).all()[:30])
        for h in historial:
            h.accion_label = _format_historial_accion(getattr(h, "accion", ""))
            h.comentario_label = _format_historial_comentario(getattr(h, "comentario", ""))
        adjuntos_activos = list(reclamo.adjuntos.filter(activo=True))
        datos_dinamicos_list = list(reclamo.datos_dinamicos.all())
        adjuntos_por_nombre = {}
        for a in adjuntos_activos:
            nombre = (a.nombre_original or "").strip()
            if nombre:
                adjuntos_por_nombre[nombre] = a
        for item in datos_dinamicos_list:
            item.valor_preview_url = ""
            if getattr(getattr(item, "campo", None), "tipo_dato", "") == "archivo":
                valor_raw = str(getattr(item, "valor", "") or "").strip()
                if valor_raw.startswith("http://") or valor_raw.startswith("https://") or valor_raw.startswith("/"):
                    item.valor_preview_url = valor_raw
                elif valor_raw in adjuntos_por_nombre and getattr(adjuntos_por_nombre[valor_raw], "archivo", None):
                    item.valor_preview_url = adjuntos_por_nombre[valor_raw].archivo.url
        cierre_info = None
        cierre_adjuntos_ids = set()
        cierre_hist = (
            reclamo.historial.filter(accion="respuesta_operador_ciudadano", visible_ciudadano=True)
            .order_by("-fecha", "-id")
            .first()
        )
        if cierre_hist:
            cierre_meta = getattr(cierre_hist, "metadata", None) or {}
            comentario_id = cierre_meta.get("comentario_id")
            comentario_cierre = None
            if comentario_id:
                comentario_cierre = ReclamoComentario.objects.filter(id=comentario_id, reclamo=reclamo).first()
            observacion = (getattr(comentario_cierre, "comentario", "") or "").strip() or (
                getattr(cierre_hist, "comentario", "") or ""
            ).strip()
            observacion = _normalize_html_links(observacion)
            cantidad_adjuntos = 0
            try:
                cantidad_adjuntos = int(cierre_meta.get("adjuntos_nuevos") or 0)
            except (TypeError, ValueError):
                cantidad_adjuntos = 0
            adjuntos_cierre = []
            if cantidad_adjuntos > 0:
                adjuntos_cierre = list(reclamo.adjuntos.filter(activo=True).order_by("-created_at", "-id")[:cantidad_adjuntos])
                adjuntos_cierre.reverse()
                cierre_adjuntos_ids = {a.id for a in adjuntos_cierre if getattr(a, "id", None)}
            cierre_info = {
                "fecha": cierre_hist.fecha,
                "observacion": observacion,
                "adjuntos": adjuntos_cierre,
            }
        adjuntos_generales = [a for a in adjuntos_activos if a.id not in cierre_adjuntos_ids]

        context.update(
            {
                "ciudadano": ciudadano,
                "solicitud_tipo": "reclamo",
                "solicitud_obj": reclamo,
                "solicitud_label": "Reclamo",
                "tipo_label": "Sub?rea",
                "tipo_nombre": reclamo.tipo_reclamo.nombre,
                "fecha_label": "Fecha de ingreso",
                "fecha_valor": reclamo.fecha_ingreso,
                "datos_dinamicos": datos_dinamicos_list,
                "adjuntos": adjuntos_generales,
                "historial": historial,
                "solicitudes_datos_pendientes": solicitudes_datos_pendientes,
                "cierre_info": cierre_info,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        ciudadano = request.user.ciudadano_perfil
        reclamo = self._get_reclamo_ciudadano(ciudadano, kwargs["pk"])
        solicitudes_pendientes = self._get_solicitudes_datos_pendientes(reclamo)
        if not solicitudes_pendientes:
            messages.error(request, "No hay solicitudes de datos pendientes para este reclamo.")
            return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)

        solicitud_map = {s.id: s for s in solicitudes_pendientes}
        try:
            solicitud_id = int(request.POST.get("solicitud_id") or 0)
        except (TypeError, ValueError):
            solicitud_id = 0
        solicitud = solicitud_map.get(solicitud_id)
        if not solicitud:
            messages.error(request, "La solicitud seleccionada no es v?lida.")
            return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)

        campo_objetivo = self._extract_campo_objetivo(solicitud)
        if not campo_objetivo:
            messages.error(request, "No se indic? el campo a actualizar.")
            return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)

        detalle = []
        with transaction.atomic():
            campos_actualizados = []
            campos_valores = []

            if campo_objetivo.startswith("campo_dinamico:"):
                nombre_campo = campo_objetivo.split(":", 1)[1].strip()
                campo = CampoDinamicoReclamo.objects.filter(
                    tipo_reclamo=reclamo.tipo_reclamo,
                    nombre__iexact=nombre_campo,
                    activo=True,
                ).first()
                if not campo:
                    messages.error(request, "No se encontr? el campo din?mico solicitado.")
                    return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)

                input_name = f"valor_solicitud_{solicitud.id}"
                if campo.tipo_dato == CampoDinamicoReclamo.TipoDato.ARCHIVO:
                    uploaded = request.FILES.get(input_name)
                    if not uploaded:
                        messages.error(request, "Debes adjuntar el archivo solicitado.")
                        return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)
                    adjunto = ReclamoAdjunto(
                        reclamo=reclamo,
                        nombre_original=uploaded.name,
                        tipo_mime=getattr(uploaded, "content_type", "") or "",
                        subido_por=request.user if request.user.is_authenticated else None,
                        visible_ciudadano=True,
                    )
                    adjunto.archivo.save(uploaded.name, uploaded, save=False)
                    adjunto.save()
                    valor_nuevo = uploaded.name
                    campos_valores.append(
                        {
                            "campo": campo.nombre,
                            "tipo": "archivo",
                            "valor": uploaded.name,
                            "url": adjunto.archivo.url,
                        }
                    )
                else:
                    valor_nuevo = (request.POST.get(input_name) or "").strip()
                    if not valor_nuevo:
                        messages.error(request, "Debes completar el nuevo valor solicitado.")
                        return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)
                    campos_valores.append({"campo": campo.nombre, "tipo": "texto", "valor": valor_nuevo})

                ReclamoDatoDinamico.objects.update_or_create(
                    reclamo=reclamo,
                    campo=campo,
                    defaults={"valor": valor_nuevo, "activo": True},
                )
                campos_actualizados.append(campo.nombre)
            elif campo_objetivo == "adjuntos_imagenes":
                input_name = f"valor_solicitud_{solicitud.id}"
                uploaded = request.FILES.get(input_name)
                if not uploaded:
                    messages.error(request, "Debes adjuntar el archivo solicitado.")
                    return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)
                adjunto = ReclamoAdjunto(
                    reclamo=reclamo,
                    nombre_original=uploaded.name,
                    tipo_mime=getattr(uploaded, "content_type", "") or "",
                    subido_por=request.user if request.user.is_authenticated else None,
                    visible_ciudadano=True,
                )
                adjunto.archivo.save(uploaded.name, uploaded, save=False)
                adjunto.save()
                campos_actualizados.append("adjuntos_imagenes")
                campos_valores.append(
                    {
                        "campo": "adjuntos_imagenes",
                        "tipo": "archivo",
                        "valor": uploaded.name,
                        "url": adjunto.archivo.url,
                    }
                )
            else:
                input_name = f"valor_solicitud_{solicitud.id}"
                valor_nuevo = (request.POST.get(input_name) or "").strip()
                if not valor_nuevo:
                    messages.error(request, "Debes completar el nuevo valor solicitado.")
                    return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)
                if hasattr(reclamo, campo_objetivo):
                    setattr(reclamo, campo_objetivo, valor_nuevo)
                    reclamo.save(update_fields=[campo_objetivo, "updated_at"])
                    campos_actualizados.append(campo_objetivo)
                    campos_valores.append({"campo": campo_objetivo, "tipo": "texto", "valor": valor_nuevo})
                else:
                    messages.error(request, "El campo solicitado no es v?lido.")
                    return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)

            if campos_actualizados:
                detalle.append(f"Campos actualizados: {', '.join(campos_actualizados)}")
            detalle_texto = "\n".join(detalle) if detalle else "El ciudadano respondi? a la solicitud de datos."

            registrar_historial_reclamo(
                reclamo=reclamo,
                accion="respuesta_solicitud_datos_ciudadano",
                usuario=request.user if request.user.is_authenticated else None,
                estado_nuevo=reclamo.estado,
                area_nueva=reclamo.area_actual,
                comentario=detalle_texto,
                visible_ciudadano=True,
                metadata={
                    "origen": "portal_ciudadano",
                    "solicitud_origen_id": solicitud.id,
                    "campos_actualizados": campos_actualizados,
                    "campos_valores": campos_valores,
                },
            )

        messages.success(request, "La informaci?n solicitada fue actualizada correctamente.")
        return redirect("portal_ciudadano:detalle_reclamo", pk=reclamo.pk)


class PortalCiudadanoTramiteDetalleSolicitudView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/solicitud_detalle.html"

    @staticmethod
    def _extract_campo_objetivo(solicitud):
        campo_objetivo = ((getattr(solicitud, "metadata", None) or {}).get("campo_objetivo") or "").strip()
        if campo_objetivo:
            return campo_objetivo
        comentario_src = (getattr(solicitud, "comentario", "") or "").strip()
        if "campo_dinamico:" in comentario_src:
            try:
                return "campo_dinamico:" + comentario_src.split("campo_dinamico:", 1)[1].split("'", 1)[0]
            except Exception:
                return ""
        return ""

    @classmethod
    def _get_solicitudes_datos_pendientes(cls, tramite):
        solicitudes = list(
            tramite.historial.filter(accion="solicitud_datos_ciudadano", visible_ciudadano=True).order_by("-fecha", "-id")
        )
        pendientes = []
        for solicitud in solicitudes:
            respuesta = (
                tramite.historial.filter(
                    accion="respuesta_solicitud_datos_ciudadano",
                    fecha__gte=solicitud.fecha,
                    metadata__solicitud_origen_id=solicitud.id,
                )
                .order_by("-fecha", "-id")
                .first()
            )
            if respuesta:
                continue
            pendientes.append(solicitud)
        return pendientes

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = self.request.user.ciudadano_perfil
        tramite = get_object_or_404(
            Tramite.objects.select_related(
                "tipo_tramite",
                "estado",
                "prioridad",
                "area_actual",
                "area_responsable",
                "municipio",
                "localidad",
                "provincia",
            ).prefetch_related(
                "datos_dinamicos__campo",
                "adjuntos",
                "historial__estado_nuevo",
                "historial__area_nueva",
                "historial__usuario",
            ),
            pk=kwargs["pk"],
            ciudadano=ciudadano,
            activo=True,
        )
        solicitudes_datos_pendientes = self._get_solicitudes_datos_pendientes(tramite)
        for solicitud in solicitudes_datos_pendientes:
            solicitud.comentario_label = _format_historial_comentario(getattr(solicitud, "comentario", ""))
            solicitud.campo_objetivo = self._extract_campo_objetivo(solicitud)
            solicitud.es_campo_dinamico = solicitud.campo_objetivo.startswith("campo_dinamico:")
            solicitud.input_name = f"valor_solicitud_{solicitud.id}"
            solicitud.input_type = "text"
            if solicitud.es_campo_dinamico:
                nombre_campo = solicitud.campo_objetivo.split(":", 1)[1].strip()
                campo = CampoDinamicoTramite.objects.filter(
                    tipo_tramite=tramite.tipo_tramite,
                    nombre__iexact=nombre_campo,
                    activo=True,
                ).first()
                solicitud.campo_dinamico = campo
                if campo and campo.tipo_dato == CampoDinamicoTramite.TipoDato.ARCHIVO:
                    solicitud.input_type = "file"
        historial = list(tramite.historial.filter(visible_ciudadano=True).all()[:30])
        for h in historial:
            h.accion_label = _format_historial_accion(getattr(h, "accion", ""))
            h.comentario_label = _format_historial_comentario(getattr(h, "comentario", ""))
        adjuntos_activos = list(tramite.adjuntos.filter(activo=True))
        datos_dinamicos_list = list(tramite.datos_dinamicos.all())
        adjuntos_por_nombre = {}
        for a in adjuntos_activos:
            nombre = (a.nombre_original or "").strip()
            if nombre:
                adjuntos_por_nombre[nombre] = a
        for item in datos_dinamicos_list:
            item.valor_preview_url = ""
            if getattr(getattr(item, "campo", None), "tipo_dato", "") == "archivo":
                valor_raw = str(getattr(item, "valor", "") or "").strip()
                if valor_raw.startswith("http://") or valor_raw.startswith("https://") or valor_raw.startswith("/"):
                    item.valor_preview_url = valor_raw
                elif valor_raw in adjuntos_por_nombre and getattr(adjuntos_por_nombre[valor_raw], "archivo", None):
                    item.valor_preview_url = adjuntos_por_nombre[valor_raw].archivo.url
        cierre_info = None
        cierre_adjuntos_ids = set()
        cierre_hist = (
            tramite.historial.filter(accion="respuesta_operador_ciudadano", visible_ciudadano=True)
            .order_by("-fecha", "-id")
            .first()
        )
        if cierre_hist:
            cierre_meta = getattr(cierre_hist, "metadata", None) or {}
            comentario_id = cierre_meta.get("comentario_id")
            comentario_cierre = None
            if comentario_id:
                comentario_cierre = TramiteComentario.objects.filter(id=comentario_id, tramite=tramite).first()
            observacion = (getattr(comentario_cierre, "comentario", "") or "").strip() or (
                getattr(cierre_hist, "comentario", "") or ""
            ).strip()
            observacion = _normalize_html_links(observacion)
            cantidad_adjuntos = 0
            try:
                cantidad_adjuntos = int(cierre_meta.get("adjuntos_nuevos") or 0)
            except (TypeError, ValueError):
                cantidad_adjuntos = 0
            adjuntos_cierre = []
            if cantidad_adjuntos > 0:
                adjuntos_cierre = list(tramite.adjuntos.filter(activo=True).order_by("-created_at", "-id")[:cantidad_adjuntos])
                adjuntos_cierre.reverse()
                cierre_adjuntos_ids = {a.id for a in adjuntos_cierre if getattr(a, "id", None)}
            cierre_info = {
                "fecha": cierre_hist.fecha,
                "observacion": observacion,
                "adjuntos": adjuntos_cierre,
            }
        adjuntos_generales = [a for a in adjuntos_activos if a.id not in cierre_adjuntos_ids]

        context.update(
            {
                "ciudadano": ciudadano,
                "solicitud_tipo": "tramite",
                "solicitud_obj": tramite,
                "solicitud_label": "Trámite",
                "tipo_label": "Tipo",
                "tipo_nombre": tramite.tipo_tramite.nombre,
                "fecha_label": "Fecha de inicio",
                "fecha_valor": tramite.fecha_inicio,
                "datos_dinamicos": datos_dinamicos_list,
                "adjuntos": adjuntos_generales,
                "historial": historial,
                "solicitudes_datos_pendientes": solicitudes_datos_pendientes,
                "cierre_info": cierre_info,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        ciudadano = request.user.ciudadano_perfil
        tramite = get_object_or_404(
            Tramite.objects.select_related("tipo_tramite", "estado", "area_actual"),
            pk=kwargs["pk"],
            ciudadano=ciudadano,
            activo=True,
        )
        solicitudes_pendientes = self._get_solicitudes_datos_pendientes(tramite)
        if not solicitudes_pendientes:
            messages.error(request, "No hay solicitudes de datos pendientes para este trámite.")
            return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)

        solicitud_map = {s.id: s for s in solicitudes_pendientes}
        try:
            solicitud_id = int(request.POST.get("solicitud_id") or 0)
        except (TypeError, ValueError):
            solicitud_id = 0
        solicitud = solicitud_map.get(solicitud_id)
        if not solicitud:
            messages.error(request, "La solicitud seleccionada no es válida.")
            return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)

        campo_objetivo = self._extract_campo_objetivo(solicitud)
        if not campo_objetivo:
            messages.error(request, "No se indicó el campo a actualizar.")
            return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)

        campos_actualizados = []
        campos_valores = []
        detalle = []

        with transaction.atomic():
            if campo_objetivo.startswith("campo_dinamico:"):
                nombre_campo = campo_objetivo.split(":", 1)[1].strip()
                campo = CampoDinamicoTramite.objects.filter(
                    tipo_tramite=tramite.tipo_tramite, nombre__iexact=nombre_campo, activo=True
                ).first()
                if not campo:
                    messages.error(request, "No se encontró el campo dinámico solicitado.")
                    return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)

                input_name = f"valor_solicitud_{solicitud.id}"
                if campo.tipo_dato == CampoDinamicoTramite.TipoDato.ARCHIVO:
                    uploaded = request.FILES.get(input_name)
                    if not uploaded:
                        messages.error(request, "Debes adjuntar el archivo solicitado.")
                        return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)
                    adjunto = TramiteAdjunto(
                        tramite=tramite,
                        nombre_original=uploaded.name,
                        tipo_mime=getattr(uploaded, "content_type", "") or "",
                        subido_por=request.user if request.user.is_authenticated else None,
                        visible_ciudadano=True,
                    )
                    adjunto.archivo.save(uploaded.name, uploaded, save=False)
                    adjunto.save()
                    valor_nuevo = uploaded.name
                    campos_valores.append(
                        {
                            "campo": campo.nombre,
                            "tipo": "archivo",
                            "valor": uploaded.name,
                            "url": adjunto.archivo.url,
                        }
                    )
                else:
                    valor_nuevo = (request.POST.get(input_name) or "").strip()
                    if not valor_nuevo:
                        messages.error(request, "Debes completar el nuevo valor solicitado.")
                        return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)
                    campos_valores.append(
                        {
                            "campo": campo.nombre,
                            "tipo": "texto",
                            "valor": valor_nuevo,
                        }
                    )

                TramiteDatoDinamico.objects.update_or_create(
                    tramite=tramite,
                    campo=campo,
                    defaults={"valor": valor_nuevo, "activo": True},
                )
                campos_actualizados.append(campo.nombre)
            else:
                input_name = f"valor_solicitud_{solicitud.id}"
                valor_nuevo = (request.POST.get(input_name) or "").strip()
                if not valor_nuevo:
                    messages.error(request, "Debes completar el nuevo valor solicitado.")
                    return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)
                if hasattr(tramite, campo_objetivo):
                    setattr(tramite, campo_objetivo, valor_nuevo)
                    tramite.save(update_fields=[campo_objetivo, "updated_at"])
                    campos_actualizados.append(campo_objetivo)
                    campos_valores.append(
                        {
                            "campo": campo_objetivo,
                            "tipo": "texto",
                            "valor": valor_nuevo,
                        }
                    )
                else:
                    messages.error(request, "El campo solicitado no es válido.")
                    return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)

            if campos_actualizados:
                detalle.append(f"Campos actualizados: {', '.join(campos_actualizados)}")
            detalle_texto = "\n".join(detalle) if detalle else "El ciudadano respondió a la solicitud de datos."

            registrar_historial_tramite(
                tramite=tramite,
                accion="respuesta_solicitud_datos_ciudadano",
                usuario=request.user if request.user.is_authenticated else None,
                estado_nuevo=tramite.estado,
                area_nueva=tramite.area_actual,
                comentario=detalle_texto,
                visible_ciudadano=True,
                metadata={
                    "origen": "portal_ciudadano",
                    "solicitud_origen_id": solicitud.id,
                    "campos_actualizados": campos_actualizados,
                    "campos_valores": campos_valores,
                },
            )

        messages.success(request, "La información solicitada fue actualizada correctamente.")
        return redirect("portal_ciudadano:detalle_tramite", pk=tramite.pk)


class PortalCiudadanoReclamosView(TemplateView):
    template_name = "portal_ciudadano/reclamos.html"

    _AREAS_FALLBACK = [
        "Alumbrado público",
        "Limpieza urbana",
        "Espacio público",
        "Parques y plazas",
        "Habilitaciones e inspecciones",
        "Baches y veredas",
        "Tránsito y señalización",
        "Recolección de residuos",
        "Mantenimiento urbano",
        "Zoonosis",
        "Obras públicas",
        "Seguridad",
    ]

    @staticmethod
    def _icon_for_tipo(name):
        text = (name or "").lower()
        if "alumbr" in text or "luz" in text:
            return "fa-regular fa-lightbulb"
        if "limpieza" in text or "residu" in text or "basur" in text:
            return "fa-regular fa-trash-can"
        if "espacio" in text:
            return "fa-regular fa-building"
        if "parque" in text or "plaza" in text:
            return "fa-regular fa-image"
        if "habilit" in text or "inspecc" in text:
            return "fa-solid fa-building-columns"
        if "bache" in text or "vereda" in text:
            return "fa-solid fa-truck"
        if "tránsito" in text or "transito" in text or "señal" in text or "senal" in text:
            return "fa-solid fa-ban"
        if "manten" in text:
            return "fa-solid fa-gavel"
        if "zoon" in text:
            return "fa-solid fa-bug"
        if "obra" in text:
            return "fa-solid fa-screwdriver-wrench"
        if "segur" in text:
            return "fa-regular fa-eye"
        return "fa-regular fa-folder"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = _get_ciudadano_from_user(self.request.user)
        q = (self.request.GET.get("q") or "").strip()
        ranking_days = 90
        puede_ver_areas = True
        uso_filter = Q(reclamos__activo=True)
        if ranking_days > 0:
            desde = timezone.now() - timedelta(days=ranking_days)
            uso_filter &= Q(reclamos__created_at__gte=desde)
        tipos_qs = (
            TipoReclamo.objects.filter(activo=True)
            .select_related("area")
            .annotate(cantidad_uso=Count("reclamos", filter=uso_filter))
            .order_by("-cantidad_uso", "orden", "nombre")
        )
        if q:
            tipos_qs = tipos_qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))
        tipos_destacados = []
        tipos_otros = []
        tipos_items = [
            {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "area_id": tipo.area_id,
                "icon": self._icon_for_tipo(tipo.nombre),
                "cantidad_uso": int(getattr(tipo, "cantidad_uso", 0) or 0),
                "destacado_manual": bool(tipo.destacado),
            }
            for tipo in tipos_qs
        ]

        hay_ranking = any(item["cantidad_uso"] > 0 for item in tipos_items)
        if hay_ranking:
            tipos_destacados = tipos_items[:6]
            tipos_otros = tipos_items[6:]
        else:
            for item in tipos_items:
                if item["destacado_manual"] and len(tipos_destacados) < 6:
                    tipos_destacados.append(item)
                else:
                    tipos_otros.append(item)

        if not tipos_destacados and not tipos_otros:
            tipos_otros = [
                {
                    "id": idx + 1,
                    "nombre": name,
                    "area_id": None,
                    "icon": self._icon_for_tipo(name),
                }
                for idx, name in enumerate(self._AREAS_FALLBACK)
            ]

        context.update(
            {
                "ciudadano": ciudadano,
                "nombre_ciudadano": getattr(ciudadano, "nombre", "") if ciudadano else "",
                "tipos_destacados": tipos_destacados,
                "tipos_otros": tipos_otros,
                "puede_ver_areas": puede_ver_areas,
                "mostrar_selector_inicio": False,
                "q": q,
            }
        )
        return context


class PortalCiudadanoReclamoDetalleView(TemplateView):
    template_name = "portal_ciudadano/reclamos_detalle.html"

    @staticmethod
    def _is_image(uploaded_file):
        content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
        if content_type.startswith("image/"):
            return True
        extension = os.path.splitext((uploaded_file.name or "").lower())[1]
        return extension in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}

    @staticmethod
    def _cleanup_temp_files(draft):
        for file_meta in (draft or {}).get("adjuntos_meta", []):
            file_path = file_meta.get("path")
            if file_path and default_storage.exists(file_path):
                default_storage.delete(file_path)

    @staticmethod
    def _resolve_input_kind(tipo_dato):
        mapping = {
            "texto": "text",
            "numero": "number",
            "fecha": "date",
            "horario": "time",
            "booleano": "checkbox",
            "seleccion": "select",
            "email": "email",
            "telefono": "tel",
            "dni": "text",
            "archivo": "file",
        }
        return mapping.get(tipo_dato, "text")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = _get_ciudadano_from_user(self.request.user)

        area_param = self.request.GET.get("area") or self.request.POST.get("area_id")
        area_qs = Area.objects.filter(activo=True).order_by("orden", "nombre")
        if area_param:
            area = get_object_or_404(area_qs, id=area_param)
        else:
            area = area_qs.first()

        tipos_qs = (
            TipoReclamo.objects.filter(activo=True, area=area)
            .select_related("area", "area__parent")
            .order_by("orden", "nombre")
        )
        tipo_param = self.request.GET.get("tipo") or self.request.POST.get("tipo_id")
        tipo = tipos_qs.filter(id=tipo_param).first() if tipo_param else tipos_qs.first()
        area_principal_nombre = ""
        subarea_nombre = ""
        if tipo and tipo.area_id:
            if tipo.area.parent_id:
                area_principal_nombre = tipo.area.parent.nombre
                subarea_nombre = tipo.area.nombre
            else:
                area_principal_nombre = tipo.area.nombre

        campos_extra = []
        if tipo:
            campos = (
                CampoDinamicoReclamo.objects.filter(activo=True, tipo_reclamo=tipo)
                .prefetch_related("opciones")
                .order_by("orden", "id")
            )
            campos_extra = [
                {
                    "id": campo.id,
                    "nombre": campo.nombre,
                    "tipo_dato": campo.tipo_dato,
                    "input_kind": self._resolve_input_kind(campo.tipo_dato),
                    "obligatorio": campo.obligatorio,
                    "placeholder": campo.placeholder or "",
                    "ayuda": campo.ayuda or "",
                    "opciones": list(campo.opciones.filter(activo=True).order_by("orden", "id")),
                }
                for campo in campos
            ]

        form = kwargs.get("form") or ReclamoDetalleForm(
            initial={
                "area_id": area.id if area else None,
                "tipo_id": tipo.id if tipo else None,
            }
        )

        context.update(
            {
                "ciudadano": ciudadano,
                "area": area,
                "tipos_reclamo": tipos_qs,
                "tipo_seleccionado": tipo,
                "area_principal_nombre": area_principal_nombre,
                "subarea_nombre": subarea_nombre,
                "campos_extra": campos_extra,
                "form": form,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        form = ReclamoDetalleForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        existing_draft = request.session.get("portal_ciudadano_reclamo_draft", {})
        self._cleanup_temp_files(existing_draft)

        adjuntos_meta = []
        for uploaded in request.FILES.getlist("adjuntos"):
            if not uploaded:
                continue
            temp_name = f"portal_ciudadano/reclamos_draft/{uuid.uuid4().hex}_{uploaded.name}"
            stored_path = default_storage.save(temp_name, uploaded)
            adjuntos_meta.append(
                {
                    "name": uploaded.name,
                    "path": stored_path,
                    "url": default_storage.url(stored_path),
                    "is_image": self._is_image(uploaded),
                    "content_type": getattr(uploaded, "content_type", "") or "",
                }
            )

        payload = {
            "area_id": form.cleaned_data.get("area_id"),
            "tipo_id": form.cleaned_data.get("tipo_id"),
            "titulo_solicitud": form.cleaned_data.get("titulo_solicitud", ""),
            "descripcion": form.cleaned_data.get("descripcion", ""),
            "direccion_ubicacion": form.cleaned_data.get("direccion_ubicacion", ""),
            "fecha_aproximada": form.cleaned_data["fecha_aproximada"].isoformat(),
            "adjuntos": [file_meta["name"] for file_meta in adjuntos_meta],
            "adjuntos_meta": adjuntos_meta,
            "extras": {
                k: v
                for k, v in request.POST.items()
                if k.startswith("extra_") and str(v).strip()
            },
        }
        request.session["portal_ciudadano_reclamo_draft"] = payload
        request.session.modified = True
        return redirect("portal_ciudadano:reclamos_confirmar")


class PortalCiudadanoTramitesView(TemplateView):
    template_name = "portal_ciudadano/tramites.html"

    _TIPOS_FALLBACK = [
        "Licencia de conducir",
        "Habilitaci?n comercial",
        "Solicitud de poda",
        "Certificado de domicilio",
        "Permiso de obra",
        "Libre deuda municipal",
        "Subsidio social",
        "Solicitud de turno",
        "Exenci?n de tasas",
        "Inscripci?n a programas",
        "Renovaci?n de permiso",
        "Mesa de entradas",
    ]

    @staticmethod
    def _icon_for_tipo(name):
        text = (name or "").lower()
        if "licencia" in text or "permiso" in text:
            return "fa-regular fa-id-card"
        if "habilit" in text:
            return "fa-solid fa-building-columns"
        if "obra" in text or "poda" in text:
            return "fa-solid fa-screwdriver-wrench"
        if "certificado" in text:
            return "fa-regular fa-file-lines"
        if "deuda" in text or "tas" in text:
            return "fa-regular fa-money-bill-1"
        if "subsidio" in text or "programa" in text:
            return "fa-regular fa-handshake"
        if "turno" in text:
            return "fa-regular fa-calendar-check"
        if "mesa" in text or "entrada" in text:
            return "fa-regular fa-folder-open"
        return "fa-regular fa-file-lines"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = _get_ciudadano_from_user(self.request.user)
        q = (self.request.GET.get("q") or "").strip()
        ranking_days = 90
        uso_filter = Q(tramites__activo=True)
        if ranking_days > 0:
            desde = timezone.now() - timedelta(days=ranking_days)
            uso_filter &= Q(tramites__created_at__gte=desde)
        tipos_qs = (
            TipoTramite.objects.filter(activo=True)
            .annotate(cantidad_uso=Count("tramites", filter=uso_filter))
            .order_by("-cantidad_uso", "orden", "nombre")
        )
        if q:
            tipos_qs = tipos_qs.filter(Q(nombre__icontains=q) | Q(descripcion__icontains=q))

        tipos_items = [
            {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "icon": tipo.icono or self._icon_for_tipo(tipo.nombre),
                "imagen_portada": tipo.imagen_portada,
                "cantidad_uso": int(getattr(tipo, "cantidad_uso", 0) or 0),
                "destacado_manual": bool(tipo.destacado),
            }
            for tipo in tipos_qs
        ]
        tipos_destacados = []
        tipos_otros = []
        hay_ranking = any(item["cantidad_uso"] > 0 for item in tipos_items)
        if hay_ranking:
            tipos_destacados = tipos_items[:6]
            tipos_otros = tipos_items[6:]
        else:
            for item in tipos_items:
                if item["destacado_manual"] and len(tipos_destacados) < 6:
                    tipos_destacados.append(item)
                else:
                    tipos_otros.append(item)

        if not tipos_destacados and not tipos_otros:
            tipos_otros = [
                {
                    "id": idx + 1,
                    "nombre": name,
                    "icon": self._icon_for_tipo(name),
                    "imagen_portada": None,
                }
                for idx, name in enumerate(self._TIPOS_FALLBACK)
            ]

        context.update(
            {
                "ciudadano": ciudadano,
                "tipos_destacados": tipos_destacados,
                "tipos_otros": tipos_otros,
                "q": q,
            }
        )
        return context


class PortalCiudadanoTramiteDetalleView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/tramites_detalle.html"

    @staticmethod
    def _is_image(uploaded_file):
        content_type = (getattr(uploaded_file, "content_type", "") or "").lower()
        if content_type.startswith("image/"):
            return True
        extension = os.path.splitext((uploaded_file.name or "").lower())[1]
        return extension in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".svg"}

    @staticmethod
    def _cleanup_temp_files(draft):
        for file_meta in (draft or {}).get("adjuntos_meta", []):
            file_path = file_meta.get("path")
            if file_path and default_storage.exists(file_path):
                default_storage.delete(file_path)

    @staticmethod
    def _resolve_input_kind(tipo_dato):
        mapping = {
            "texto": "text",
            "numero": "number",
            "fecha": "date",
            "horario": "time",
            "booleano": "checkbox",
            "seleccion": "select",
            "email": "email",
            "telefono": "tel",
            "dni": "text",
            "archivo": "file",
        }
        return mapping.get(tipo_dato, "text")

    @staticmethod
    def _get_sedes_agenda(tipo):
        if not tipo:
            return []
        configuraciones = (
            ConfiguracionTurnos.objects.select_related("sede", "recursoturnos")
            .filter(
                activo=True,
                tipo_tramite=tipo,
                sede__isnull=False,
                sede__activo=True,
                recursoturnos__activo=True,
            )
            .order_by("sede__nombre", "id")
        )
        sedes_agenda = []
        for cfg in configuraciones:
            recurso = getattr(cfg, "recursoturnos", None)
            if not recurso:
                continue
            sedes_agenda.append(
                {
                    "sede_id": cfg.sede_id,
                    "sede_nombre": cfg.sede.nombre,
                    "recurso_id": recurso.id,
                    "recurso_nombre": recurso.nombre,
                }
            )
        return sedes_agenda

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = self.request.user.ciudadano_perfil

        tipo_param = self.request.GET.get("tipo")
        tipos_qs = TipoTramite.objects.filter(activo=True).select_related("area", "area__parent").order_by("orden", "nombre")
        if tipo_param:
            tipo = get_object_or_404(tipos_qs, id=tipo_param)
        else:
            tipo = tipos_qs.first()
        area_principal_nombre = ""
        subarea_nombre = ""
        if tipo and tipo.area_id:
            if tipo.area.parent_id:
                area_principal_nombre = tipo.area.parent.nombre
                subarea_nombre = tipo.area.nombre
            else:
                area_principal_nombre = tipo.area.nombre

        campos_extra = []
        requisitos = []
        if tipo:
            campos = (
                CampoDinamicoTramite.objects.filter(activo=True, tipo_tramite=tipo)
                .prefetch_related("opciones")
                .order_by("orden", "id")
            )
            requisitos = RequisitoTramite.objects.filter(activo=True, tipo_tramite=tipo).order_by("orden", "id")
            campos_extra = [
                {
                    "id": campo.id,
                    "nombre": campo.nombre,
                    "tipo_dato": campo.tipo_dato,
                    "input_kind": self._resolve_input_kind(campo.tipo_dato),
                    "obligatorio": campo.obligatorio,
                    "placeholder": campo.placeholder or "",
                    "ayuda": campo.ayuda or "",
                    "opciones": list(campo.opciones.filter(activo=True).order_by("orden", "id")),
                }
                for campo in campos
            ]

        form = kwargs.get("form") or TramiteDetalleForm(initial={"tipo_id": tipo.id if tipo else None})
        sedes_agenda = self._get_sedes_agenda(tipo) if tipo and getattr(tipo, "requiere_turno", False) else []
        tramite_max_anticipacion_dias = 10
        if tipo:
            max_cfg = (
                ConfiguracionTurnos.objects.filter(activo=True, tipo_tramite=tipo)
                .exclude(anticipacion_maxima_dias__isnull=True)
                .order_by("-anticipacion_maxima_dias")
                .values_list("anticipacion_maxima_dias", flat=True)
                .first()
            )
            if max_cfg:
                tramite_max_anticipacion_dias = int(max_cfg)
        sede_seleccionada_raw = self.request.POST.get("sede_id") or self.request.GET.get("sede_id") or ""
        try:
            sede_seleccionada_id = int(sede_seleccionada_raw) if sede_seleccionada_raw else None
        except (TypeError, ValueError):
            sede_seleccionada_id = None

        context.update(
            {
                "ciudadano": ciudadano,
                "tipo_seleccionado": tipo,
                "mostrar_selector_turno": False,
                "area_principal_nombre": area_principal_nombre,
                "subarea_nombre": subarea_nombre,
                "requisitos": requisitos,
                "campos_extra": campos_extra,
                "form": form,
                "tramite_requiere_turno": bool(getattr(tipo, "requiere_turno", False)) if tipo else False,
                "tramite_permite_online": bool(getattr(tipo, "permite_online", False)) if tipo else False,
                "tramite_permite_presencial": bool(getattr(tipo, "permite_presencial", False)) if tipo else False,
                "tramite_recurso_turnos": getattr(tipo, "recurso_turnos", None) if tipo else None,
                "tramite_sedes_agenda": sedes_agenda,
                "tramite_sede_seleccionada_id": sede_seleccionada_id,
                "tramite_max_anticipacion_dias": tramite_max_anticipacion_dias,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        form = TramiteDetalleForm(request.POST)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        tipo = TipoTramite.objects.filter(activo=True, id=form.cleaned_data.get("tipo_id")).first()
        if not tipo:
            messages.error(request, "El tipo de tramite seleccionado ya no esta disponible.")
            return redirect("portal_ciudadano:tramites_detalle")
        tramite_abierto = _get_tramite_abierto_mismo_tipo(request.user.ciudadano_perfil, tipo)
        if tramite_abierto:
            messages.error(request, f"Ya tenes un tramite iniciado de este tipo ({tramite_abierto.numero}).")
            return self.render_to_response(self.get_context_data(form=form))

        modalidad = (request.POST.get("modalidad_atencion") or "").strip().lower()
        modalidades_habilitadas = []
        if tipo.permite_online:
            modalidades_habilitadas.append("virtual")
        if tipo.permite_presencial:
            modalidades_habilitadas.append("presencial")
        if not modalidad and len(modalidades_habilitadas) == 1:
            modalidad = modalidades_habilitadas[0]
        if not modalidad or modalidad not in modalidades_habilitadas:
            messages.error(request, "Selecciona una modalidad valida para este tramite.")
            return self.render_to_response(self.get_context_data(form=form))

        turno_id_vinculado = None
        turno_codigo_vinculado = ""
        sede_id_vinculada = None
        sede_nombre_vinculada = ""
        recurso_turnos_id_vinculado = None
        if tipo.requiere_turno:
            sedes_agenda = self._get_sedes_agenda(tipo)
            if not sedes_agenda:
                messages.error(
                    request,
                    "Este tramite requiere turno pero no tiene agenda configurada. Contacta al municipio.",
                )
                return self.render_to_response(self.get_context_data(form=form))
            sedes_por_id = {item["sede_id"]: item for item in sedes_agenda}
            sede_id_raw = (request.POST.get("sede_id") or "").strip()
            if len(sedes_agenda) == 1 and not sede_id_raw:
                sede_id_vinculada = sedes_agenda[0]["sede_id"]
            else:
                try:
                    sede_id_vinculada = int(sede_id_raw)
                except (TypeError, ValueError):
                    sede_id_vinculada = None
            sede_agenda = sedes_por_id.get(sede_id_vinculada)
            if not sede_agenda:
                messages.error(request, "Selecciona una sede valida para continuar con el tramite.")
                return self.render_to_response(self.get_context_data(form=form))
            recurso_turnos_id_vinculado = sede_agenda["recurso_id"]
            sede_nombre_vinculada = sede_agenda["sede_nombre"]
            turno = (
                TurnoCiudadano.objects.filter(
                    ciudadano=request.user.ciudadano_perfil,
                    recurso_id=recurso_turnos_id_vinculado,
                    estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
                    fecha__gte=date.today(),
                )
                .order_by("fecha", "hora_inicio")
                .first()
            )
            if not turno:
                messages.error(
                    request,
                    "Este tramite requiere turno. Primero reserva un turno y luego continua con la solicitud.",
                )
                return self.render_to_response(self.get_context_data(form=form))
            turno_id_vinculado = turno.id
            turno_codigo_vinculado = turno.codigo_turno

        existing_draft = request.session.get("portal_ciudadano_tramite_draft", {})
        self._cleanup_temp_files(existing_draft)
        extras_payload = {
            k: v
            for k, v in request.POST.items()
            if k.startswith("extra_") and str(v).strip()
        }
        adjuntos_meta = []
        campos_archivo_ids = list(
            CampoDinamicoTramite.objects.filter(
                activo=True,
                tipo_tramite=tipo,
                tipo_dato=CampoDinamicoTramite.TipoDato.ARCHIVO,
            ).values_list("id", flat=True)
        )
        for campo_id in campos_archivo_ids:
            field_name = f"extra_{campo_id}"
            uploaded = request.FILES.get(field_name)
            if not uploaded:
                continue
            temp_name = f"portal_ciudadano/tramites_draft/{uuid.uuid4().hex}_{uploaded.name}"
            stored_path = default_storage.save(temp_name, uploaded)
            extras_payload[field_name] = uploaded.name
            adjuntos_meta.append(
                {
                    "campo_id": campo_id,
                    "name": uploaded.name,
                    "path": stored_path,
                    "url": default_storage.url(stored_path),
                    "is_image": self._is_image(uploaded),
                    "content_type": getattr(uploaded, "content_type", "") or "",
                }
            )

        payload = {
            "tipo_id": form.cleaned_data.get("tipo_id"),
            "extras": extras_payload,
            "adjuntos_meta": adjuntos_meta,
            "modalidad_atencion": modalidad,
            "turno_id_vinculado": turno_id_vinculado,
            "turno_codigo_vinculado": turno_codigo_vinculado,
            "sede_id": sede_id_vinculada,
            "sede_nombre": sede_nombre_vinculada,
            "recurso_turnos_id": recurso_turnos_id_vinculado,
        }
        request.session["portal_ciudadano_tramite_draft"] = payload
        request.session.modified = True
        return redirect("portal_ciudadano:tramites_confirmar")


class PortalCiudadanoTramiteInicioView(PortalCiudadanoTramiteDetalleView):
    template_name = "portal_ciudadano/tramites_detalle.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["mostrar_selector_turno"] = True
        return context


class PortalCiudadanoReclamoConfirmarView(TemplateView):
    template_name = "portal_ciudadano/reclamos_confirmar.html"

    @staticmethod
    def _build_dynamic_items(extras):
        items = []
        for key, value in (extras or {}).items():
            if not str(key).startswith("extra_"):
                continue
            try:
                campo_id = int(str(key).split("_", 1)[1])
            except (TypeError, ValueError, IndexError):
                continue
            items.append({"campo_id": campo_id, "valor": value})
        return items

    @staticmethod
    def _persist_adjuntos(*, reclamo, draft, user):
        for file_meta in (draft or {}).get("adjuntos_meta", []):
            file_path = file_meta.get("path")
            file_name = file_meta.get("name") or os.path.basename(file_path or "")
            if not file_path or not default_storage.exists(file_path):
                continue
            with default_storage.open(file_path, "rb") as fh:
                dj_file = File(fh, name=file_name)
                adjunto = ReclamoAdjunto(
                    reclamo=reclamo,
                    nombre_original=file_name,
                    tipo_mime=file_meta.get("content_type", "") or "",
                    subido_por=user if user and user.is_authenticated else None,
                    visible_ciudadano=True,
                )
                adjunto.archivo.save(file_name, dj_file, save=False)
                adjunto.save()

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("portal_ciudadano_reclamo_draft"):
            return redirect("portal_ciudadano:reclamos_detalle")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        draft = dict(self.request.session.get("portal_ciudadano_reclamo_draft", {}))
        fecha = draft.get("fecha_aproximada")
        if isinstance(fecha, str) and len(fecha) == 10 and "-" in fecha:
            y, m, d = fecha.split("-")
            draft["fecha_aproximada"] = f"{d}/{m}/{y}"
        draft.setdefault("adjuntos_meta", [])
        area = Area.objects.filter(id=draft.get("area_id")).first() if draft.get("area_id") else None
        tipo = TipoReclamo.objects.filter(id=draft.get("tipo_id")).first() if draft.get("tipo_id") else None
        context.update(
            {
                "ciudadano": _get_ciudadano_from_user(self.request.user),
                "draft": draft,
                "area": area,
                "tipo": tipo,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        draft = dict(request.session.get("portal_ciudadano_reclamo_draft", {}))
        tipo = (
            TipoReclamo.objects.select_related("area", "prioridad_default")
            .filter(id=draft.get("tipo_id"), activo=True)
            .first()
        )
        if not tipo:
            messages.error(request, "El tipo de reclamo seleccionado ya no está disponible.")
            return redirect("portal_ciudadano:reclamos_detalle")

        ciudadano = _get_ciudadano_from_user(request.user)
        request_user = request.user if request.user.is_authenticated else None
        municipio = getattr(ciudadano, "municipio", None) or tipo.municipio
        estado = obtener_estado_inicial_reclamo(municipio=municipio) or obtener_estado_inicial_reclamo()
        prioridad = (
            tipo.prioridad_default
            or obtener_prioridad_base_reclamo(municipio=municipio)
            or obtener_prioridad_base_reclamo()
        )

        if not estado or not prioridad:
            messages.error(request, "Falta configuración base de estado/prioridad para reclamos.")
            return redirect("portal_ciudadano:reclamos_detalle")

        with transaction.atomic():
            reclamo = Reclamo.objects.create(
                titulo=(draft.get("titulo_solicitud") or f"Reclamo {tipo.nombre}")[:200],
                descripcion="",
                detalle_interno="Creado desde portal ciudadano.",
                tipo_reclamo=tipo,
                estado=estado,
                prioridad=prioridad,
                area_actual=tipo.area,
                area_responsable=tipo.area,
                ciudadano=ciudadano,
                nombre_contacto=getattr(ciudadano, "nombre", "") or "",
                apellido_contacto=getattr(ciudadano, "apellido", "") or "",
                dni_contacto=getattr(ciudadano, "dni", "") or "",
                email_contacto=getattr(ciudadano, "email", "") or "",
                telefono_contacto=getattr(ciudadano, "telefono", "") or "",
                provincia=getattr(ciudadano, "provincia", None),
                municipio=municipio,
                localidad=getattr(ciudadano, "localidad", None),
                referencia=draft.get("direccion_ubicacion", ""),
                origen=Reclamo.Origen.WEB,
                creado_por=request_user,
                actualizado_por=request_user,
                sla_horas=tipo.sla_horas,
                es_anonimo=ciudadano is None,
                visible_ciudadano=True,
            )

            datos_preparados = validar_datos_dinamicos_reclamo(
                tipo_reclamo=tipo,
                datos=self._build_dynamic_items(draft.get("extras", {})),
            )
            guardar_datos_dinamicos_reclamo(reclamo=reclamo, datos_preparados=datos_preparados)

            self._persist_adjuntos(reclamo=reclamo, draft=draft, user=request.user)

            registrar_historial_reclamo(
                reclamo=reclamo,
                accion="creacion_portal_ciudadano",
                usuario=request_user,
                estado_nuevo=reclamo.estado,
                area_nueva=reclamo.area_actual,
                visible_ciudadano=True,
                metadata={"origen": "portal_ciudadano"},
            )

        PortalCiudadanoReclamoDetalleView._cleanup_temp_files(draft)
        request.session.pop("portal_ciudadano_reclamo_draft", None)
        request.session["portal_ciudadano_reclamo_enviado"] = {
            "numero": reclamo.numero,
            "tipo": "reclamo",
        }
        request.session.modified = True
        return redirect("portal_ciudadano:reclamos_enviado")


class PortalCiudadanoTramiteConfirmarView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/tramites_confirmar.html"

    @staticmethod
    def _build_dynamic_items(extras):
        items = []
        for key, value in (extras or {}).items():
            if not str(key).startswith("extra_"):
                continue
            try:
                campo_id = int(str(key).split("_", 1)[1])
            except (TypeError, ValueError, IndexError):
                continue
            items.append({"campo_id": campo_id, "valor": value})
        return items

    @staticmethod
    def _persist_adjuntos(*, tramite, draft, user):
        for file_meta in (draft or {}).get("adjuntos_meta", []):
            file_path = file_meta.get("path")
            file_name = file_meta.get("name") or os.path.basename(file_path or "")
            if not file_path or not default_storage.exists(file_path):
                continue
            with default_storage.open(file_path, "rb") as fh:
                dj_file = File(fh, name=file_name)
                adjunto = TramiteAdjunto(
                    tramite=tramite,
                    nombre_original=file_name,
                    tipo_mime=file_meta.get("content_type", "") or "",
                    subido_por=user if user and user.is_authenticated else None,
                    visible_ciudadano=True,
                )
                adjunto.archivo.save(file_name, dj_file, save=False)
                adjunto.save()

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("portal_ciudadano_tramite_draft"):
            return redirect("portal_ciudadano:tramites_detalle")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        draft = dict(self.request.session.get("portal_ciudadano_tramite_draft", {}))
        tipo = TipoTramite.objects.filter(id=draft.get("tipo_id")).first() if draft.get("tipo_id") else None
        extras_raw = draft.get("extras", {}) or {}
        campo_ids = []
        for key in extras_raw.keys():
            if not str(key).startswith("extra_"):
                continue
            try:
                campo_ids.append(int(str(key).split("_", 1)[1]))
            except (TypeError, ValueError, IndexError):
                continue
        campos_por_id = {
            campo.id: campo
            for campo in CampoDinamicoTramite.objects.filter(id__in=campo_ids).only("id", "nombre")
        }
        adjunto_por_campo = {
            int(meta.get("campo_id")): meta
            for meta in (draft.get("adjuntos_meta") or [])
            if str(meta.get("campo_id", "")).isdigit()
        }
        extras_resumen = []
        for key, value in extras_raw.items():
            if not str(key).startswith("extra_"):
                continue
            try:
                campo_id = int(str(key).split("_", 1)[1])
            except (TypeError, ValueError, IndexError):
                continue
            campo = campos_por_id.get(campo_id)
            meta_adjunto = adjunto_por_campo.get(campo_id, {})
            extras_resumen.append(
                {
                    "campo_id": campo_id,
                    "nombre": getattr(campo, "nombre", f"Dato {campo_id}"),
                    "valor": value,
                    "is_image": bool(meta_adjunto.get("is_image")),
                    "url": meta_adjunto.get("url", ""),
                }
            )
        context.update(
            {
                "ciudadano": self.request.user.ciudadano_perfil,
                "draft": draft,
                "tipo": tipo,
                "extras_resumen": extras_resumen,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        draft = dict(request.session.get("portal_ciudadano_tramite_draft", {}))
        tipo = (
            TipoTramite.objects.select_related("area", "prioridad_default")
            .filter(id=draft.get("tipo_id"), activo=True)
            .first()
        )
        if not tipo:
            messages.error(request, "El tipo de trámite seleccionado ya no está disponible.")
            return redirect("portal_ciudadano:tramites_detalle")

        ciudadano = request.user.ciudadano_perfil
        tramite_abierto = _get_tramite_abierto_mismo_tipo(ciudadano, tipo)
        if tramite_abierto:
            messages.error(request, f"Ya tenes un tramite iniciado de este tipo ({tramite_abierto.numero}).")
            return redirect("portal_ciudadano:tramites_detalle")
        municipio = getattr(ciudadano, "municipio", None) or tipo.municipio
        estado = obtener_estado_inicial_tramite(municipio=municipio) or obtener_estado_inicial_tramite()
        prioridad = (
            tipo.prioridad_default
            or obtener_prioridad_base_tramite(municipio=municipio)
            or obtener_prioridad_base_tramite()
        )

        if not estado or not prioridad:
            messages.error(request, "Falta configuración base de estado/prioridad para trámites.")
            return redirect("portal_ciudadano:tramites_detalle")

        modalidad = (draft.get("modalidad_atencion") or "").strip().lower()
        if modalidad not in {"virtual", "presencial"}:
            messages.error(request, "La modalidad de atencion no es valida.")
            return redirect("portal_ciudadano:tramites_detalle")
        if modalidad == "virtual" and not tipo.permite_online:
            messages.error(request, "Este tramite no permite modalidad virtual.")
            return redirect("portal_ciudadano:tramites_detalle")
        if modalidad == "presencial" and not tipo.permite_presencial:
            messages.error(request, "Este tramite no permite modalidad presencial.")
            return redirect("portal_ciudadano:tramites_detalle")

        turno_vinculado = None
        if tipo.requiere_turno:
            recurso_turnos_id = draft.get("recurso_turnos_id")
            if not recurso_turnos_id:
                messages.error(request, "Este tramite requiere turno pero no tiene agenda configurada para la sede.")
                return redirect("portal_ciudadano:tramites_detalle")
            turno_id_vinculado = draft.get("turno_id_vinculado")
            if turno_id_vinculado:
                turno_vinculado = (
                    TurnoCiudadano.objects.filter(
                        id=turno_id_vinculado,
                        ciudadano=ciudadano,
                        recurso_id=recurso_turnos_id,
                        estado__in=[TurnoCiudadano.Estado.PENDIENTE, TurnoCiudadano.Estado.CONFIRMADO],
                    )
                    .order_by("fecha", "hora_inicio")
                    .first()
                )
            if not turno_vinculado:
                messages.error(request, "No se encontro un turno vigente asociado para este tramite.")
                return redirect("portal_ciudadano:tramites_detalle")

        with transaction.atomic():
            tramite = Tramite.objects.create(
                titulo=(tipo.nombre or "Trámite")[:200],
                descripcion="",
                detalle_interno="Creado desde portal ciudadano.",
                tipo_tramite=tipo,
                estado=estado,
                prioridad=prioridad,
                area_actual=tipo.area,
                area_responsable=tipo.area,
                ciudadano=ciudadano,
                nombre_contacto=getattr(ciudadano, "nombre", "") or "",
                apellido_contacto=getattr(ciudadano, "apellido", "") or "",
                dni_contacto=getattr(ciudadano, "dni", "") or "",
                email_contacto=getattr(ciudadano, "email", "") or "",
                telefono_contacto=getattr(ciudadano, "telefono", "") or "",
                provincia=getattr(ciudadano, "provincia", None),
                municipio=municipio,
                localidad=getattr(ciudadano, "localidad", None),
                origen=Tramite.Origen.PRESENCIAL if modalidad == "presencial" else Tramite.Origen.WEB,
                canal_detalle=f"Modalidad: {'Presencial' if modalidad == 'presencial' else 'Virtual'}",
                externo_id=f"turno:{turno_vinculado.id}" if turno_vinculado else "",
                creado_por=request.user,
                actualizado_por=request.user,
                sla_horas=tipo.sla_horas,
                visible_ciudadano=True,
            )

            datos_preparados = validar_datos_dinamicos_tramite(
                tipo_tramite=tipo,
                datos=self._build_dynamic_items(draft.get("extras", {})),
            )
            guardar_datos_dinamicos_tramite(tramite=tramite, datos_preparados=datos_preparados)
            self._persist_adjuntos(tramite=tramite, draft=draft, user=request.user)

            registrar_historial_tramite(
                tramite=tramite,
                accion="creacion_portal_ciudadano",
                usuario=request.user,
                estado_nuevo=tramite.estado,
                area_nueva=tramite.area_actual,
                visible_ciudadano=True,
                metadata={
                    "origen": "portal_ciudadano",
                    "modalidad_atencion": modalidad,
                    "sede_id": draft.get("sede_id"),
                    "sede_nombre": draft.get("sede_nombre", ""),
                    "turno_id_vinculado": turno_vinculado.id if turno_vinculado else None,
                    "turno_codigo_vinculado": turno_vinculado.codigo_turno if turno_vinculado else "",
                },
            )

        PortalCiudadanoTramiteDetalleView._cleanup_temp_files(draft)
        request.session.pop("portal_ciudadano_tramite_draft", None)
        request.session["portal_ciudadano_tramite_enviado"] = {
            "numero": tramite.numero,
            "tipo": "tramite",
            "tramite_id": tramite.id,
        }
        request.session.modified = True
        return redirect("portal_ciudadano:tramites_enviado")


class PortalCiudadanoReclamoEnviadoView(TemplateView):
    template_name = "portal_ciudadano/solicitud_enviada.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("portal_ciudadano_reclamo_enviado"):
            return redirect("portal_ciudadano:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get("portal_ciudadano_reclamo_enviado", {})
        context.update(
            {
                "numero": data.get("numero", "-"),
                "titulo": "Solicitud enviada,",
                "subtitulo": "esta información va a quedar siempre disponible en tus solicitudes",
                "nueva_url": "portal_ciudadano:reclamos",
            }
        )
        return context


class PortalCiudadanoTramiteEnviadoView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/tramites_enviado.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("portal_ciudadano_tramite_enviado"):
            return redirect("portal_ciudadano:mi_perfil")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get("portal_ciudadano_tramite_enviado", {})
        tramite = (
            Tramite.objects.select_related("tipo_tramite")
            .filter(
                id=data.get("tramite_id"),
                ciudadano=getattr(self.request.user, "ciudadano_perfil", None),
            )
            .first()
        )
        modalidad = "-"
        canal = (getattr(tramite, "canal_detalle", "") or "").strip().lower()
        if "presencial" in canal:
            modalidad = "Presencial"
        elif "virtual" in canal or "online" in canal:
            modalidad = "Online"
        context.update(
            {
                "numero": data.get("numero", "-"),
                "tramite": tramite,
                "modalidad": modalidad,
            }
        )
        return context



# ── Registro ──────────────────────────────────────────────────────────────────

class PortalCiudadanoRegistroStep1View(View):
    template_name = 'portal_ciudadano/registro_step1.html'

    def get(self, request):
        if _is_ciudadano_user(request.user):
            return redirect('portal_ciudadano:mi_perfil')
        next_url = _get_safe_next(request)
        if next_url:
            request.session['portal_next'] = next_url
        return render(request, self.template_name, {'form': RegistroStep1Form(), 'next': next_url})

    def post(self, request):
        from portal.infrastructure.services.ciudadano_auth import (
            RegistroCiudadanoCuentaExistenteError,
            RegistroCiudadanoIdentidadNoVerificadaError,
            RegistroCiudadanoServicioNoDisponibleError,
            preparar_registro_ciudadano,
        )
        next_url = _get_safe_next(request)
        if next_url:
            request.session['portal_next'] = next_url
        form = RegistroStep1Form(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'next': next_url})
        try:
            request.session['registro_ciudadano'] = preparar_registro_ciudadano(
                dni=form.cleaned_data['dni'],
                genero=form.cleaned_data['genero'],
            )
        except RegistroCiudadanoCuentaExistenteError:
            messages.info(request, 'Ya tenés una cuenta. Ingresá con tu DNI y contraseña.')
            return redirect('portal_ciudadano:login')
        except RegistroCiudadanoIdentidadNoVerificadaError:
            form.add_error('dni', 'No pudimos verificar tu identidad. Verificá los datos ingresados.')
            return render(request, self.template_name, {'form': form, 'next': next_url})
        except RegistroCiudadanoServicioNoDisponibleError:
            form.add_error(None, 'El servicio de verificación no está disponible. Intentá más tarde.')
            return render(request, self.template_name, {'form': form, 'next': next_url})
        return redirect('portal_ciudadano:registro_step2')


class PortalCiudadanoRegistroStep2View(View):
    template_name = 'portal_ciudadano/registro_step2.html'

    def get(self, request):
        if not request.session.get('registro_ciudadano'):
            return redirect('portal_ciudadano:registro_step1')
        return render(request, self.template_name, {
            'form': RegistroStep2Form(),
            'datos': request.session['registro_ciudadano'],
        })

    def post(self, request):
        from portal.infrastructure.services.ciudadano_auth import (
            RegistroCiudadanoCuentaExistenteError,
            RegistroCiudadanoLegajoYaVinculadoError,
            RegistroCiudadanoSesionInvalidaError,
            completar_registro_ciudadano,
        )
        datos = request.session.get('registro_ciudadano')
        if not datos:
            return redirect('portal_ciudadano:registro_step1')
        form = RegistroStep2Form(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {'form': form, 'datos': datos})
        try:
            user, ciudadano = completar_registro_ciudadano(
                datos_registro=datos,
                email=form.cleaned_data['email'],
                telefono=form.cleaned_data['telefono'],
                password=form.cleaned_data['password1'],
            )
        except RegistroCiudadanoSesionInvalidaError:
            return redirect('portal_ciudadano:registro_step1')
        except (RegistroCiudadanoCuentaExistenteError, RegistroCiudadanoLegajoYaVinculadoError):
            messages.error(request, 'Ya existe una cuenta con ese DNI. Ingresá con tu contraseña.')
            request.session.pop('registro_ciudadano', None)
            return redirect('portal_ciudadano:login')
        request.session.pop('registro_ciudadano', None)
        login(request, user)
        messages.success(request, f'Bienvenido/a, {ciudadano.nombre}. Tu cuenta fue creada correctamente.')
        next_url = _get_safe_next(request)
        request.session.pop('portal_next', None)
        return redirect(next_url or 'portal_ciudadano:mi_perfil')


# ── Mis datos ─────────────────────────────────────────────────────────────────

def portal_ciudadano_mis_datos(request):
    auth = _require_ciudadano_or_login(request)
    if auth:
        return auth
    ciudadano = request.user.ciudadano_perfil
    form = CiudadanoEditarDatosForm(request.POST or None, instance=ciudadano)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tus datos fueron actualizados correctamente.')
        return redirect('portal_ciudadano:mis_datos')
    return render(request, 'portal_ciudadano/mis_datos.html', {'ciudadano': ciudadano, 'form': form})


def portal_ciudadano_cambio_password(request):
    auth = _require_ciudadano_or_login(request)
    if auth:
        return auth
    ciudadano = request.user.ciudadano_perfil
    form = CiudadanoCambioPasswordForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Tu contraseña fue cambiada correctamente.')
        return redirect('portal_ciudadano:mis_datos')
    return render(request, 'portal_ciudadano/cambio_password.html', {'ciudadano': ciudadano, 'form': form})


def portal_ciudadano_cambio_email(request):
    auth = _require_ciudadano_or_login(request)
    if auth:
        return auth
    from portal.infrastructure.services.ciudadano_perfil import crear_solicitud_cambio_email
    ciudadano = request.user.ciudadano_perfil
    form = CiudadanoCambioEmailForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        crear_solicitud_cambio_email(
            request=request,
            user=request.user,
            nuevo_email=form.cleaned_data['nuevo_email'],
        )
        messages.success(request, f'Te enviamos un email a {form.cleaned_data["nuevo_email"]} para confirmar el cambio.')
        return redirect('portal_ciudadano:mis_datos')
    return render(request, 'portal_ciudadano/cambio_email.html', {'ciudadano': ciudadano, 'form': form})


def portal_ciudadano_confirmar_email(request, token):
    from portal.infrastructure.services.ciudadano_perfil import (
        CambioEmailExpiradoError, CambioEmailInvalidoError, confirmar_cambio_email,
    )
    try:
        confirmar_cambio_email(token=token)
    except CambioEmailInvalidoError:
        messages.error(request, 'El enlace de confirmación no es válido.')
        return redirect('portal_ciudadano:login')
    except CambioEmailExpiradoError:
        messages.error(request, 'Este enlace expiró. Solicitá un nuevo cambio de email.')
        return redirect('portal_ciudadano:login')
    messages.success(request, 'Tu email fue actualizado correctamente.')
    return redirect('portal_ciudadano:mis_datos')


# ── Consultas ─────────────────────────────────────────────────────────────────

def portal_ciudadano_mis_consultas(request):
    auth = _require_ciudadano_or_login(request)
    if auth:
        return auth
    from portal.infrastructure.selectors.ciudadano import get_ciudadano_conversaciones, get_ciudadano_perfil
    ciudadano = get_ciudadano_perfil(request.user)
    return render(request, 'portal_ciudadano/mis_consultas.html', {
        'ciudadano': ciudadano,
        'conversaciones': get_ciudadano_conversaciones(request.user, ciudadano),
    })


def portal_ciudadano_nueva_consulta(request):
    auth = _require_ciudadano_or_login(request)
    if auth:
        return auth
    from portal.infrastructure.selectors.ciudadano import get_ciudadano_perfil
    from conversaciones.interfaces.module_api import crear_consulta_ciudadana
    ciudadano = get_ciudadano_perfil(request.user)
    form = CiudadanoNuevaConsultaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        conversacion = crear_consulta_ciudadana(
            ciudadano=ciudadano,
            user=request.user,
            motivo=form.cleaned_data['motivo'],
        )
        return redirect('portal_ciudadano:consulta_detalle', pk=conversacion.pk)
    return render(request, 'portal_ciudadano/nueva_consulta.html', {'ciudadano': ciudadano, 'form': form})


def portal_ciudadano_consulta_detalle(request, pk):
    auth = _require_ciudadano_or_login(request)
    if auth:
        return auth
    from portal.infrastructure.selectors.ciudadano import get_ciudadano_conversacion_or_404, get_ciudadano_perfil
    ciudadano = get_ciudadano_perfil(request.user)
    conversacion = get_ciudadano_conversacion_or_404(request.user, ciudadano, pk)
    return render(request, 'portal_ciudadano/consulta_detalle.html', {
        'ciudadano': ciudadano,
        'conversacion': conversacion,
        'mensajes': conversacion.mensajes.order_by('fecha_envio'),
        'puede_enviar': conversacion.estado != 'cerrada',
        'mensaje_form': CiudadanoEnviarMensajeForm(),
    })


def portal_ciudadano_enviar_mensaje(request, pk):
    auth = _require_ciudadano_or_login(request)
    if auth:
        return auth
    from portal.infrastructure.selectors.ciudadano import get_ciudadano_conversacion_or_404, get_ciudadano_perfil
    from conversaciones.interfaces.module_api import crear_mensaje_ciudadano_desde_portal
    ciudadano = get_ciudadano_perfil(request.user)
    conversacion = get_ciudadano_conversacion_or_404(request.user, ciudadano, pk)
    form = CiudadanoEnviarMensajeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        crear_mensaje_ciudadano_desde_portal(conversacion=conversacion, texto=form.cleaned_data['texto'])
    return redirect('portal_ciudadano:consulta_detalle', pk=pk)


# ── Password reset ────────────────────────────────────────────────────────────

class PortalCiudadanoPasswordResetView(PasswordResetView):
    form_class = CiudadanoPasswordResetForm
    template_name = 'portal_ciudadano/password_reset.html'
    email_template_name = 'portal_ciudadano/email/password_reset_body.html'
    subject_template_name = 'portal_ciudadano/email/password_reset_subject.txt'
    success_url = reverse_lazy('portal_ciudadano:password_reset_done')


class PortalCiudadanoPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'portal_ciudadano/password_reset_done.html'


class PortalCiudadanoPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'portal_ciudadano/password_reset_confirm.html'
    success_url = reverse_lazy('portal_ciudadano:password_reset_complete')


class PortalCiudadanoPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'portal_ciudadano/password_reset_complete.html'


