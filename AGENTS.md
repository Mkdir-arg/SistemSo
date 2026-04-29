# AGENTS.md

## Fuente principal del proyecto
- Leer `CLAUDE.md` como documento base de contexto, convenciones y workflow general.
- Si hay conflicto entre instrucciones del prompt actual y `CLAUDE.md`, priorizar el prompt actual.
- Si hay conflicto entre `CLAUDE.md` y el código real del proyecto, priorizar el código real y aclararlo al final.

## Objetivo
Trabajar en este repositorio con cambios chicos, seguros, revisables y consistentes con SistemSo/NODO.

## Reglas de trabajo
- No tocar archivos fuera del alcance pedido.
- No refactorizar de más.
- No renombrar cosas sin necesidad.
- No agregar dependencias nuevas salvo pedido explícito.
- Mantener consistencia con la arquitectura actual del proyecto.
- Antes de implementar, revisar cómo ya está hecho en la app afectada.

## Modo ahorro
- No ejecutar tests, lint, build, docker, migraciones ni comandos costosos salvo que se pidan explícitamente.
- No leer documentación no relacionada con la tarea.
- No recorrer todo el repo si la tarea afecta solo una parte.
- No actualizar changelog, sprint, backlog, arquitectura ni documentación formal salvo pedido explícito.
- No escanear automáticamente `docs/errores/` ni `docs/requerimientos/` salvo que la tarea lo requiera.
- No repetir resúmenes largos si ya fueron dados.

## Lectura mínima obligatoria antes de cambiar código
Para cada tarea:
1. Leer archivos del módulo afectado
2. Leer modelos, views, urls, serializers, forms o admin relacionados
3. Leer `CLAUDE.md` solo si hace falta contexto adicional o convenciones del proyecto
4. Leer documentación específica solo si realmente impacta la tarea

## Historial obligatorio
- Mantener actualizado `docs/tmp/WORKLOG.md`
- Registrar:
  - tarea
  - archivos creados
  - archivos modificados
  - cambios realizados
  - decisiones o supuestos
  - pendientes

## Flujo recomendado
1. Inspeccionar estructura relacionada
2. Resumir hallazgos en pocas líneas
3. Proponer implementación mínima
4. Hacer cambios
5. Mostrar archivos tocados y pendientes

## Para Django
- Reutilizar modelos base existentes si ya existen
- Reutilizar Usuario, Ciudadano, Municipio, Provincia, Localidad o Area si ya existen
- Mantener `verbose_name`, `__str__`, `Meta`, `related_name` y nombres consistentes
- Si se cambia un model, preparar la migración correspondiente solo si fue pedida o si el flujo actual del repositorio lo exige explícitamente

## Templates y frontend
- No tocar frontend salvo pedido explícito
- Si se crea template nuevo, revisar el patrón real del proyecto antes de escribirlo

## Entrega
Al final de cada tarea, informar:
- archivos creados
- archivos modificados
- resumen funcional breve
- pendientes o dudas