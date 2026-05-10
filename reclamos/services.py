from datetime import datetime

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime

from .models import (
    CampoDinamicoOpcion,
    CampoDinamicoReclamo,
    EstadoReclamoTransicion,
    EstadoReclamo,
    PrioridadReclamo,
    ReclamoDatoDinamico,
    ReclamoHistorial,
)


def obtener_estado_inicial(municipio=None):
    return EstadoReclamo.objects.filter(activo=True, es_inicial=True).order_by("orden", "id").first()


def obtener_prioridad_base(municipio=None):
    return PrioridadReclamo.objects.filter(activo=True).order_by("nivel", "id").first()


def registrar_historial(
    *,
    reclamo,
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
    return ReclamoHistorial.objects.create(
        reclamo=reclamo,
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
    if tipo in {CampoDinamicoReclamo.TipoDato.TEXTO, CampoDinamicoReclamo.TipoDato.EMAIL, CampoDinamicoReclamo.TipoDato.TELEFONO, CampoDinamicoReclamo.TipoDato.DNI, CampoDinamicoReclamo.TipoDato.ARCHIVO}:
        valor_str = str(valor).strip()
        if campo.longitud_maxima and len(valor_str) > campo.longitud_maxima:
            raise ValueError(f"El campo '{campo.nombre}' supera la longitud maxima.")
        return valor_str
    if tipo == CampoDinamicoReclamo.TipoDato.NUMERO:
        try:
            return float(valor)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"El campo '{campo.nombre}' requiere un numero.") from exc
    if tipo == CampoDinamicoReclamo.TipoDato.BOOLEANO:
        if isinstance(valor, bool):
            return valor
        if isinstance(valor, str) and valor.lower() in {"true", "false"}:
            return valor.lower() == "true"
        raise ValueError(f"El campo '{campo.nombre}' requiere un booleano.")
    if tipo == CampoDinamicoReclamo.TipoDato.FECHA:
        if isinstance(valor, str):
            dt = parse_datetime(valor)
            if dt:
                return dt.isoformat()
            d = parse_date(valor)
            if d:
                return d.isoformat()
        raise ValueError(f"El campo '{campo.nombre}' requiere una fecha valida (ISO).")
    if tipo == CampoDinamicoReclamo.TipoDato.HORARIO:
        valor_str = str(valor).strip()
        try:
            datetime.strptime(valor_str, "%H:%M")
        except ValueError as exc:
            raise ValueError(f"El campo '{campo.nombre}' requiere un horario valido (HH:MM).") from exc
        return valor_str
    if tipo == CampoDinamicoReclamo.TipoDato.SELECCION:
        valor_str = str(valor).strip()
        existe = CampoDinamicoOpcion.objects.filter(campo=campo, activo=True, valor=valor_str).exists()
        if not existe:
            raise ValueError(f"El valor '{valor_str}' no es valido para el campo '{campo.nombre}'.")
        return valor_str
    return valor


def validar_y_preparar_datos_dinamicos(*, tipo_reclamo, datos):
    campos = list(
        CampoDinamicoReclamo.objects.filter(tipo_reclamo=tipo_reclamo, activo=True).order_by("orden", "id")
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


def guardar_datos_dinamicos(*, reclamo, datos_preparados):
    if not datos_preparados:
        return
    for campo_id, valor in datos_preparados.items():
        ReclamoDatoDinamico.objects.update_or_create(
            reclamo=reclamo,
            campo_id=campo_id,
            defaults={"valor": valor, "activo": True},
        )


def validar_transicion_estado_reclamo(
    *,
    reclamo,
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

    base_qs = EstadoReclamoTransicion.objects.filter(
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
    area_referencia = area_actual or reclamo.area_actual
    if areas_permitidas.exists():
        if not area_referencia or not areas_permitidas.filter(id=area_referencia.id).exists():
            raise ValueError("La transicion no esta habilitada para el area actual.")

    if transicion.requiere_comentario and not str(comentario or "").strip():
        raise ValueError("La transicion requiere comentario.")
    if transicion.requiere_asignado and not asignado_a:
        raise ValueError("La transicion requiere un usuario asignado.")
    if transicion.requiere_area_responsable and not (area_responsable or reclamo.area_responsable):
        raise ValueError("La transicion requiere area responsable.")


def validar_requisitos_runtime_reclamo(*, reclamo, tipo_reclamo, estado_objetivo=None):
    if not tipo_reclamo:
        return

    if tipo_reclamo.requiere_ubicacion:
        tiene_geo = bool(reclamo.latitud and reclamo.longitud)
        tiene_direccion = bool(reclamo.calle or reclamo.barrio or reclamo.referencia)
        if not (tiene_geo or tiene_direccion):
            raise ValueError("El tipo de reclamo requiere ubicacion (direccion o coordenadas).")

    estado_ref = estado_objetivo or reclamo.estado
    exige_adjunto = bool(tipo_reclamo.requiere_adjunto and estado_ref and not estado_ref.es_inicial)
    if exige_adjunto:
        if not reclamo.pk or not reclamo.adjuntos.filter(activo=True).exists():
            raise ValueError("El tipo de reclamo requiere al menos un adjunto para avanzar de estado.")
