# Checklist de validacion final

## Modularidad

- [ ] Cada modulo activable tiene `module.py`.
- [ ] `settings.SYSTEM_MODULES` es la unica fuente de verdad de modulos instalados.
- [ ] Ningun modulo nuevo importa `views/forms/templates` de otro modulo.

## Activacion

- [ ] `sync_module_catalog` crea o sincroniza estados correctamente.
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
