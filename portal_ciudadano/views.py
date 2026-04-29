import os
import uuid
from datetime import date

from django.contrib import messages
from django.contrib.auth import login, logout
from django.core.files import File
from django.core.files.storage import default_storage
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from portal.forms import CiudadanoConfirmarTurnoForm
from reclamos.models import Area, CampoDinamicoReclamo, Reclamo, ReclamoAdjunto, TipoReclamo
from reclamos.services import (
    guardar_datos_dinamicos as guardar_datos_dinamicos_reclamo,
    obtener_estado_inicial as obtener_estado_inicial_reclamo,
    obtener_prioridad_base as obtener_prioridad_base_reclamo,
    registrar_historial as registrar_historial_reclamo,
    validar_y_preparar_datos_dinamicos as validar_datos_dinamicos_reclamo,
)
from tramites.models import CampoDinamicoTramite, RequisitoTramite, TipoTramite, Tramite, TramiteAdjunto
from tramites.services import (
    guardar_datos_dinamicos as guardar_datos_dinamicos_tramite,
    obtener_estado_inicial as obtener_estado_inicial_tramite,
    obtener_prioridad_base as obtener_prioridad_base_tramite,
    registrar_historial as registrar_historial_tramite,
    validar_y_preparar_datos_dinamicos as validar_datos_dinamicos_tramite,
)

from .forms import ReclamoDetalleForm, TramiteDetalleForm

from portal.forms import CiudadanoLoginForm
from portal.selectors import get_ciudadano_perfil_context, get_portal_home_context
from portal.selectors import (
    get_ciudadano_programa_derivaciones,
    get_ciudadano_programa_detalle_or_404,
    get_ciudadano_programas_context,
    get_recurso_turnos_activo_or_404,
    get_recursos_turnos_activos,
    get_turno_ciudadano_or_404,
    get_turnos_ciudadano_contexto,
)
from portal.services.turnos_ciudadano import (
    TurnoNoDisponibleError,
    cancelar_turno_ciudadano,
    reservar_turno_ciudadano,
)
from portal.turnos_utils import get_calendario_mensual, get_slots_disponibles
from portal.views.ciudadano_auth import (
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
        return explicit_flag or str(next_url or "").startswith("/portal-ciudadano/reclamos/")

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
            }
        )


class PortalCiudadanoLogoutView(View):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect("portal_ciudadano:login")


class PortalCiudadanoAuthTemplateView(TemplateView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.groups.filter(name="Ciudadanos").exists():
            return redirect("portal_ciudadano:login")
        return super().dispatch(request, *args, **kwargs)


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
        tipo = (self.request.GET.get("tipo") or "todas").strip().lower()
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
            reclamos = reclamos.filter(estado__nombre__iexact=estado)
            tramites = tramites.filter(estado__nombre__iexact=estado)

        show_reclamos = tipo in {"todas", "reclamos"}
        show_tramites = tipo in {"todas", "tramites"}
        if not show_reclamos:
            reclamos = reclamos.none()
        if not show_tramites:
            tramites = tramites.none()

        estados_reclamo = (
            Reclamo.objects.filter(ciudadano=ciudadano, activo=True)
            .values_list("estado__nombre", flat=True)
            .distinct()
        )
        estados_tramite = (
            Tramite.objects.filter(ciudadano=ciudadano, activo=True)
            .values_list("estado__nombre", flat=True)
            .distinct()
        )
        estados_disponibles = sorted({e for e in list(estados_reclamo) + list(estados_tramite) if e})

        context.update(
            {
                "ciudadano": ciudadano,
                "reclamos": reclamos,
                "tramites": tramites,
                "filtro_q": query,
                "filtro_tipo": tipo,
                "filtro_estado": estado,
                "estados_disponibles": estados_disponibles,
                "show_reclamos": show_reclamos,
                "show_tramites": show_tramites,
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
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    return render(
        request,
        "portal_ciudadano/turnos_solicitar.html",
        {
            "ciudadano": request.user.ciudadano_perfil,
            "recursos": get_recursos_turnos_activos(),
        },
    )


def portal_ciudadano_turno_calendario(request, recurso_id):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
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
            "ciudadano": request.user.ciudadano_perfil,
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
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return JsonResponse({"error": "No autenticado"}, status=403)
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


def portal_ciudadano_confirmar_turno(request, recurso_id):
    auth_response = _require_ciudadano_or_login(request)
    if auth_response:
        return auth_response
    ciudadano = request.user.ciudadano_perfil
    recurso = get_recurso_turnos_activo_or_404(recurso_id)
    form = CiudadanoConfirmarTurnoForm(request.POST or None, initial=request.GET or None)

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
            return redirect("portal_ciudadano:turno_calendario", recurso_id=recurso_id)
        return redirect("portal_ciudadano:turno_confirmado", pk=turno.pk)

    if request.method == "POST" and not form.is_valid():
        messages.error(request, "Datos del turno inválidos. Intentá de nuevo.")
        return redirect("portal_ciudadano:turno_calendario", recurso_id=recurso_id)

    return render(
        request,
        "portal_ciudadano/turnos_confirmar.html",
        {
            "ciudadano": ciudadano,
            "recurso": recurso,
            "fecha": request.GET.get("fecha"),
            "hora_inicio": request.GET.get("hora_inicio"),
            "hora_fin": request.GET.get("hora_fin"),
            "form": form,
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ciudadano = self.request.user.ciudadano_perfil
        reclamo = get_object_or_404(
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
            pk=kwargs["pk"],
            ciudadano=ciudadano,
            activo=True,
        )
        context.update(
            {
                "ciudadano": ciudadano,
                "solicitud_tipo": "reclamo",
                "solicitud_obj": reclamo,
                "solicitud_label": "Reclamo",
                "tipo_label": "Subárea",
                "tipo_nombre": reclamo.tipo_reclamo.nombre,
                "fecha_label": "Fecha de ingreso",
                "fecha_valor": reclamo.fecha_ingreso,
                "datos_dinamicos": reclamo.datos_dinamicos.all(),
                "adjuntos": reclamo.adjuntos.filter(activo=True),
                "historial": reclamo.historial.all()[:30],
            }
        )
        return context


class PortalCiudadanoTramiteDetalleSolicitudView(PortalCiudadanoAuthTemplateView):
    template_name = "portal_ciudadano/solicitud_detalle.html"

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
                "datos_dinamicos": tramite.datos_dinamicos.all(),
                "adjuntos": tramite.adjuntos.filter(activo=True),
                "historial": tramite.historial.all()[:30],
            }
        )
        return context


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
    def _icon_for_area(name):
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
        mostrar_flujo_anonimo = str(self.request.GET.get("anonimo", "")).strip() in {"1", "true", "si", "yes"}
        puede_ver_areas = ciudadano is not None or mostrar_flujo_anonimo
        areas_qs = Area.objects.filter(activo=True).order_by("orden", "nombre")

        areas = [
            {
                "id": area.id,
                "nombre": area.nombre,
                "icon": self._icon_for_area(area.nombre),
            }
            for area in areas_qs
        ]

        if not areas:
            areas = [
                {
                    "id": idx + 1,
                    "nombre": name,
                    "icon": self._icon_for_area(name),
                }
                for idx, name in enumerate(self._AREAS_FALLBACK)
            ]

        context.update(
            {
                "ciudadano": ciudadano,
                "nombre_ciudadano": getattr(ciudadano, "nombre", "") if ciudadano else "",
                "areas_reclamo": areas,
                "puede_ver_areas": puede_ver_areas,
                "mostrar_selector_inicio": ciudadano is None and not mostrar_flujo_anonimo,
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

        tipos_qs = TipoReclamo.objects.filter(activo=True, area=area).order_by("orden", "nombre")
        tipo_param = self.request.GET.get("tipo") or self.request.POST.get("tipo_id")
        tipo = tipos_qs.filter(id=tipo_param).first() if tipo_param else tipos_qs.first()

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


class PortalCiudadanoTramitesView(PortalCiudadanoAuthTemplateView):
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
        ciudadano = self.request.user.ciudadano_perfil
        tipos_qs = TipoTramite.objects.filter(activo=True).order_by("orden", "nombre")

        tipos = [
            {
                "id": tipo.id,
                "nombre": tipo.nombre,
                "icon": self._icon_for_tipo(tipo.nombre),
            }
            for tipo in tipos_qs
        ]

        if not tipos:
            tipos = [
                {
                    "id": idx + 1,
                    "nombre": name,
                    "icon": self._icon_for_tipo(name),
                }
                for idx, name in enumerate(self._TIPOS_FALLBACK)
            ]

        context.update(
            {
                "ciudadano": ciudadano,
                "tipos_tramite": tipos,
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
        ciudadano = self.request.user.ciudadano_perfil

        tipo_param = self.request.GET.get("tipo")
        tipos_qs = TipoTramite.objects.filter(activo=True).order_by("orden", "nombre")
        if tipo_param:
            tipo = get_object_or_404(tipos_qs, id=tipo_param)
        else:
            tipo = tipos_qs.first()

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

        context.update(
            {
                "ciudadano": ciudadano,
                "tipo_seleccionado": tipo,
                "requisitos": requisitos,
                "campos_extra": campos_extra,
                "form": form,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        form = TramiteDetalleForm(request.POST, request.FILES)
        if not form.is_valid():
            return self.render_to_response(self.get_context_data(form=form))

        existing_draft = request.session.get("portal_ciudadano_tramite_draft", {})
        self._cleanup_temp_files(existing_draft)

        adjuntos_meta = []
        for uploaded in request.FILES.getlist("adjuntos"):
            if not uploaded:
                continue
            temp_name = f"portal_ciudadano/tramites_draft/{uuid.uuid4().hex}_{uploaded.name}"
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
            "tipo_id": form.cleaned_data.get("tipo_id"),
            "descripcion": form.cleaned_data.get("descripcion", ""),
            "fecha_aproximada": form.cleaned_data["fecha_aproximada"].isoformat(),
            "adjuntos": [file_meta["name"] for file_meta in adjuntos_meta],
            "adjuntos_meta": adjuntos_meta,
            "extras": {
                k: v
                for k, v in request.POST.items()
                if k.startswith("extra_") and str(v).strip()
            },
        }
        request.session["portal_ciudadano_tramite_draft"] = payload
        request.session.modified = True
        return redirect("portal_ciudadano:tramites_confirmar")


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
                descripcion=draft.get("descripcion", ""),
                detalle_interno=f"Fecha aproximada declarada: {draft.get('fecha_aproximada', '-')}",
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
        fecha = draft.get("fecha_aproximada")
        if isinstance(fecha, str) and len(fecha) == 10 and "-" in fecha:
            y, m, d = fecha.split("-")
            draft["fecha_aproximada"] = f"{d}/{m}/{y}"
        draft.setdefault("adjuntos_meta", [])
        tipo = TipoTramite.objects.filter(id=draft.get("tipo_id")).first() if draft.get("tipo_id") else None
        context.update(
            {
                "ciudadano": self.request.user.ciudadano_perfil,
                "draft": draft,
                "tipo": tipo,
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

        with transaction.atomic():
            tramite = Tramite.objects.create(
                titulo=(tipo.nombre or "Trámite")[:200],
                descripcion=draft.get("descripcion", ""),
                detalle_interno=f"Fecha aproximada declarada: {draft.get('fecha_aproximada', '-')}",
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
                origen=Tramite.Origen.WEB,
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
                metadata={"origen": "portal_ciudadano"},
            )

        PortalCiudadanoTramiteDetalleView._cleanup_temp_files(draft)
        request.session.pop("portal_ciudadano_tramite_draft", None)
        request.session["portal_ciudadano_tramite_enviado"] = {
            "numero": tramite.numero,
            "tipo": "tramite",
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
    template_name = "portal_ciudadano/solicitud_enviada.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get("portal_ciudadano_tramite_enviado"):
            return redirect("portal_ciudadano:mi_perfil")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.session.get("portal_ciudadano_tramite_enviado", {})
        context.update(
            {
                "numero": data.get("numero", "-"),
                "titulo": "Solicitud enviada,",
                "subtitulo": "esta información va a quedar siempre disponible en tus solicitudes",
                "nueva_url": "portal_ciudadano:tramites",
            }
        )
        return context
