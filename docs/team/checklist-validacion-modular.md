# Checklist de validacion final

## Modularidad

- [ ] Cada modulo declarado tiene `module.py`.
- [ ] Cada modulo declarado tiene `domain/`, `application/`, `infrastructure/` e `interfaces/`.
- [ ] Cada modulo declarado tiene URLConfs canonicas en `interfaces/web/urls.py` y `interfaces/api/urls.py`.
- [ ] `config.modules.INSTALLED_PROJECT_MODULES` es la unica fuente de verdad de modulos instalados.
- [ ] Ningun modulo importa `views/forms/templates/services/selectors/models` internos de otro modulo.
- [ ] `domain/` y `application/` no importan Django.
- [ ] `application/` no importa adapters internos del modulo.

## Activacion

- [ ] `python manage.py modules sync` crea o sincroniza estados correctamente.
- [ ] Un modulo instalado pero inactivo responde `module_inactive`.
- [ ] Un modulo no instalado deja de publicar sus rutas opcionales.

## No rotura del sistema

- [ ] Los tests existentes relevantes siguen pasando.
- [ ] Las pantallas shell siguen cargando con modulos apagados.
- [ ] Los grupos de modulos inactivos o no instalados no aparecen para alta/edicion de usuarios.

## Seguridad y permisos

- [ ] Las vistas protegidas siguen usando login/grupo ademas del guard modular.
- [ ] No se filtran links ni widgets a modulos inactivos.
- [ ] Las APIs no devuelven `500` por modulo inactivo o removido.

## Frontend

- [ ] El sidebar no muestra accesos a modulos opcionales desactivados.
- [ ] El portal ciudadano no rompe si faltan `turnos` o `conversaciones`.
- [ ] El bubble del chatbot no se renderiza si el modulo esta inactivo.

## Mantenibilidad

- [ ] Existe README general y README de los modulos activables.
- [ ] Existe guia para crear modulos nuevos.
- [ ] Existe plan de migracion y preguntas de control para el equipo.
