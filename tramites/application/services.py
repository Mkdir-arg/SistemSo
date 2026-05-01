from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from tramites.models import (
    CampoDinamicoOpcion,
    CampoDinamicoTramite,
    EstadoTramiteTransicion,
    EstadoTramite,
    PrioridadTramite,
    RequisitoTramite,
    TramiteDatoDinamico,
    TramiteHistorial,
)


def obtener_estado_inicial(municipio=None):
    estado = EstadoTramite.objects.filter(activo=True, es_inicial=True, municipio=municipio).order_by("orden", "id").first()
    if estado:
        return estado
    return EstadoTramite.objects.filter(activo=True, es_inicial=True, municipio__isnull=True).order_by("orden", "id").first()


def obtener_prioridad_base(municipio=None):
    prioridad = PrioridadTramite.objects.filter(activo=True, municipio=municipio).order_by("nivel", "id").first()
    if prioridad:
        return prioridad
    return PrioridadTramite.objects.filter(activo=True, municipio__isnull=True).order_by("nivel", "id").first()


def registrar_historial(
    *,
    tramite,
    accion,
    usuario=None,
    estado_anterior=None,
    estado_nuevo=None,
    area_anterior=None,
    area_nueva=None,
    asignado_anterior=None,
    asignado_nuevo=None,
    comentario="",
    visible_ciudadano=False,
    metadata=None,
):
    return TramiteHistorial.objects.create(
        tramite=tramite,
        fecha=timezone.now(),
        usuario=usuario,
        accion=accion,
        estado_anterior=estado_anterior,
        estado_nuevo=estado_nuevo,
        area_anterior=area_anterior,
        area_nueva=area_nueva,
        asignado_anterior=asignado_anterior,
        asignado_nuevo=asignado_nuevo,
        comentario=comentario or "",
        visible_ciudadano=visible_ciudadano,
        metadata=metadata,
    )


def _normalizar_valor_campo(campo, valor):
    if valor is None:
        return None

    tipo = campo.tipo_dato
    if tipo in {CampoDinamicoTramite.TipoDato.TEXTO, CampoDinamicoTramite.TipoDato.EMAIL, CampoDinamicoTramite.TipoDato.TELEFONO, CampoDinamicoTramite.TipoDato.DNI, CampoDinamicoTramite.TipoDato.ARCHIVO}:
        valor_str = str(valor).strip()
        if campo.longitud_maxima and len(valor_str) > campo.longitud_maxima:
            raise ValueError(f"El campo '{campo.nombre}' supera la longitud maxima.")
        return valor_str
    if tipo == CampoDinamicoTramite.TipoDato.NUMERO:
        try:
            return float(valor)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"El campo '{campo.nombre}' requiere un numero.") from exc
    if tipo == CampoDinamicoTramite.TipoDato.BOOLEANO:
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, str) and valor.lower() in {"true", "false"}:
            return valor.lower() == "true"
        raise ValueError(f"El campo '{campo.nombre}' requiere un booleano.")
    if tipo == CampoDinamicoTramite.TipoDato.FECHA:
        if isinstance(valor, str):
            dt = parse_datetime(valor)
            if dt:
                return dt.isoformat()
            d = parse_date(valor)
            if d:
                return d.isoformat()
        raise ValueError(f"El campo '{campo.nombre}' requiere una fecha valida (ISO).")
    if tipo == CampoDinamicoTramite.TipoDato.SELECCION:
        valor_str = str(valor).strip()
        existe = CampoDinamicoOpcion.objects.filter(campo=campo, activo=True, valor=valor_str).exists()
        if not existe:
            raise ValueError(f"El valor '{valor_str}' no es valido para el campo '{campo.nombre}'.")
        return valor_str
    return valor


def validar_y_preparar_datos_dinamicos(*, tipo_tramite, datos):
    campos = list(
        CampoDinamicoTramite.objects.filter(tipo_tramite=tipo_tramite, activo=True).order_by("orden", "id")
    )
    if not campos:
        return {}

    datos = datos or []
    index_por_campo_id = {}
    index_por_codigo = {}
    for item in datos:
        if not isinstance(item, dict):
            raise ValueError("Cada dato dinamico debe ser un objeto con campo y valor.")
        campo_id = item.get("campo_id")
        codigo = item.get("codigo")
        valor = item.get("valor")
        if campo_id is not None:
            index_por_campo_id[int(campo_id)] = valor
        if codigo:
            index_por_codigo[str(codigo)] = valor

    preparado = {}
    for campo in campos:
        valor = index_por_campo_id.get(campo.id, index_por_codigo.get(campo.codigo))
        if valor in (None, ""):
            if campo.obligatorio:
                raise ValueError(f"El campo dinamico '{campo.nombre}' es obligatorio.")
            continue
        preparado[campo.id] = _normalizar_valor_campo(campo, valor)
    return preparado


def guardar_datos_dinamicos(*, tramite, datos_preparados):
    if not datos_preparados:
        return
    for campo_id, valor in datos_preparados.items():
        TramiteDatoDinamico.objects.update_or_create(
            tramite=tramite,
            campo_id=campo_id,
            defaults={"valor": valor, "activo": True},
        )


def validar_transicion_estado_tramite(
    *,
    tramite,
    estado_anterior,
    estado_nuevo,
    usuario=None,
    comentario="",
    area_actual=None,
    asignado_a=None,
    area_responsable=None,
):
    if not estado_anterior or not estado_nuevo or estado_anterior == estado_nuevo:
        return

    base_qs = EstadoTramiteTransicion.objects.filter(
        activo=True,
        estado_origen=estado_anterior,
    ).prefetch_related("grupos_permitidos", "areas_permitidas")

    if not base_qs.exists():
        return

    transicion = base_qs.filter(estado_destino=estado_nuevo).first()
    if not transicion:
        raise ValueError(f"No esta permitida la transicion de '{estado_anterior}' a '{estado_nuevo}'.")

    grupos_permitidos = transicion.grupos_permitidos.all()
    if grupos_permitidos.exists():
        if not usuario or not usuario.is_authenticated:
            raise ValueError("La transicion requiere usuario autenticado.")
        if not usuario.is_superuser and not usuario.groups.filter(id__in=grupos_permitidos.values_list("id", flat=True)).exists():
            raise ValueError("El usuario no tiene rol habilitado para esta transicion.")

    areas_permitidas = transicion.areas_permitidas.all()
    area_referencia = area_actual or tramite.area_actual
    if areas_permitidas.exists():
        if not area_referencia or not areas_permitidas.filter(id=area_referencia.id).exists():
            raise ValueError("La transicion no esta habilitada para el area actual.")

    if transicion.requiere_comentario and not str(comentario or "").strip():
        raise ValueError("La transicion requiere comentario.")
    if transicion.requiere_asignado and not asignado_a:
        raise ValueError("La transicion requiere un usuario asignado.")
    if transicion.requiere_area_responsable and not area_responsable:
        raise ValueError("La transicion requiere area responsable.")


def validar_requisitos_runtime_tramite(*, tramite, tipo_tramite, estado_objetivo=None, datos_preparados=None):
    if not tipo_tramite:
        return

    estado_ref = estado_objetivo or tramite.estado
    exige_adjunto = bool(estado_ref and not estado_ref.es_inicial)
    tiene_adjuntos = bool(tramite.pk and tramite.adjuntos.filter(activo=True).exists())

    if tipo_tramite.requiere_adjunto and exige_adjunto and not tiene_adjuntos:
        raise ValueError("El tipo de tramite requiere al menos un adjunto para avanzar de estado.")

    requisitos = (
        RequisitoTramite.objects.filter(
            activo=True,
            tipo_tramite=tipo_tramite,
            obligatorio=True,
        )
        .select_related("campo_dinamico")
        .order_by("orden", "id")
    )

    for requisito in requisitos:
        if requisito.requiere_adjunto and exige_adjunto and not tiene_adjuntos:
            raise ValueError(f"El requisito '{requisito.nombre}' requiere adjunto.")

        if not requisito.campo_dinamico_id:
            continue

        valor = None
        if datos_preparados and requisito.campo_dinamico_id in datos_preparados:
            valor = datos_preparados.get(requisito.campo_dinamico_id)
        elif tramite.pk:
            valor = (
                TramiteDatoDinamico.objects.filter(
                    tramite=tramite,
                    campo_id=requisito.campo_dinamico_id,
                    activo=True,
                )
                .values_list("valor", flat=True)
                .first()
            )

        if valor in (None, "", []):
            raise ValueError(f"Falta completar el requisito obligatorio '{requisito.nombre}'.")
