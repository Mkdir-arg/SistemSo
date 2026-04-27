# dashboard

`dashboard` actua como shell/adaptador de reporting transversal.

## Responsabilidad

- Componer widgets y accesos de modulos activos.
- No asumir que `conversaciones`, `chatbot` o futuros modulos existen siempre.

## Regla

Todo acceso a un modulo opcional debe pasar por capacidades renderizadas desde `system_modules`.

## Literalidad fisica

Las views, API, templates y signals del shell viven bajo `interfaces/` o `infrastructure/`. `dashboard` no publica entrypoints top-level para adapters.
