"""API publica del modulo legajos para consumidores externos."""


def consultar_datos_renaper(dni, sexo):
    from legajos.infrastructure.services.consulta_renaper import consultar_datos_renaper as consultar

    return consultar(dni, sexo)


def get_or_create_ciudadano_basico(*, dni, genero, datos_renaper):
    from legajos.models import Ciudadano

    return Ciudadano.objects.get_or_create(
        dni=dni,
        defaults={
            "nombre": datos_renaper.get("nombre", "Usuario"),
            "apellido": datos_renaper.get("apellido", "Chat"),
            "genero": genero,
            "domicilio": datos_renaper.get("domicilio", ""),
        },
    )


def crear_alerta_ciudadano(*, ciudadano, tipo, prioridad, mensaje):
    from legajos.models import AlertaCiudadano
    from legajos.infrastructure.services.alertas import AlertasService

    alerta = AlertaCiudadano.objects.create(
        ciudadano=ciudadano,
        tipo=tipo,
        prioridad=prioridad,
        mensaje=mensaje,
    )
    AlertasService._enviar_notificacion_alerta(alerta)
    return alerta
