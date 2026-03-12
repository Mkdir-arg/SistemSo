from .views_backoffice import (
    api_conversacion_detalle,
    api_estadisticas_tiempo_real,
    api_metricas_tiempo_real,
    asignacion_automatica,
    asignar_conversacion,
    cerrar_conversacion,
    configurar_cola,
    detalle_conversacion,
    enviar_mensaje_operador,
    evaluar_conversacion,
    lista_conversaciones,
    metricas_conversaciones,
    reasignar_conversacion,
    tiene_permiso_conversaciones,
)
from .views_public import (
    chat_ciudadano,
    consultar_renaper,
    enviar_mensaje_ciudadano,
    iniciar_conversacion,
    obtener_mensajes_ciudadano,
)
