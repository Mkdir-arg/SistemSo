# Checklist de validacion final

## Modularidad

- [x] Cada modulo declarado tiene `module.py`.
- [x] Cada modulo declarado tiene `domain/`, `application/`, `infrastructure/` e `interfaces/`.
- [x] Cada modulo declarado tiene URLConfs canonicas en `interfaces/web/urls.py` y `interfaces/api/urls.py`.
- [x] `config.modules.INSTALLED_PROJECT_MODULES` es la unica fuente de verdad de modulos instalados.
- [x] Ningun modulo importa `views/forms/templates/services/selectors/models` internos de otro modulo como contrato publico.
- [x] `domain/` y `application/` no importan Django.
- [x] `application/` no importa adapters internos del modulo.
- [x] No quedan entrypoints publicos top-level para views, forms, services, selectors, signals, api views, serializers, templates, static ni realtime.

## Activacion

- [x] `python manage.py modules sync` crea o sincroniza estados correctamente.
- [x] Un modulo instalado pero inactivo responde `module_inactive`.
- [x] Un modulo no instalado deja de publicar sus rutas opcionales.

## No rotura del sistema

- [x] Los tests existentes relevantes siguen pasando.
- [x] Las pantallas shell siguen cargando con modulos apagados.
- [x] Los grupos de modulos inactivos o no instalados no aparecen para alta/edicion de usuarios.

## Seguridad y permisos

- [x] Las vistas protegidas siguen usando login/grupo ademas del guard modular.
- [x] No se filtran links ni widgets a modulos inactivos.
- [x] Las APIs no devuelven `500` por modulo inactivo o removido.

## Frontend

- [x] El sidebar no muestra accesos a modulos opcionales desactivados.
- [x] El portal ciudadano no rompe si faltan `turnos` o `conversaciones`.
- [x] El bubble del chatbot no se renderiza si el modulo esta inactivo.
- [x] Existe smoke funcional automatizado para shells con modulos opcionales ausentes e inactivos.
- [x] Existe E2E UI automatizado para el flujo Turnos ciudadano -> operador -> ciudadano.

## Mantenibilidad

- [x] Existe README general y README de los modulos activables.
- [x] Existe guia para crear modulos nuevos.
- [x] Existe plan de migracion y preguntas de control para el equipo.
