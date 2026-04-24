# dashboard

`dashboard` actua como shell/adaptador de reporting transversal.

## Responsabilidad

- Componer widgets y accesos de modulos activos.
- No asumir que `conversaciones`, `chatbot` o futuros modulos existen siempre.

## Regla

Todo acceso a un modulo opcional debe pasar por capacidades renderizadas desde `system_modules`.
