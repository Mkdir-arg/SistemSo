# Guia practica de pruebas UI

> Objetivo: probar el sistema desde la interfaz de forma rapida, repetible y con
> evidencia suficiente para decidir si una branch esta lista para revisar.

Esta guia es manual y no agrega infraestructura de automatizacion. Sirve como
contrato operativo para ejecutar pruebas UI hoy y como base para futuros flujos
E2E automatizados.

## Preparacion

1. Levantar el entorno local.

   ```powershell
   docker compose -f docker-compose.hybrid.yml up -d --build
   ```

2. Confirmar que la aplicacion responde.

   ```powershell
   Invoke-WebRequest http://localhost:8000/health/ -UseBasicParsing
   ```

3. Abrir la UI en `http://localhost:8000/`.

4. Definir antes de empezar:
   - Branch bajo prueba.
   - Usuario o rol usado.
   - Flujo exacto a validar.
   - Resultado esperado.
   - Capturas o notas de cualquier error.

## Orden recomendado

Probar primero lo mas barato y general. Avanzar a flujos largos solo si el smoke
basico pasa.

1. Smoke global:
   - La home o login carga sin error visual.
   - El login funciona.
   - El menu lateral/topbar muestra los modulos esperados.
   - Cerrar sesion funciona.

2. Navegacion por rol:
   - Administrador.
   - Operador backoffice.
   - Ciudadano en portal.
   - Rol especifico del modulo que se esta tocando.

3. Flujo principal del cambio:
   - Crear o iniciar el recurso.
   - Editar o completar la accion principal.
   - Validar estado final en pantalla.
   - Volver a entrar al listado o detalle y confirmar persistencia.

4. Regresiones cercanas:
   - Listados afectados.
   - Formularios relacionados.
   - Permisos del modulo.
   - Acciones de aprobar, cancelar, eliminar o confirmar.

## Checklist general por pantalla

Para cada pantalla tocada o cercana al cambio:

- Carga sin error 500.
- No hay contenido vacio inesperado.
- Los textos principales son comprensibles.
- Los botones visibles ejecutan una accion clara.
- Los formularios muestran validaciones utiles.
- Los mensajes de exito o error aparecen despues de guardar.
- Los filtros, busquedas y paginacion siguen funcionando si existen.
- El estado se conserva al refrescar o volver al listado.
- Un usuario sin permiso no puede ejecutar la accion.

## Flujo base de Turnos

Este es el primer flujo candidato para E2E automatizado porque cruza portal
ciudadano, modulo Turnos y backoffice.

### Ciudadano solicita turno

1. Entrar al portal ciudadano.
2. Iniciar sesion con un ciudadano de prueba.
3. Ir a `Mi Perfil` -> `Mis Turnos` -> `Solicitar turno`.
4. Elegir un recurso activo.
5. Elegir un dia con disponibilidad.
6. Elegir un slot horario.
7. Confirmar con un motivo.
8. Validar que el turno quede en estado pendiente si el recurso requiere
   aprobacion.

### Operador aprueba turno

1. Cerrar sesion como ciudadano.
2. Iniciar sesion como operador de turnos.
3. Abrir la bandeja de pendientes.
4. Ubicar el turno por ciudadano, recurso y fecha.
5. Aprobar el turno.
6. Validar mensaje de exito.
7. Confirmar que el turno ya no aparece como pendiente.

### Ciudadano verifica confirmacion

1. Volver a iniciar sesion como el ciudadano.
2. Abrir `Mis Turnos`.
3. Validar que el turno aparece como confirmado.
4. Abrir el detalle si existe y revisar fecha, hora, recurso y motivo.

## Criterio de evidencia

Una prueba UI se considera reportable cuando incluye:

- Fecha y branch probada.
- URL base usada.
- Usuario o rol.
- Pasos ejecutados.
- Resultado esperado y resultado observado.
- Captura de pantalla solo si hubo falla o comportamiento dudoso.

Formato breve sugerido:

```text
Branch:
URL:
Rol:
Flujo:
Resultado:
Evidencia:
Bloquea release: si/no
```

## Cuando automatizar

Automatizar un flujo cuando cumpla al menos una condicion:

- Se repite en cada PR o release.
- Cruza dos o mas roles.
- Ya fallo antes por regresion.
- Tiene alto costo manual.
- Valida reglas de negocio criticas.

Prioridad recomendada:

1. Login y navegacion basica por rol.
2. Turnos: ciudadano solicita, operador aprueba, ciudadano ve confirmado.
3. Formularios CRUD criticos de backoffice.
4. Permisos negativos por rol.
5. Flujos de portal ciudadano con datos persistentes.

## Cierre de una ronda UI

Antes de dar por terminada una prueba:

- Ejecutar al menos un flujo feliz completo.
- Ejecutar una validacion negativa simple si aplica.
- Refrescar la pantalla final y confirmar persistencia.
- Revisar que no haya estados intermedios colgados.
- Registrar cualquier bug con pasos reproducibles.

Si el flujo principal falla, no seguir acumulando pruebas alrededor. Primero
aislar causa, pantalla exacta y accion que rompe.
