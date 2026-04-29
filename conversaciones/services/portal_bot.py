from __future__ import annotations

from typing import Optional
from urllib.parse import quote

from django.db import transaction
from django.utils import timezone

from legajos.models import Ciudadano
from reclamos.models import Reclamo, TipoReclamo
from reclamos.services import (
    obtener_estado_inicial as obtener_estado_inicial_reclamo,
    obtener_prioridad_base as obtener_prioridad_base_reclamo,
    registrar_historial as registrar_historial_reclamo,
)
from tramites.models import TipoTramite, Tramite
from tramites.services import (
    obtener_estado_inicial as obtener_estado_inicial_tramite,
    obtener_prioridad_base as obtener_prioridad_base_tramite,
    registrar_historial as registrar_historial_tramite,
)

from ..models import Conversacion, FlujoPortalConversacion, Mensaje


MENU_TEXT = (
    "Contame que queres hacer y te guio paso a paso.\n"
    "Podes escribir por ejemplo: 'quiero hacer un reclamo' o 'quiero iniciar un tramite'.\n"
    "Si preferis operador humano, escribi 'operador'."
)


def iniciar_o_recuperar_flujo_portal(conversacion: Conversacion, canal: Optional[str] = None) -> FlujoPortalConversacion:
    defaults = {}
    if canal:
        defaults["canal"] = canal
    flujo, _ = FlujoPortalConversacion.objects.get_or_create(
        conversacion=conversacion,
        defaults=defaults or {"canal": FlujoPortalConversacion.Canal.RECLAMO_ANONIMO},
    )
    if canal and flujo.canal != canal and not flujo.finalizado:
        flujo.canal = canal
        flujo.save(update_fields=["canal", "updated_at"])
    return flujo


def enviar_mensaje_bot(conversacion: Conversacion, contenido: str) -> Mensaje:
    return Mensaje.objects.create(
        conversacion=conversacion,
        remitente="operador",
        contenido=contenido,
    )


def _choice(texto: str) -> str:
    t = (texto or "").strip().lower()
    if not t:
        return ""
    return t.split()[0]


def _auth_links(conversacion: Conversacion, canal: str) -> str:
    volver = f"/portal/mi-perfil/consultas/{conversacion.id}/"
    next_param = quote(volver, safe="")
    login_url = f"/portal/mi-perfil/login/?next={next_param}"
    registro_url = f"/portal/mi-perfil/registro/?next={next_param}"
    return (
        f"<br><a href='{login_url}' style='display:inline-block;margin-top:8px;padding:6px 10px;"
        f"border-radius:8px;background:#ffffff;color:#1f2937;font-weight:600;text-decoration:none;'>Iniciar sesion</a> "
        f"<a href='{registro_url}' style='display:inline-block;margin-top:8px;padding:6px 10px;"
        f"border-radius:8px;border:1px solid #ffffff;color:#ffffff;font-weight:600;text-decoration:none;'>Crear cuenta</a>"
    )


def _normalize(texto: str) -> str:
    return (texto or "").strip().lower()


def _is_yes(texto: str) -> bool:
    t = _normalize(texto)
    return t in {"si", "s", "ok", "dale", "confirmar", "confirmo", "1"}


def _is_no(texto: str) -> bool:
    t = _normalize(texto)
    return t in {"no", "n", "cancelar", "cancelo", "3"}


def _detectar_intencion(texto: str) -> Optional[str]:
    t = _normalize(texto)
    if not t:
        return None
    palabras_tramite = {"tramite", "tramites", "gestion", "solicitud"}
    palabras_reclamo = {"reclamo", "reclamos", "queja", "denuncia", "bache", "luz", "basura"}
    if any(p in t for p in palabras_tramite):
        return "tramite"
    if any(p in t for p in palabras_reclamo):
        return "reclamo"
    return None


def _detectar_canal_reclamo(texto: str) -> Optional[str]:
    t = _normalize(texto)
    if not t:
        return None
    if any(p in t for p in {"anon", "anonimo", "anoni", "sin cuenta"}) or t == "1":
        return FlujoPortalConversacion.Canal.RECLAMO_ANONIMO
    if any(p in t for p in {"cuenta", "logue", "login", "usuario", "dni"}) or t == "2":
        return FlujoPortalConversacion.Canal.RECLAMO_LOGIN
    return None


def _ciudadano_por_usuario(user) -> Optional[Ciudadano]:
    if not user or not user.is_authenticated:
        return None
    return Ciudadano.objects.filter(usuario=user).first()


def _tipos_reclamo_disponibles(anonimo: bool):
    qs = TipoReclamo.objects.filter(activo=True).select_related("area", "municipio").order_by("orden", "nombre")
    if anonimo:
        qs = qs.filter(permite_anonimo=True)
    return list(qs[:10])


def _tipos_tramite_disponibles():
    qs = (
        TipoTramite.objects.filter(activo=True, permite_online=True)
        .select_related("area", "municipio")
        .order_by("orden", "nombre")
    )
    return list(qs[:10])


def _render_tipos(items, modulo: str) -> str:
    etiqueta = "tipos de reclamo" if modulo == FlujoPortalConversacion.Modulo.RECLAMOS else "tipos de tramite"
    rows = [f"Elegi un {etiqueta}:"]
    for idx, item in enumerate(items, start=1):
        rows.append(f"{idx}. {item.nombre}")
    rows.append("Podes escribir el numero o el nombre.")
    return "\n".join(rows)


def _preparar_seleccion_tipo(flujo: FlujoPortalConversacion, user=None) -> str:
    if flujo.modulo == FlujoPortalConversacion.Modulo.RECLAMOS:
        tipos = _tipos_reclamo_disponibles(anonimo=flujo.canal == FlujoPortalConversacion.Canal.RECLAMO_ANONIMO)
    else:
        if not user or not user.is_authenticated:
            return (
                "Para iniciar un tramite tenes que iniciar sesion."
                f"{_auth_links(flujo.conversacion, FlujoPortalConversacion.Canal.TRAMITE_LOGIN)}"
            )
        tipos = _tipos_tramite_disponibles()

    if not tipos:
        return "No hay tipos disponibles para iniciar online. Escribi operador y te derivo con una persona."

    flujo.paso = FlujoPortalConversacion.Paso.SELECCION_TIPO
    flujo.datos = {**(flujo.datos or {}), "tipos": [{"id": t.id, "nombre": t.nombre} for t in tipos]}
    flujo.save(update_fields=["paso", "datos", "updated_at"])
    return _render_tipos(tipos, flujo.modulo)


def _resolver_tipo(texto: str, tipos: list[dict]) -> Optional[dict]:
    token = _choice(texto)
    if token.isdigit():
        idx = int(token) - 1
        if 0 <= idx < len(tipos):
            return tipos[idx]
        return None
    t = _normalize(texto)
    if not t:
        return None
    for item in tipos:
        if _normalize(item.get("nombre", "")) == t:
            return item
    for item in tipos:
        if t in _normalize(item.get("nombre", "")):
            return item
    return None


def _create_reclamo(conversacion: Conversacion, flujo: FlujoPortalConversacion, user):
    tipo_id = flujo.datos.get("tipo_id")
    titulo = (flujo.datos.get("titulo") or "").strip()
    descripcion = (flujo.datos.get("descripcion") or "").strip()
    tipo = TipoReclamo.objects.select_related("area", "prioridad_default").filter(id=tipo_id, activo=True).first()
    if not tipo:
        raise ValueError("El tipo de reclamo seleccionado ya no esta disponible.")

    ciudadano = _ciudadano_por_usuario(user)
    if flujo.canal == FlujoPortalConversacion.Canal.RECLAMO_ANONIMO and not tipo.permite_anonimo:
        raise ValueError("Este tipo no permite reclamo anonimo.")

    municipio = getattr(ciudadano, "municipio", None) or tipo.municipio
    estado = obtener_estado_inicial_reclamo(municipio=municipio) or obtener_estado_inicial_reclamo()
    prioridad = tipo.prioridad_default or obtener_prioridad_base_reclamo(municipio=municipio) or obtener_prioridad_base_reclamo()
    if not estado or not prioridad:
        raise ValueError("Falta configuracion base de estado/prioridad para reclamos.")

    reclamo = Reclamo.objects.create(
        titulo=titulo[:200],
        descripcion=descripcion,
        tipo_reclamo=tipo,
        estado=estado,
        prioridad=prioridad,
        area_actual=tipo.area,
        area_responsable=tipo.area,
        ciudadano=ciudadano,
        nombre_contacto=(ciudadano.nombre if ciudadano else ""),
        apellido_contacto=(ciudadano.apellido if ciudadano else ""),
        dni_contacto=(ciudadano.dni if ciudadano else ""),
        email_contacto=(ciudadano.email if ciudadano else ""),
        telefono_contacto=(ciudadano.telefono if ciudadano else ""),
        provincia=getattr(ciudadano, "provincia", None),
        municipio=municipio,
        localidad=getattr(ciudadano, "localidad", None),
        origen=Reclamo.Origen.CHAT,
        fecha_ingreso=timezone.now(),
        creado_por=user if user and user.is_authenticated else None,
        actualizado_por=user if user and user.is_authenticated else None,
        sla_horas=tipo.sla_horas,
        es_anonimo=flujo.canal == FlujoPortalConversacion.Canal.RECLAMO_ANONIMO,
        visible_ciudadano=True,
    )
    registrar_historial_reclamo(
        reclamo=reclamo,
        accion="creacion_chat_portal",
        usuario=user if user and user.is_authenticated else None,
        estado_nuevo=reclamo.estado,
        area_nueva=reclamo.area_actual,
        visible_ciudadano=True,
        metadata={"conversacion_id": conversacion.id},
    )
    return reclamo


def _create_tramite(conversacion: Conversacion, flujo: FlujoPortalConversacion, user):
    if not user or not user.is_authenticated:
        raise ValueError("Para iniciar un tramite tenes que iniciar sesion.")

    tipo_id = flujo.datos.get("tipo_id")
    titulo = (flujo.datos.get("titulo") or "").strip()
    descripcion = (flujo.datos.get("descripcion") or "").strip()
    tipo = TipoTramite.objects.select_related("area", "prioridad_default").filter(id=tipo_id, activo=True, permite_online=True).first()
    if not tipo:
        raise ValueError("El tipo de tramite seleccionado no esta disponible online.")

    ciudadano = _ciudadano_por_usuario(user)
    municipio = getattr(ciudadano, "municipio", None) or tipo.municipio
    estado = obtener_estado_inicial_tramite(municipio=municipio) or obtener_estado_inicial_tramite()
    prioridad = tipo.prioridad_default or obtener_prioridad_base_tramite(municipio=municipio) or obtener_prioridad_base_tramite()
    if not estado or not prioridad:
        raise ValueError("Falta configuracion base de estado/prioridad para tramites.")

    tramite = Tramite.objects.create(
        titulo=titulo[:200],
        descripcion=descripcion,
        tipo_tramite=tipo,
        estado=estado,
        prioridad=prioridad,
        area_actual=tipo.area,
        area_responsable=tipo.area,
        ciudadano=ciudadano,
        nombre_contacto=(ciudadano.nombre if ciudadano else ""),
        apellido_contacto=(ciudadano.apellido if ciudadano else ""),
        dni_contacto=(ciudadano.dni if ciudadano else ""),
        email_contacto=(ciudadano.email if ciudadano else ""),
        telefono_contacto=(ciudadano.telefono if ciudadano else ""),
        provincia=getattr(ciudadano, "provincia", None),
        municipio=municipio,
        localidad=getattr(ciudadano, "localidad", None),
        origen=Tramite.Origen.CHAT,
        fecha_inicio=timezone.now(),
        creado_por=user,
        actualizado_por=user,
        sla_horas=tipo.sla_horas,
        visible_ciudadano=True,
    )
    registrar_historial_tramite(
        tramite=tramite,
        accion="creacion_chat_portal",
        usuario=user,
        estado_nuevo=tramite.estado,
        area_nueva=tramite.area_actual,
        visible_ciudadano=True,
        metadata={"conversacion_id": conversacion.id},
    )
    return tramite


def procesar_flujo_portal(conversacion: Conversacion, mensaje: str, user=None) -> Optional[str]:
    flujo = getattr(conversacion, "flujo_portal", None)
    if not flujo or flujo.finalizado:
        return None

    texto = (mensaje or "").strip()
    token = _choice(texto)

    if token in {"9", "operador", "humano"}:
        flujo.derivado_operador = True
        flujo.finalizado = True
        flujo.paso = FlujoPortalConversacion.Paso.FINALIZADO
        flujo.save(update_fields=["derivado_operador", "finalizado", "paso", "updated_at"])
        conversacion.prioridad = "alta"
        conversacion.save(update_fields=["prioridad"])
        return "Te derivo con un operador en linea. Quedate en este chat."

    if flujo.paso == FlujoPortalConversacion.Paso.MENU:
        if not texto:
            canal_fijo = flujo.canal
            if canal_fijo == FlujoPortalConversacion.Canal.TRAMITE_LOGIN:
                flujo.modulo = FlujoPortalConversacion.Modulo.TRAMITES
                flujo.save(update_fields=["modulo", "updated_at"])
                return "Vamos a iniciar un tramite por chat."
            if canal_fijo == FlujoPortalConversacion.Canal.RECLAMO_LOGIN:
                flujo.modulo = FlujoPortalConversacion.Modulo.RECLAMOS
                flujo.save(update_fields=["modulo", "updated_at"])
                return "Vamos a iniciar un reclamo con tu cuenta."
            if canal_fijo == FlujoPortalConversacion.Canal.RECLAMO_ANONIMO:
                flujo.modulo = FlujoPortalConversacion.Modulo.RECLAMOS
                flujo.save(update_fields=["modulo", "updated_at"])
                return "Vamos a iniciar un reclamo anonimo por chat."
            return MENU_TEXT

        # Si viene canal fijo desde el link, avanza directo.
        if flujo.canal in {
            FlujoPortalConversacion.Canal.RECLAMO_ANONIMO,
            FlujoPortalConversacion.Canal.RECLAMO_LOGIN,
            FlujoPortalConversacion.Canal.TRAMITE_LOGIN,
        } and not flujo.modulo:
            if flujo.canal == FlujoPortalConversacion.Canal.TRAMITE_LOGIN:
                flujo.modulo = FlujoPortalConversacion.Modulo.TRAMITES
            else:
                flujo.modulo = FlujoPortalConversacion.Modulo.RECLAMOS
            flujo.save(update_fields=["modulo", "updated_at"])
            return _preparar_seleccion_tipo(flujo, user=user)

        if flujo.datos.get("esperando_canal_reclamo"):
            canal = _detectar_canal_reclamo(texto)
            if not canal:
                return "Para el reclamo, queres hacerlo anonimo o con cuenta?"
            if canal == FlujoPortalConversacion.Canal.RECLAMO_LOGIN and (not user or not user.is_authenticated):
                return (
                    "Para reclamo con cuenta primero inicia sesion."
                    f"{_auth_links(conversacion, FlujoPortalConversacion.Canal.RECLAMO_LOGIN)}"
                )
            flujo.canal = canal
            flujo.datos = {**(flujo.datos or {}), "esperando_canal_reclamo": False}
            flujo.save(update_fields=["canal", "datos", "updated_at"])
            return _preparar_seleccion_tipo(flujo, user=user)

        intencion = _detectar_intencion(texto)
        if not intencion and token in {"1", "2", "3"}:
            intencion = "reclamo" if token in {"1", "2"} else "tramite"

        if intencion == "tramite":
            flujo.modulo = FlujoPortalConversacion.Modulo.TRAMITES
            flujo.canal = FlujoPortalConversacion.Canal.TRAMITE_LOGIN
            flujo.save(update_fields=["modulo", "canal", "updated_at"])
            return _preparar_seleccion_tipo(flujo, user=user)

        if intencion == "reclamo":
            canal = _detectar_canal_reclamo(texto)
            if canal == FlujoPortalConversacion.Canal.RECLAMO_LOGIN and (not user or not user.is_authenticated):
                return (
                    "Para reclamo con cuenta primero inicia sesion."
                    f"{_auth_links(conversacion, FlujoPortalConversacion.Canal.RECLAMO_LOGIN)}"
                )
            flujo.modulo = FlujoPortalConversacion.Modulo.RECLAMOS
            if canal:
                flujo.canal = canal
                flujo.save(update_fields=["modulo", "canal", "updated_at"])
                return _preparar_seleccion_tipo(flujo, user=user)
            flujo.datos = {**(flujo.datos or {}), "esperando_canal_reclamo": True}
            flujo.save(update_fields=["modulo", "datos", "updated_at"])
            return "Perfecto. El reclamo lo queres hacer anonimo o con cuenta?"

        return "No te entendi del todo. Contame si queres iniciar un reclamo o un tramite. Si queres operador, escribi operador."

    if flujo.paso == FlujoPortalConversacion.Paso.SELECCION_TIPO:
        tipos = flujo.datos.get("tipos", [])
        seleccionado = _resolver_tipo(texto, tipos)
        if not seleccionado:
            return "No encontre ese tipo. Podes escribir numero o nombre."
        flujo.datos["tipo_id"] = seleccionado["id"]
        flujo.datos["tipo_nombre"] = seleccionado["nombre"]
        flujo.paso = FlujoPortalConversacion.Paso.TITULO
        flujo.save(update_fields=["datos", "paso", "updated_at"])
        return f"Perfecto. Escribi un titulo breve para el {flujo.modulo[:-1]}."

    if flujo.paso == FlujoPortalConversacion.Paso.TITULO:
        if len(texto) < 5:
            return "El titulo es muy corto. Escribi al menos 5 caracteres."
        flujo.datos["titulo"] = texto
        flujo.paso = FlujoPortalConversacion.Paso.DESCRIPCION
        flujo.save(update_fields=["datos", "paso", "updated_at"])
        return "Ahora describi el caso con mas detalle."

    if flujo.paso == FlujoPortalConversacion.Paso.DESCRIPCION:
        if len(texto) < 10:
            return "La descripcion es muy corta. Agrega mas detalle para poder registrarlo."
        flujo.datos["descripcion"] = texto
        flujo.paso = FlujoPortalConversacion.Paso.CONFIRMACION
        flujo.save(update_fields=["datos", "paso", "updated_at"])
        return (
            f"Resumen:\nTipo: {flujo.datos.get('tipo_nombre')}\nTitulo: {flujo.datos.get('titulo')}\n"
            "1. Confirmar y registrar\n2. Derivar a operador\n3. Cancelar"
        )

    if flujo.paso == FlujoPortalConversacion.Paso.CONFIRMACION:
        if _is_no(texto):
            flujo.finalizado = True
            flujo.paso = FlujoPortalConversacion.Paso.FINALIZADO
            flujo.save(update_fields=["finalizado", "paso", "updated_at"])
            return "Operacion cancelada. Si queres empezar de nuevo, escribi hola."

        if token == "2" or "operador" in _normalize(texto):
            flujo.derivado_operador = True
            flujo.finalizado = True
            flujo.paso = FlujoPortalConversacion.Paso.FINALIZADO
            flujo.save(update_fields=["derivado_operador", "finalizado", "paso", "updated_at"])
            conversacion.prioridad = "alta"
            conversacion.save(update_fields=["prioridad"])
            return "Te derivo con un operador para continuar."

        if not (_is_yes(texto) or token == "1"):
            return "Si queres registrar, responde 'si'. Si preferis operador, escribi 'operador'. Para cancelar, 'no'."

        try:
            if flujo.modulo == FlujoPortalConversacion.Modulo.RECLAMOS:
                obj = _create_reclamo(conversacion, flujo, user)
                msg = f"Reclamo generado correctamente. Numero: {obj.numero}."
            else:
                obj = _create_tramite(conversacion, flujo, user)
                msg = f"Tramite generado correctamente. Numero: {obj.numero}."
        except ValueError as exc:
            return f"No pude registrarlo: {exc} Escribi 2 para derivar a operador."

        flujo.finalizado = True
        flujo.paso = FlujoPortalConversacion.Paso.FINALIZADO
        flujo.save(update_fields=["finalizado", "paso", "updated_at"])
        return f"{msg} Si necesitas algo mas, podes escribir 9 para hablar con un operador."

    return None


def reactivar_flujo_post_login(conversacion: Conversacion, user) -> Optional[str]:
    """Retoma el flujo del bot después de que el ciudadano inicia sesión.

    Llama desde la vista de detalle de consulta cuando el ciudadano llega
    post-login y el flujo todavía está en paso MENU sin haber avanzado.
    Retorna el texto del mensaje del bot, o None si no hay nada que reactivar.
    """
    flujo = getattr(conversacion, "flujo_portal", None)
    if not flujo or flujo.finalizado:
        return None
    if flujo.paso != FlujoPortalConversacion.Paso.MENU:
        return None
    if flujo.datos.get("reactivado"):
        return None

    # Marcar como reactivado para evitar doble envío en recargas
    flujo.datos = {**(flujo.datos or {}), "reactivado": True}

    # Asegurar que el módulo esté seteado según el canal
    if not flujo.modulo:
        if flujo.canal == FlujoPortalConversacion.Canal.TRAMITE_LOGIN:
            flujo.modulo = FlujoPortalConversacion.Modulo.TRAMITES
        elif flujo.canal in {
            FlujoPortalConversacion.Canal.RECLAMO_LOGIN,
            FlujoPortalConversacion.Canal.RECLAMO_ANONIMO,
        }:
            flujo.modulo = FlujoPortalConversacion.Modulo.RECLAMOS
        flujo.save(update_fields=["modulo", "datos", "updated_at"])
    else:
        flujo.save(update_fields=["datos", "updated_at"])

    return _preparar_seleccion_tipo(flujo, user=user)


@transaction.atomic
def iniciar_flujo_guiado(user, canal: str) -> Conversacion:
    """Crea una nueva Conversacion con bot guiado desde el portal logueado.

    Muestra directamente la lista de tipos sin pasar por el menú general.
    """
    conversacion = Conversacion.objects.create(
        tipo="personal",
        ciudadano_usuario=user,
        estado="pendiente",
    )
    modulo = (
        FlujoPortalConversacion.Modulo.TRAMITES
        if canal == FlujoPortalConversacion.Canal.TRAMITE_LOGIN
        else FlujoPortalConversacion.Modulo.RECLAMOS
    )
    flujo = FlujoPortalConversacion.objects.create(
        conversacion=conversacion,
        canal=canal,
        modulo=modulo,
        paso=FlujoPortalConversacion.Paso.MENU,
        datos={"reactivado": True},
    )
    texto_bot = _preparar_seleccion_tipo(flujo, user=user)
    enviar_mensaje_bot(conversacion, texto_bot)
    return conversacion
