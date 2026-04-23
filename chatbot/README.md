# chatbot

`chatbot` es un modulo opcional registrado en `system_modules`.

## Estado actual

- Catalogo explicito con `chatbot/module.py`.
- Guards en vistas publicas y administrativas.
- Bubble global y accesos del shell condicionados por capacidades.

## Dependencias permitidas

- Shared kernel: `core`, `users`.
- Shells consumidores: `portal`, `dashboard`, `templates/includes/base.html`.

## Si se desactiva

- Desaparece el acceso en administracion.
- No se renderiza el bubble global.
- Las vistas responden `module_inactive`.
