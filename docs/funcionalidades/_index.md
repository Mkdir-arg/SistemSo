# Indice de Funcionalidades

> Leer antes de iniciar cualquier tarea. Actualizado por el Documentador en cada Fase 5.
> Cada funcionalidad tiene su propia carpeta con documentos versionados.

## Indice

| Funcionalidad | Carpeta | Version actual | Ultima actualizacion |
|--------------|---------|---------------|---------------------|
| Confirmar Ciudadano RENAPER | `confirmar-ciudadano-renaper/` | v1.0 | 2026-03-04 |
| Mejora de Logging | `mejora-logging/` | v1.0 | 2026-03-05 |
| Portal Ciudadano — Autenticacion y Registro | `portal-ciudadano/` | v1.0 | 2026-03-08 |

---

## Convencion de nombres

- Carpeta: `[slug-funcionalidad]/` — minusculas con guiones
- Documento: `v[X.Y]_[titulo-breve].md`
  - X = version mayor (cambio de arquitectura o modelo)
  - Y = version menor (mejora o ajuste dentro de la funcionalidad)
  - Ejemplo: `v1.0_alta-ciudadano-renaper.md`, `v1.1_agregar-foto-perfil.md`

Cuando se agrega una version nueva → crear un archivo nuevo (no editar el anterior).
El archivo mas reciente es el estado actual.

---

## Aplicaciones del proyecto

| App | Descripcion |
|-----|------------|
| `apps/ciudadanos` | Gestion de ciudadanos |
| `apps/contactos` | Contactos y comunicaciones |
| `apps/derivaciones` | Derivaciones entre areas |
| `apps/institucional` | Datos institucionales |
| `apps/legajos` | Legajos y expedientes |
| `apps/nachec` | Modulo nachec |
| `apps/programas` | Programas y planes |
| `core` | Base, autenticacion, utilidades compartidas |
| `dashboard` | Panel principal |
| `chatbot` | Bot de asistencia |
| `configuracion` | Configuracion del sistema |
| `tramites` | Gestion de tramites |
| `users` | Usuarios y permisos |
| `portal` | Portal publico |
