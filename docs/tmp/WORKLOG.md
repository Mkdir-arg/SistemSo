# Worklog temporal

## 2026-05-01 - Resolver conflictos PR codex/modular-monolith-strict -> Dev

**Tarea:** Resolver conflictos de merge de `Dev` en `codex/modular-monolith-strict`.

**Archivos creados:**
- `docs/tmp/WORKLOG.md`

**Archivos modificados:**
- `config/settings.py`
- `config/urls.py`
- `conversaciones/interfaces/web/urls.py`
- `conversaciones/interfaces/web/views/public.py`
- `conversaciones/infrastructure/services/portal_bot.py`
- `docs/team/changelog.md`
- `portal_ciudadano/views.py`
- `templates/includes/base.html`
- `templates/includes/sidebar/opciones.html`
- `tramites/application/services.py`
- `tramites/interfaces/api/serializers.py`
- `tramites/interfaces/api/urls.py`
- `tramites/interfaces/api/views.py`
- `tramites/module.py`

**Cambios realizados:**
- Se resolvieron conflictos manteniendo la estructura modular canÃ³nica de la rama del PR.
- Se agregaron `portal_ciudadano` y `reclamos` como apps legacy no modularizadas para no duplicar apps ya declaradas en `config.modules`.
- Se conservaron rutas opcionales por registry modular y se agregaron solo rutas directas para apps nuevas no modularizadas.
- Se moviÃ³ la API nueva de `tramites` a `tramites/interfaces/api` y los services a `tramites/application`.
- Se actualizaron imports legacy de `portal_ciudadano` y `conversaciones`.
- Se aceptÃ³ la eliminaciÃ³n del selector legacy `portal/selectors/ciudadano.py`.

**Decisiones o supuestos:**
- `tramites`, `chatbot`, `conversaciones` y `flujos` siguen publicando rutas mediante `module.py`.
- `portal_ciudadano` y `reclamos` se mantienen como apps directas porque llegaron desde `Dev` sin layout modular.

**Pendientes:**
- Ejecutar tests/checks solo si se pide explÃ­citamente.

## 2026-05-07 - Rediseño configuracion de reclamos

**Tarea:** Reemplazar `reclamos/configuracion/` para que gestione tipos de reclamo con listado filtrable, alta/edicion/inactivacion y campos dinamicos inline.

**Archivos creados:**
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_form.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_detail.html`

**Archivos modificados:**
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/web/urls.py`
- `configuracion/interfaces/web/views/__init__.py`
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/web/forms/__init__.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `reclamos/configuracion/` ahora muestra listado de `TipoReclamo` con filtros por area, prioridad, municipio, estado activo/inactivo y banderas funcionales.
- Se agrego boton `Agregar` para crear nuevos tipos de reclamo.
- Se agregaron acciones de `Detalle`, `Editar` e `Inactivar/Activar` desde el listado.
- Se incorporo formulario de alta/edicion de tipo de reclamo con campos dinamicos inline (agregar multiples en la misma pantalla).
- Se movio la pantalla de catalogos anterior a `reclamos/catalogos/`.

**Decisiones o supuestos:**
- Se interpreto "crear reclamos" como configuracion de `TipoReclamo` (por los campos solicitados).
- `Localidad` no se agrego porque `TipoReclamo` no tiene ese campo en el modelo actual; se mantuvo `Municipio`.

**Pendientes:**
- Validar visualmente en navegador el flujo completo de alta/edicion con multiples campos dinamicos.
- Si se requiere `Localidad` en tipo de reclamo, implicaria cambio de modelo y migracion.

## 2026-05-07 - Ordenar pantalla de alta de tipo de reclamo

**Tarea:** Reorganizar `reclamos/configuracion/agregar/` para reducir confusion y hacer el flujo mas claro.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se rediseño el formulario en 3 bloques visuales y secuenciales: Datos principales, Reglas y Campos extra dinamicos.
- Se explicitaron etiquetas y orden de campos clave (nombre, area, prioridad, sla, municipio, orden).
- Se separaron los booleanos funcionales en una seccion de reglas para lectura rapida.
- Se simplifico la seccion de campos extra, con boton claro de agregar y tarjetas mas legibles por campo.
- Se mejoraron acciones finales (`Cancelar` y `Guardar tipo de reclamo`) para cierre de flujo mas evidente.

**Decisiones o supuestos:**
- Se mantuvo el mismo backend/formset, cambiando solo presentacion y estructura de la UI.

**Pendientes:**
- Validar en navegador con carga real de multiples campos extra y errores de validacion.

## 2026-05-07 - Ajuste UX campos dinamicos (eliminar + boton al final)

**Tarea:** Reordenar campos dinamicos y mejorar acciones de agregar/eliminar en el formulario de tipo de reclamo.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reordeno la grilla de cada campo dinamico (nombre, codigo, tipo, orden, descripcion, ayuda, placeholder, default, longitud, checks).
- Se agrego boton explicito `Eliminar campo extra` por tarjeta.
- El boton `Agregar campo extra` quedo al final del listado, debajo del ultimo campo.
- Se implemento JS para marcar `DELETE` y ocultar la tarjeta al eliminar, compatible con formset de Django.

**Decisiones o supuestos:**
- Se mantiene logica backend existente de formset; el borrado se resuelve con `DELETE`.

**Pendientes:**
- Validar en navegador que el flujo de eliminar/agregar varios campos en secuencia quede correcto.

## 2026-05-07 - Catalogos de reclamos en solapas + limpieza de opciones

**Tarea:** Dejar solo Areas, Estados y Prioridades en catalogos de reclamos; eliminar accesos a transiciones/campos dinamicos; agregar detalle/editar/borrar y listado por solapas.

**Archivos creados:**
- `configuracion/interfaces/templates/configuracion/reclamo_catalogo_detail.html`

**Archivos modificados:**
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/web/urls.py`
- `configuracion/interfaces/web/views/__init__.py`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogo_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `reclamos/catalogos/` paso a una pantalla por solapas (`Areas`, `Estados`, `Prioridades`) con listado y boton `Agregar` en cada solapa.
- Se agregaron acciones por fila: `Detalle`, `Editar` y `Borrar` para los 3 catalogos.
- Se agregaron vistas/rutas de detalle para area/estado/prioridad.
- Se quitaron de URLs publicas de reclamos las rutas de `transiciones-estado`, `campos-dinamicos` y `campos-opciones`.
- Altas/ediciones/bajas de areas/estados/prioridades ahora vuelven al panel de catalogos.

**Decisiones o supuestos:**
- "Eliminar de todos lados" se implemento para el flujo de configuracion de reclamos (UI + rutas publicas del modulo).

**Pendientes:**
- Revisar en navegador que al volver desde crear/editar/borrar conserve solapa activa (hoy vuelve al panel general).

## 2026-05-07 - Renombre de Catalogos a Configuraciones de Reclamos

**Tarea:** Cambiar textos visibles "Catalogo/Catalogos" por "Configuraciones de Reclamos" en el flujo de reclamos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se actualizo titulo de pagina y encabezado principal a `Configuraciones de Reclamos`.
- Se actualizo el boton de acceso desde tipos de reclamo para que diga `Configuraciones de Reclamos`.

**Pendientes:**
- Ninguno.

## 2026-05-07 - Areas como configuracion comun

**Tarea:** Sacar Areas de configuracion de Reclamos/Tramites y moverlo a una seccion comun dentro de Configuracion.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/views/geografia.py`
- `configuracion/interfaces/web/views/__init__.py`
- `configuracion/interfaces/web/urls.py`
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `configuracion/interfaces/web/views/tramites.py`
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se creo seccion comun `Configuracion > Areas` con listado, detalle, alta, edicion y baja.
- Se agregaron rutas nuevas: `configuracion/areas/` (+ crear/detalle/editar/eliminar).
- Se agrego acceso a `Areas` en el submenu general de Configuracion (sidebar).
- Se removio `Areas` del panel `Configuraciones de Reclamos` (solapas quedan Estados y Prioridades).
- Se removio `Areas` del panel de `Configuracion de Tramites`.

**Decisiones o supuestos:**
- Se mantienen rutas legacy de areas dentro de reclamos/tramites para compatibilidad, pero ya no se muestran en UI.

**Pendientes:**
- Si se desea, en un siguiente paso se pueden eliminar rutas/vistas legacy de areas en reclamos/tramites.

## 2026-05-07 - Eliminacion de legacy de Areas en Reclamos y Tramites

**Tarea:** Eliminar definitivamente rutas/vistas/forms legacy de Areas en modulos de reclamos y tramites.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/urls.py`
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/web/views/tramites.py`
- `configuracion/interfaces/web/views/__init__.py`
- `configuracion/interfaces/web/forms/tramites.py`
- `configuracion/interfaces/web/forms/__init__.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se eliminaron rutas `reclamos/configuracion/areas/*`.
- Se eliminaron rutas `tramites/configuracion/areas/*`.
- Se removieron clases de vistas de areas en `views/reclamos.py` y `views/tramites.py`.
- Se limpiaron exportaciones de esas vistas en `views/__init__.py`.
- Se removio `AreaTramiteConfigForm` y su export.

**Pendientes:**
- Ninguno.

## 2026-05-07 - Fix menu Areas + soporte Subareas

**Tarea:** Corregir visual del boton Areas en menu y agregar jerarquia de subareas.

**Archivos creados:**
- `reclamos/migrations/0004_area_parent.py`
- `configuracion/interfaces/templates/configuracion/area_config_list.html`

**Archivos modificados:**
- `reclamos/models.py`
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/web/views/geografia.py`
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego campo `parent` en `Area` para soportar subareas (area padre/subarea).
- Se actualizo `AreaConfigForm` para elegir `parent` (excluye la propia area en edicion).
- Se agrego migracion `0004_area_parent`.
- Se creo listado dedicado `Areas y Subareas` con columna `Area padre`.
- Se ajusto menu de Configuracion para mostrar `Areas y Subareas` con separacion visual respecto de `Localidades`.

**Decisiones o supuestos:**
- Subarea se modela como una `Area` con `parent` definido (jerarquia de un nivel o mas).

**Pendientes:**
- Ejecutar migraciones en entorno (`python manage.py migrate`) para habilitar campo `parent` en BD.

## 2026-05-07 - Separacion Areas/Subareas + formularios dedicados

**Tarea:** Separar Areas y Subareas, reorganizar formularios, quitar municipio y permitir elegir area en subareas.

**Archivos creados:**
- `configuracion/interfaces/templates/configuracion/area_raiz_list.html`
- `configuracion/interfaces/templates/configuracion/subarea_list.html`
- `configuracion/interfaces/templates/configuracion/area_form.html`
- `configuracion/interfaces/templates/configuracion/subarea_form.html`
- `configuracion/interfaces/templates/configuracion/area_detail.html`
- `configuracion/interfaces/templates/configuracion/subarea_detail.html`

**Archivos modificados:**
- `reclamos/models.py`
- `reclamos/migrations/0004_area_parent.py`
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/web/forms/__init__.py`
- `configuracion/interfaces/web/views/geografia.py`
- `configuracion/interfaces/web/views/__init__.py`
- `configuracion/interfaces/web/urls.py`
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se separo gestion en dos secciones: `Areas` y `Subareas`.
- Se crearon formularios dedicados:
  - `AreaRaizConfigForm` (sin municipio ni area padre).
  - `SubareaConfigForm` (sin municipio, con `parent` obligatorio).
- Se agrego jerarquia real en modelo `Area` con campo `parent`.
- Se agregaron rutas y vistas CRUD separadas para subareas.
- Se agregaron templates de listado/form/detalle separados para cada seccion.
- Se corrigio menu de Configuracion para mostrar `Areas` y `Subareas` como items separados (sin superposicion).
- Se agregaron restricciones en vistas para evitar mezclar por URL manual (areas solo raiz, subareas solo hijas).

**Pendientes:**
- Ejecutar migraciones (`python manage.py migrate`) para aplicar `Area.parent` en BD.

## 2026-05-07 - Quitar Municipio de catalogos de Reclamos

**Tarea:** Eliminar campo Municipio de catalogos de reclamos (areas, tipos de reclamo, estados y prioridades).

**Archivos creados:**
- `reclamos/migrations/0005_remove_municipio_catalogos.py`

**Archivos modificados:**
- `reclamos/models.py`
- `reclamos/services.py`
- `reclamos/api_views.py`
- `reclamos/admin.py`
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_detail.html`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se removio `municipio` de modelos: `Area`, `TipoReclamo`, `EstadoReclamo`, `PrioridadReclamo`.
- Se actualizaron constraints unicos para no depender de municipio.
- Se quitaron filtros/select_related por municipio en APIs y vistas de configuracion.
- Se limpio admin para no mostrar ni filtrar por municipio en esos catalogos.
- Se removio municipio de formularios y pantallas de tipos/estados/prioridades.

**Decisiones o supuestos:**
- Se mantuvo `municipio` en el modelo operativo `Reclamo` (ubicacion del reclamo), porque no fue pedido quitarlo de la entidad de reclamo en si.

**Pendientes:**
- Ejecutar migraciones (`python manage.py migrate`).
- Verificar que no existan duplicados de `codigo`/`nombre` que impidan nuevas constraints globales.

## 2026-05-07 - Alta de reclamo con Area + Subarea dependiente

**Tarea:** Permitir seleccionar Area y luego Subarea al crear un reclamo.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregaron campos de formulario `area_principal` y `subarea` en alta de reclamo.
- Se agrego validacion backend para asegurar que la subarea pertenezca al area seleccionada.
- Se guarda en `area_actual` la subarea si existe; si no, el area principal.
- Se adapto inicializacion desde query param `area` para soportar area o subarea.
- Se actualizo template para mostrar Area/Subarea y filtrar subareas en frontend segun area elegida.

**Pendientes:**
- Validar visualmente el flujo en navegador con distintas combinaciones de area/subarea.

## 2026-05-07 - Area/Subarea en alta de tipo de reclamo

**Tarea:** Aplicar selector dependiente Area -> Subarea en `/configuracion/reclamos/configuracion/agregar/`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregaron campos `area_principal` y `subarea` a `TipoReclamoConfigForm`.
- Se oculto `area` real del modelo y se completa automaticamente con subarea (o area principal).
- Se valido backend que subarea pertenezca al area seleccionada.
- Se actualizo template de alta/edicion de tipo de reclamo para mostrar `Area` y `Subarea` con filtrado dependiente en frontend.

**Pendientes:**
- Validar visualmente el flujo en navegador para alta y edicion.

## 2026-05-07 - Renombrar "Nivel" a "Orden de prioridad"

**Tarea:** Mejorar claridad en UI de prioridades de reclamos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se renombro etiqueta del campo `nivel` a `Orden de prioridad` en formulario de prioridades de reclamos.
- Se renombro encabezado de columna `Nivel` a `Orden de prioridad` en listado de prioridades.

**Pendientes:**
- Ninguno.

## 2026-05-07 - Ajuste visual menu Areas/Subareas

**Tarea:** Corregir superposicion visual del boton Areas en submenu de Configuracion.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agruparon `Areas` y `Subareas` en bloque propio dentro del submenu.
- Se agrego separador superior (`border-t`) y espaciado (`mt-1 pt-1 space-y-1`) para evitar montado con el item anterior.

**Pendientes:**
- Validar visualmente en navegador en modo expandido/colapsado.

## 2026-05-07 - Reclamos/Tramites directos en submenu Configuracion

**Tarea:** Quitar boton interno "Configuraciones" para Reclamos y Tramites en submenu de Configuracion.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reemplazaron bloques desplegables de `Reclamos` y `Tramites` por links directos.
- Al hacer click en `Reclamos` o `Tramites` ahora navega directo a sus pantallas de configuracion.
- Se eliminaron chevrons/subniveles "Configuraciones" internos.

**Pendientes:**
- Validar visualmente en navegador el submenu.

## 2026-05-07 - Fix layout vertical en submenu Configuracion

**Tarea:** Corregir botones de Areas/Subareas/Reclamos/Tramites que aparecian en la misma linea.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se forzaron links a `flex w-full items-center` para ocupar ancho completo y apilar verticalmente.
- Ajuste aplicado a `Areas`, `Subareas`, `Reclamos` y `Tramites` dentro de Configuracion.

**Pendientes:**
- Verificar visualmente en navegador.

## 2026-05-07 - Alinear botones de Configuracion sin separador

**Tarea:** Quitar linea/separador en menu y dejar Areas/Subareas/Reclamos/Tramites alineados como el resto.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se elimino bloque con `border-t` que agregaba la linea visible.
- Se normalizaron clases de botones a `block rounded-xl py-2 px-3 text-sm transition-colors`, igual que el resto del submenu.
- Se removieron overrides `flex w-full items-center` para evitar desfasajes.

**Pendientes:**
- Validar visualmente en navegador.

## 2026-05-07 - Fix robusto de apilado vertical en submenu Configuracion

**Tarea:** Evitar que botones se muestren al lado en lugar de uno debajo del otro.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se envolvieron los links de `Areas`, `Subareas`, `Reclamos`, `Tramites` y `Cola Conversaciones` en contenedores `div.w-full`.
- Se mantiene cada link con `block` para forzar fila completa.
- Esto neutraliza cualquier estilo global que los ponga en linea.

**Pendientes:**
- Validar visualmente tras recarga dura del navegador.

## 2026-05-07 - Homogeneizar visual de listados nuevos con Provincias/Municipios

**Tarea:** Alinear listados creados recientemente al patron visual de tablas de configuracion.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/area_raiz_list.html`
- `configuracion/interfaces/templates/configuracion/subarea_list.html`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregaron descripciones bajo titulos para mantener consistencia de encabezado.
- Se normalizaron acciones por fila a iconos (`ver`, `editar`, `eliminar`/toggle) como en listados base.
- Se ajustaron estados vacios con icono grande, texto explicativo y CTA.
- Se conservaron funcionalidades existentes (filtros, tabs, activacion/inactivacion).

**Pendientes:**
- Validacion visual final en navegador sobre desktop y mobile.

## 2026-05-07 - Bajas logicas en Areas/Subareas/Reclamos/Estados/Prioridades

**Tarea:** Convertir eliminaciones fisicas a bajas logicas (`activo=False`).

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/views/geografia.py`
- `configuracion/interfaces/web/views/reclamos.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `AreaConfigDeleteView` ahora inactiva (`activo=False`) en lugar de borrar.
- `SubareaConfigDeleteView` ahora inactiva (`activo=False`) en lugar de borrar.
- `ReclamoCatalogoDeleteBaseView` ahora hace baja logica generica para catalogos de reclamos (incluye tipos, estados, prioridades).

**Pendientes:**
- Verificar funcionalmente en UI que los listados no muestren inactivos cuando corresponda (segun cada pantalla/filtro).

## 2026-05-07 - Portada opcional en Tipo de Reclamo

**Tarea:** Agregar en configuracion de tipo de reclamo la opcion de cargar una imagen de portada.

**Archivos creados:**
- `reclamos/migrations/0006_tiporeclamo_imagen_portada.py`

**Archivos modificados:**
- `reclamos/models.py`
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_form.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego campo opcional `imagen_portada` en `TipoReclamo` (`ImageField`).
- Se agrego migracion para persistir el campo nuevo.
- Se incorporo `imagen_portada` al formulario de alta/edicion de tipo de reclamo.
- Se habilito `multipart/form-data` en el form para permitir subida de archivos.
- Se agrego vista previa de portada actual en edicion y visualizacion en detalle/listado.
- Se elimino del template de tipo de reclamo el bloque residual de `municipio`.

**Decisiones o supuestos:**
- La portada se gestiona en `TipoReclamo` (configuracion) y no en la entidad operativa `Reclamo`.
- Se mantuvo campo opcional para no romper tipos ya existentes.

**Pendientes:**
- Ejecutar `python manage.py migrate` en entorno con Django/venv activo.
- Validar en navegador la carga/actualizacion de imagen en `/configuracion/reclamos/configuracion/agregar/`.

## 2026-05-07 - Badges/filtros de inactivos + homogeneizacion de forms

**Tarea:** Hacer visible la baja logica en listados (badge/filtro) y unificar look de formularios de configuracion.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/views/geografia.py`
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/templates/configuracion/area_raiz_list.html`
- `configuracion/interfaces/templates/configuracion/subarea_list.html`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `configuracion/interfaces/templates/configuracion/area_form.html`
- `configuracion/interfaces/templates/configuracion/subarea_form.html`
- `configuracion/interfaces/templates/configuracion/reclamo_catalogo_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego filtro `Estado (todos/activos/inactivos)` en listados de Areas y Subareas.
- Se agrego filtro de estado en `Configuraciones de Reclamos` (tabs Estados/Prioridades), manteniendo tab activa.
- Se reemplazo estado `Si/No` por badges visuales `Activo` / `Inactivo` en esos listados.
- Se homogeneizaron formularios (`area_form`, `subarea_form`, `reclamo_catalogo_form`) con mismo patron de:
  - link de vuelta arriba
  - titulo + descripcion
  - bloque `Datos...`
  - acciones `Cancelar / Guardar`
- Se mantuvo la estructura legible actual (grid simple, espaciados amplios, labels claros).

**Decisiones o supuestos:**
- Se aplico filtro de activo a los listados mas usados de configuracion (Areas, Subareas, Estados, Prioridades), y se mantuvieron sin cambios las pantallas fuera de este alcance.

**Pendientes:**
- Validacion visual en navegador de filtros y badges en desktop/mobile.

## 2026-05-07 - Jerarquia visual de filtros vs solapas

**Tarea:** Bajar jerarquia visual de filtros para que no compitan con las solapas de secciones.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_catalogos.html`
- `configuracion/interfaces/templates/configuracion/area_raiz_list.html`
- `configuracion/interfaces/templates/configuracion/subarea_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se paso el bloque de filtros a estilo secundario: contenedor suave (`bg-gray-50`, borde tenue), select neutro y acciones ligeras.
- Boton principal de filtro cambio de `Filtrar` fuerte a `Aplicar` con estilo outline.
- `Limpiar` quedo como accion de baja jerarquia (texto suave + hover).
- Se mantuvieron sin cambios las solapas para preservar su prioridad visual.

**Pendientes:**
- Validar visualmente en navegador que la nueva jerarquia se perciba correcta.

## 2026-05-07 - Quitar toggle activo/inactivo en listado de tipos de reclamo

**Tarea:** Remover switch de activacion/inactivacion en `reclamos/configuracion/` y dejar esa accion solo en edicion.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `configuracion/interfaces/web/views/reclamos.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se elimino el boton/switch toggle de la columna de acciones en el listado de tipos de reclamo.
- Se elimino el manejo `POST` en `ReclamoTipoConfiguracionListView` que activaba/inactivaba desde listado.
- Activar/inactivar queda disponible unicamente dentro de la pantalla de edicion (campo `activo` del form).

**Pendientes:**
- Validar visualmente en navegador que el listado ya no muestre toggle y que en edicion siga funcionando el campo `Activo`.

## 2026-05-07 - Ajuste columnas en listado de Tipos de Reclamo

**Tarea:** En el listado, quitar `Portada` y `SLA`, y mostrar `Subarea` junto a `Area`.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se removio columna `Portada`.
- Se removio columna `SLA hs`.
- Se agrego columna `Subarea` al lado de `Area`.
- Logica visual:
  - Si el tipo esta asociado a subarea: `Area` muestra el padre y `Subarea` la hija.
  - Si el tipo esta asociado a area raiz: `Area` muestra esa area y `Subarea` muestra `-`.

**Pendientes:**
- Validar visualmente el listado en navegador.

## 2026-05-07 - Campo Featured en espanol para tipos de reclamo

**Tarea:** Agregar checkbox tipo Featured en configuracion de reclamos y mostrarlo en listado.

**Archivos creados:**
- `reclamos/migrations/0007_tiporeclamo_destacado.py`

**Archivos modificados:**
- `reclamos/models.py`
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_form.html`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego campo booleano `destacado` en `TipoReclamo` (default `False`, indexado).
- Se incorporo el campo al formulario de alta/edicion de tipo de reclamo.
- En UI se muestra como checkbox `Destacado (portada)`.
- Se agrego columna `Destacado` en el listado con badge `Si/No`.

**Decisiones o supuestos:**
- Se eligio el nombre `Destacado` como equivalente en espanol de `Featured`.
- El comportamiento funcional de portada/listado de otros reclamos queda habilitado por este flag para consumirlo luego donde corresponda.

**Pendientes:**
- Ejecutar `python manage.py migrate` en entorno con Django activo.
- Si queres, agrego filtro por `Destacado` en el listado.

## 2026-05-07 - Filtros de Tipos de Reclamo ajustados

**Tarea:** Dejar en `/configuracion/reclamos/configuracion/` solo filtros por nombre/descripcion, area, subarea, prioridad, estado y destacado.

**Archivos modificados:**
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se removieron filtros de `requiere adjunto`, `permite anonimo` y `requiere ubicacion`.
- Se agrego filtro de `Subarea`.
- Se agrego filtro de `Destacado`.
- Backend del listado actualizado para soportar nuevos filtros.
- Se agrego filtrado visual de subareas por area seleccionada en frontend.

**Pendientes:**
- Validar visualmente en navegador que la combinacion area/subarea funcione como se espera.

## 2026-05-07 - Filtros mas compactos en Tipos de Reclamo

**Tarea:** Reducir tamaño de campos y botones de filtros en `/configuracion/reclamos/configuracion/`.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se achicaron `input/select` (padding y tipografia) en bloque de filtros.
- Se achicaron botones `Filtrar` y `Limpiar`.
- Se redujo espaciado general del grid de filtros.

**Pendientes:**
- Validacion visual final en navegador.

## 2026-05-07 - Replica de configuracion de Reclamos en Tramites

**Tarea:** Replicar en Tramites el esquema nuevo de Reclamos (listado de tipos, filtros, alta/edicion/detalle, campos dinamicos inline, catalogos por solapas), sin opcion de anonimo.

**Archivos creados:**
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html`
- `configuracion/interfaces/templates/configuracion/tramite_catalogos.html`
- `tramites/migrations/0004_tipotramite_portada_destacado.py`

**Archivos modificados:**
- `tramites/models.py`
- `configuracion/interfaces/web/forms/tramites.py`
- `configuracion/interfaces/web/forms/__init__.py`
- `configuracion/interfaces/web/views/tramites.py`
- `configuracion/interfaces/web/views/__init__.py`
- `configuracion/interfaces/web/urls.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego en `TipoTramite`:
  - `imagen_portada` (opcional)
  - `destacado` (booleano)
- Se agrego migracion para esos campos.
- Se paso `tramites/configuracion/` a listado de tipos (como Reclamos) con filtros:
  - buscar nombre/descripcion
  - area
  - subarea
  - prioridad
  - estado
  - destacado
- Se agregaron pantallas de alta/edicion/detalle para tipo de tramite, con:
  - selector Area -> Subarea dependiente
  - reglas funcionales
  - campos dinamicos inline (agregar/eliminar)
- Se reemplazo `tramites/catalogos/` por solapas de `Estados` y `Prioridades` con:
  - listado
  - filtro de activos/inactivos
  - acciones detalle/editar/borrar (baja logica)
- Se quitaron del flujo principal de tramites las rutas de configuracion viejas de transiciones/requisitos/campos externos para replicar el enfoque de Reclamos.
- Se removio `municipio` de los formularios de estados y prioridades de tramites (siguiendo el criterio visual/funcional aplicado en reclamos).
- No se agrego ninguna opcion de anonimo en tramites.

**Decisiones o supuestos:**
- Se mantuvo `eliminar` como baja logica (`activo=False`) en catalogos de tramites.
- Se conservaron algunas vistas legacy en codigo, pero ya no se exponen en las rutas principales nuevas.

**Pendientes:**
- Ejecutar `python manage.py migrate` para aplicar `0004_tipotramite_portada_destacado`.
- Validar visualmente en navegador el alta/edicion con campos dinamicos inline en tramites.

## 2026-05-07 - Paginado visible en listados de configuracion

**Tarea:** Agregar controles visibles de paginacion en listados de tipos de Reclamos y Tramites dentro de Configuracion.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_list.html`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego bloque de paginacion visible cuando `is_paginated` es verdadero.
- Se muestra `Pagina X de Y`.
- Se agregaron botones `Anterior` y `Siguiente`.
- Los enlaces preservan todos los filtros activos (`q`, `area`, `subarea`, `prioridad`, `activo`, `destacado`).

**Pendientes:**
- Validar visualmente en navegador con suficientes registros para que haya mas de 1 pagina.

## 2026-05-07 - Listados operativos: quitar boton de configuracion + agregar filtros

**Tarea:** En `/configuracion/reclamos/listado/` y `/configuracion/tramites/listado/`, quitar boton a configuracion y agregar filtros.

**Archivos modificados:**
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/web/views/tramites.py`
- `configuracion/interfaces/templates/configuracion/reclamo_list.html`
- `configuracion/interfaces/templates/configuracion/tramite_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se elimino boton `Configurar Reclamos` del listado operativo de reclamos.
- Se elimino boton `Configurar Tramites` del listado operativo de tramites.
- Se agregaron filtros en ambos listados:
  - buscar por numero/titulo
  - area
  - estado
  - prioridad
- Se implemento filtrado real en backend para esos 3 filtros adicionales.
- Se agrego boton `Limpiar` para resetear filtros.

**Pendientes:**
- Validar visualmente en navegador comportamiento y combinacion de filtros.

## 2026-05-08 - Rediseño detalle de reclamo con solapas operativas

**Tarea:** Reorganizar `/configuracion/reclamos/listado/<id>/` para operadores, con mejor visual y solapas funcionales.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se rehizo la pantalla de detalle con resumen superior por tarjetas (estado, prioridad, area, asignado).
- Se agregaron solapas navegables:
  - `Resumen`
  - `Persona`
  - `Gestion`
  - `Historial de estados`
  - `Derivaciones`
  - `Observaciones`
- Se separaron claramente los bloques operativos:
  - cambio de estado
  - derivar/asignar
  - agregar observacion
- Se dividio visualmente la informacion historica en historial de estados, derivaciones y observaciones.
- Se mantuvo compatibilidad con los formularios y acciones POST existentes (`cambiar_estado`, `derivar`, `seguimiento`).

**Pendientes:**
- Validar visualmente en navegador con datos reales de operador.

## 2026-05-08 - Historial completo por tipo de accion en detalle de reclamo

**Tarea:** Garantizar que operador vea historial de observaciones, cambios de estado y derivaciones con fecha/usuario, y pueda cargar observaciones.

**Archivos modificados:**
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En backend se separaron colecciones de historial por accion:
  - `historial_estados`
  - `historial_derivaciones`
  - `historial_observaciones`
- En UI de detalle:
  - Solapa `Historial de estados` muestra cambios con estado anterior/nuevo + fecha + usuario.
  - Solapa `Derivaciones` muestra historial de derivaciones (area/asignado anterior->nuevo + fecha + usuario) y asignaciones registradas.
  - Solapa `Observaciones` muestra historial de seguimientos y comentarios registrados con fecha/usuario.
- Se mantiene el alta de observaciones desde la solapa `Gestion` con el formulario de seguimiento existente.

**Pendientes:**
- Validar en navegador un flujo completo: agregar observacion, cambiar estado y derivar, confirmando que cada accion impacta en su historial correspondiente.

## 2026-05-08 - Derivacion con selector Area -> Subarea en detalle de reclamo

**Tarea:** Al derivar, elegir area y mostrar subareas dependientes del area seleccionada.

**Archivos modificados:**
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `ReclamoDerivacionForm` ahora incluye:
  - `area_principal` (areas raiz)
  - `subarea` (areas hijas)
  - `area` oculta (destino final)
- Validacion backend:
  - si hay subarea valida, se deriva a subarea
  - si no, se deriva al area principal
  - se valida consistencia area/subarea
- En UI de detalle (solapa Gestion):
  - formulario Derivar muestra `Area` y `Subarea`
  - subareas se filtran en frontend por area seleccionada

**Pendientes:**
- Validar en navegador el flujo de derivar eligiendo solo area, y eligiendo area + subarea.

## 2026-05-08 - Observaciones sin duplicados en detalle de reclamo

**Tarea:** Evitar duplicacion visual en solapa de observaciones/comentarios y mostrar formato lista.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se elimino el doble bloque (`historial de observaciones` + `comentarios registrados`) que generaba sensacion de duplicado.
- Se dejo una unica lista cronologica de observaciones basada en comentarios registrados.
- Se cambio presentacion a formato lista simple con divisores por fila.
- Cada fila muestra fecha, usuario, texto y metadata (interno/publico, visible o no).

**Pendientes:**
- Validar en navegador con varios comentarios para confirmar legibilidad.

## 2026-05-08 - Acciones en su solapa correspondiente + detalle fijo arriba

**Tarea:** Dejar cada accion operativa en su propia solapa y mantener el detalle del reclamo (incluyendo datos del ciudadano) arriba de las tabs.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino la solapa intermedia Gestion para evitar confusion.
- Se renombro Historial de estados a Estados y se mantuvo dentro:
  - formulario de cambio de estado
  - listado historico de cambios
- Se mantuvo Derivaciones con:
  - formulario de derivacion
  - historial de derivaciones/asignaciones
- Se mantuvo Observaciones con:
  - formulario de observacion
  - listado historico de observaciones
- Se conserva arriba de las tabs el bloque fijo Detalle del reclamo con datos generales y datos del ciudadano.

**Pendientes:**
- Validar en navegador la navegacion de tabs y el flujo de carga en cada una.
## 2026-05-08 - Homogeneizacion de tabs + resumen completo en detalle de reclamo

**Tarea:** Homogeneizar estructura visual de solapas y ampliar Resumen para mostrar todos los datos que carga el ciudadano.

**Archivos modificados:**
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se reforzo queryset/contexto del detalle para incluir:
  - djuntos_items activos
  - datos_dinamicos_items con su definicion de campo
  - provincia, municipio, localidad en select_related
- Se homogeneizo visualmente la estructura de tabs (Estados, Derivaciones, Observaciones) con patron comun:
  - formulario arriba
  - historial/listado abajo
- En Resumen se agregaron bloques completos de lectura:
  - Datos principales
  - Ubicacion y lugar (incluye link a mapa si hay coordenadas)
  - Adjuntos e imagenes
  - Campos dinamicos cargados
  - Detalle interno (si existe)
- Se mantiene sin boton Gestion y la solapa se llama Estados.

**Pendientes:**
- Validar en navegador con reclamos que tengan adjuntos, coordenadas y datos dinamicos para verificar formato final de cada valor.
## 2026-05-08 - Observaciones excluyentes (interno vs visible ciudadano)

**Tarea:** Evitar que en observaciones se puedan marcar simultaneamente Comentario interno y Visible para ciudadano.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego validacion en ReclamoSeguimientoForm.clean() para exigir seleccion excluyente.
- Regla aplicada: debe quedar exactamente una opcion activa.
- Si ambas estan tildadas o ambas destildadas, el form devuelve error: Debe seleccionar una sola opcion: comentario interno o visible para ciudadano.

**Pendientes:**
- Validar visualmente en navegador el mensaje de error con ambas opciones tildadas y con ambas desmarcadas.
## 2026-05-08 - Observaciones: checkboxes excluyentes en UI

**Tarea:** Hacer que Comentario interno y Visible para ciudadano se destilden entre si en tiempo real, iniciando oculto para el ciudadano.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego JS en detalle de reclamo para comportamiento excluyente entre ambos checkboxes.
- Estado inicial normalizado: si no hay ninguno marcado, queda marcado Comentario interno (oculto para ciudadano).
- Si se marca uno, el otro se destilda automaticamente.
- Si el usuario intenta desmarcar el unico activo, se marca el otro para mantener una opcion activa.

**Pendientes:**
- Validar visualmente en navegador que el comportamiento se mantenga tambien tras errores de validacion del form.
## 2026-05-08 - Selector de estado con valor actual preseleccionado

**Tarea:** Evitar que en la tab Estados el desplegable aparezca vacio y mostrar por defecto el estado actual del reclamo.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- configuracion/interfaces/web/views/reclamos.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- ReclamoCambioEstadoForm.estado_nuevo ahora usa empty_label=None para quitar opcion vacia (---------).
- En ReclamoConfigDetailView.get_context_data, el estado_form se inicializa con estado_nuevo igual al estado actual del reclamo.
- Resultado: al entrar a Estados, el combo muestra el estado en curso y desde ahi se elige el nuevo.

**Pendientes:**
- Validar visualmente en navegador con distintos reclamos/estados.
## 2026-05-08 - Derivaciones con contexto visual de origen/destino

**Tarea:** Mejorar la vision operativa en derivaciones mostrando claramente donde esta el reclamo y a donde se lo envia.

**Archivos modificados:**
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- El form de derivacion ahora se inicializa con el area/subarea actual del reclamo (no arranca vacio).
- Se agregaron cards informativas arriba del form:
  - Ubicacion actual (area/subarea actual + asignado actual)
  - Destino seleccionado (preview en vivo)
- Se agrego JS para actualizar el preview de destino al cambiar:
  - area
  - subarea
  - usuario asignado

**Pendientes:**
- Validar en navegador que el preview se vea bien en desktop/mobile y con casos area sin subarea.
## 2026-05-08 - Estados: mostrar actual + selector sin estado actual

**Tarea:** Mejorar UX en tab Estados: mostrar estado actual explicitamente y evitar seleccionar el mismo estado en el combo.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego linea informativa: Estado actual: <estado> en el formulario de estados.
- Se cambio etiqueta visual del combo a Cambiar estado a.
- ReclamoCambioEstadoForm ahora recibe current_estado_id y excluye ese estado del queryset de estado_nuevo.
- Se aplico tanto en GET como en POST (incluyendo re-render con errores) para mantener consistencia.

**Pendientes:**
- Validar visualmente en navegador el caso donde no haya otros estados activos disponibles.
## 2026-05-08 - Paginacion visible en listado operativo de Reclamos

**Tarea:** Mostrar paginacion en /configuracion/reclamos/listado/ como en otros listados.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_list.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego bloque visual de paginacion cuando is_paginated es verdadero.
- Se muestra Pagina X de Y.
- Se agregaron botones Anterior y Siguiente.
- Los enlaces mantienen filtros activos (q, rea, estado, prioridad).

**Pendientes:**
- Validar visualmente con mas de 20 registros para confirmar navegacion entre paginas.
## 2026-05-08 - Seguimiento interno no visible en portal ciudadano

**Tarea:** Asegurar que los seguimientos internos de reclamos/tramites no se muestren al ciudadano.

**Archivos modificados:**
- portal_ciudadano/views.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En detalle de solicitud de reclamo (PortalCiudadanoReclamoDetalleSolicitudView) se filtro historial a isible_ciudadano=True.
- En detalle de solicitud de tramite (PortalCiudadanoTramiteDetalleSolicitudView) se filtro historial a isible_ciudadano=True.
- Resultado: cualquier seguimiento interno cargado por area/operador (marcado no visible) ya no aparece en la vista del ciudadano.

**Pendientes:**
- Validar en navegador con un caso real: crear seguimiento interno desde configuracion y confirmar que no aparezca en Mis solicitudes del ciudadano.
## 2026-05-08 - Nueva solapa Seguimiento interno en detalle de reclamo

**Tarea:** Agregar en /configuracion/reclamos/listado/<id>/ una solapa separada para seguimiento interno del area, no visible al ciudadano.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- configuracion/interfaces/web/forms/__init__.py
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se creo ReclamoSeguimientoInternoForm (solo comentario).
- Se agrego accion POST nueva seguimiento_interno en ReclamoConfigDetailView.
- Al guardar seguimiento interno:
  - crea ReclamoComentario con es_interno=True y isible_ciudadano=False
  - registra historial con ccion=seguimiento_interno y isible_ciudadano=False
- Se agrego solapa nueva Seguimiento interno con:
  - formulario propio
  - historial/listado interno
- Observaciones ahora muestra solo comentarios visibles al ciudadano.

**Pendientes:**
- Validar en navegador: alta de seguimiento interno y verificacion de que aparece en su solapa y no en observaciones visibles.
## 2026-05-08 - Solicitud de ampliacion de datos al ciudadano + respuesta con historial

**Tarea:** Permitir pedir nuevamente datos al ciudadano para un reclamo (datos faltantes/incorrectos, adjuntos, ubicacion, campos dinamicos), manteniendo historial sin borrar informacion.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- configuracion/interfaces/web/forms/__init__.py
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Backoffice reclamo detalle (/configuracion/reclamos/listado/<id>/):
  - Nueva solapa Solicitar datos.
  - Nuevo formulario ReclamoSolicitudDatosForm (motivo + flags de direccion/adjuntos/campos + detalle).
  - Nueva accion POST solicitar_datos_ciudadano.
  - La solicitud se registra en historial (ccion=solicitud_datos_ciudadano, isible_ciudadano=True, metadata con flags).
- Portal ciudadano detalle de reclamo (/portal-ciudadano/mis-solicitudes/reclamo/<id>/):
  - Se detecta solicitud pendiente (ultima solicitud sin respuesta posterior).
  - Se muestra bloque para responder con:
    - comentario de respuesta
    - descripcion adicional
    - referencia/direccion/ubicacion (calle, barrio, entre calles, lat/lng)
    - nuevos adjuntos
    - campos adicionales dinamicos
  - Al enviar:
    - se actualizan campos informados del reclamo
    - se guardan nuevos adjuntos
    - se actualizan/crean datos dinamicos cargados
    - se registra comentario y movimiento en historial (ccion=respuesta_solicitud_datos_ciudadano).
- Todo queda auditado en historial; no se elimina informacion historica.

**Pendientes:**
- Validar visualmente el flujo completo operador->ciudadano con datos reales.
- Si queres, en siguiente paso agrego lista explicita en backoffice de solicitudes/respuestas de datos con estado pendiente/resuelta en la misma solapa.
## 2026-05-08 - Solicitud de datos por campo desde Resumen (sin solapa extra)

**Tarea:** Quitar solapa Solicitar datos y permitir solicitar correcciones puntuales desde Resumen, con icono por dato y modal de motivo/detalle.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- configuracion/interfaces/web/forms/__init__.py
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino la solapa Solicitar datos del detalle de reclamo.
- Se agregaron botones/iconos de solicitud dentro de Resumen junto a datos clave (descripcion, direccion/ubicacion, adjuntos y campos dinamicos).
- Al presionar un icono se abre modal con:
  - campo objetivo (automatico)
  - motivo
  - detalle adicional
- Nueva accion POST: solicitar_dato_campo_ciudadano.
- Se registra historial con ccion=solicitud_datos_ciudadano y metadata del campo_objetivo.

**Pendientes:**
- Validar visualmente en navegador el modal y los iconos en todos los bloques de Resumen.
## 2026-05-08 - Simplificacion: sin Seguimiento interno + renombre de Observaciones a Seguimiento

**Tarea:** Eliminar la parte de seguimiento interno por confusion y renombrar Observaciones a Seguimiento.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- configuracion/interfaces/web/forms/__init__.py
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino form de ReclamoSeguimientoInternoForm.
- Se quitaron importaciones, contexto, accion POST y metodo backend de seguimiento_interno.
- Se elimino la solapa Seguimiento interno del detalle de reclamo.
- Se renombro la solapa Observaciones a Seguimiento (tab + titulo + textos de acciones).

**Pendientes:**
- Validar visualmente que la navegacion de tabs quede clara con la nueva nomenclatura.
## 2026-05-08 - Nueva solapa final Historial (completa)

**Tarea:** Agregar una solapa final Historial en detalle de reclamo para ver todo el historial en formato lista.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego nueva tab Historial al final de las solapas.
- Se agrego bloque Historial completo usando historial_items.
- Cada item muestra:
  - fecha/hora
  - usuario
  - accion
  - cambios de estado (anterior->nuevo)
  - cambios de area (anterior->nueva)
  - cambios de asignado (anterior->nuevo)
  - detalle/comentario
  - visibilidad (interno o visible para ciudadano)
- Esto unifica en una sola lista: cambios de estado, derivaciones, pedidos de datos, seguimientos y demas acciones registradas.

**Pendientes:**
- Validar visualmente en navegador con historial variado para ajustar textos de acciones si hace falta.
## 2026-05-08 - Cambio de icono en solicitud de actualizacion de datos

**Tarea:** Cambiar icono de solicitud de actualizacion de datos por uno mas acorde.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se reemplazo a-comment-dots por a-file-pen en todos los botones de solicitud de dato dentro de Resumen.
- Se mantiene la misma funcionalidad (abre modal de solicitud por campo).

**Pendientes:**
- Validar visualmente en navegador que el icono nuevo se renderice correctamente con la version de Font Awesome cargada.
## 2026-05-08 - Ajuste de ubicacion solicitada al ciudadano (sin lat/long)

**Tarea:** Pedir al ciudadano calle y altura, localidad, barrio, referencia y entre calles; ocultar latitud/longitud del flujo ciudadano e impedir solicitar edicion de esos datos.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Backoffice resumen de reclamo:
  - se removieron iconos de solicitud sobre latitud y longitud (ya no se puede pedir edicion de esos datos desde el modal por campo).
- Portal ciudadano (respuesta a solicitud de datos):
  - se quitaron inputs de latitud y longitud.
  - se agregaron inputs para ltura (
umero_calle) y localidad (localidad_texto).
  - se mantienen calle, arrio, eferencia, entre calles y adjuntos.
- Backend de respuesta ciudadana:
  - ya no procesa lat/long.
  - guarda 
umero_calle.
  - intenta resolver localidad por nombre (y municipio del reclamo si existe).
  - si no encuentra localidad exacta, deja constancia en eferencia sin perder trazabilidad.

**Pendientes:**
- Validar visualmente en navegador el flujo con localidad existente/no existente.
## 2026-05-08 - Simplificacion final de ubicacion para respuesta ciudadana

**Tarea:** Dejar el formulario de ampliacion de datos con solo:
- Direccion / referencia (obligatorio)
- Ubicacion en mapa (lat/lng) opcional

**Archivos modificados:**
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino del form ciudadano el resto de campos de ubicacion (calle, altura, localidad, barrio, entre calles).
- Se dejo eferencia como campo obligatorio (frontend + validacion backend).
- Se reintrodujo latitud/longitud como opcionales para geolocalizacion.
- Backend actualizado para guardar solo eferencia (obligatoria) y latitud/longitud (si vienen validas).

**Pendientes:**
- Validar visualmente el flujo y mensajes de error cuando falta direccion/referencia.
## 2026-05-08 - Correccion: ocultar totalmente lat/lng al ciudadano

**Tarea:** Confirmar que latitud/longitud no aparezcan ni se procesen en la respuesta de datos del ciudadano.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
- portal_ciudadano/views.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se eliminaron inputs de latitud y longitud del formulario ciudadano.
- Se elimino procesamiento backend de latitud/longitud en la respuesta a solicitud de datos.
- Se simplifico guardado de ubicacion a eferencia (obligatoria) y se limpio duplicacion residual en ese bloque.

**Pendientes:**
- Validacion visual rapida del formulario en portal ciudadano.
## 2026-05-08 - Historial unificado (movimientos + observaciones)

**Tarea:** Corregir que observaciones creadas en Seguimiento tambien aparezcan en la solapa Historial.

**Archivos modificados:**
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se construyo historial_full_items unificando:
  - ReclamoHistorial (movimientos del flujo)
  - ReclamoComentario (observaciones/seguimientos)
- Se ordena cronologicamente descendente y se limita a 200 items.
- La solapa Historial ahora renderiza ambos tipos:
  - si es movimiento: accion, cambios de estado/area/asignado, detalle, visibilidad
  - si es comentario: accion Seguimiento, texto de observacion, flags interno/publico

**Pendientes:**
- Verificar visualmente en el reclamo afectado que la observacion ya aparezca en historial.
## 2026-05-08 - Toasts en detalle de reclamo

**Tarea:** Mostrar toast en cada accion dentro del detalle de reclamo para confirmar claramente lo ejecutado.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego contenedor fijo de toasts en la vista de detalle.
- Se consumen los messages de Django (success/error/info/warning) y se renderizan como toasts.
- Estilos por tipo:
  - success: verde
  - error: rojo
  - warning: amarillo
  - info/default: gris
- Cada toast aparece con animacion suave y se autocierra.

**Pendientes:**
- Validar visualmente acciones reales (estado, derivacion, seguimiento, solicitud de dato) para confirmar timing y legibilidad.
## 2026-05-08 - Fix seguimiento interno visible + deduplicacion en historial

**Tarea:** Corregir que en Seguimiento se vean comentarios internos y evitar duplicados en Historial para observaciones.

**Archivos modificados:**
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Solapa Seguimiento:
  - ahora usa comentarios_seguimiento_items con todos los comentarios del reclamo (internos y publicos).
  - mensaje vacio actualizado a Sin seguimientos registrados.
- Solapa Historial:
  - se mantiene unificado, pero se deduplican observaciones de ReclamoComentario cuando ya existe ReclamoHistorial equivalente (ccion=seguimiento, mismo usuario/comentario y ventana temporal corta).
  - evita mostrar dos veces la misma observacion (una como historial y otra como comentario).

**Pendientes:**
- Validar en UI con nuevos seguimientos internos/publicos para confirmar que no haya duplicados residuales.
## 2026-05-08 - Filtros tipo pill en Seguimiento (Interno / Visible ciudadano)

**Tarea:** Agregar al lado de Observaciones dos pills para filtrar lista de seguimiento por Interno y Visible ciudadano.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agregaron dos botones pill en cabecera de listado de seguimiento:
  - Interno
  - Visible ciudadano
- Cada fila de seguimiento ahora tiene data attrs (data-es-interno, data-es-visible).
- JS de filtrado en vivo:
  - toggle independiente por cada pill
  - estado activo visual (fondo azul / texto blanco)
  - muestra/oculta filas segun combinacion de filtros activos

**Pendientes:**
- Validar visualmente combinaciones de filtros (ninguno, uno, ambos).
## 2026-05-08 - Manejo de reclamo anonimo en detalle (sin solicitud de edicion)

**Tarea:** Contemplar reclamos anonimos sin errores en datos de persona y bloquear solicitud de edicion de datos.

**Archivos modificados:**
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Backend: se bloquea solicitar_dato_campo_ciudadano si el reclamo es anonimo o no tiene ciudadano asociado (mensaje de error y no procesa).
- UI: en Resumen se ocultan iconos de solicitud de dato cuando es anonimo/sin ciudadano.
- UI: modal de solicitud de dato solo se renderiza para reclamos no anonimos con ciudadano.
- UI: se agrega aviso explicito en resumen para reclamo anonimo indicando que no se pueden pedir ediciones al ciudadano.
- Se mantiene el comportamiento seguro en tab Persona sin errores cuando no hay ciudadano.

**Pendientes:**
- Validar visualmente con un reclamo anonimo real.
## 2026-05-08 - Simplificacion solicitud de edicion de datos (solo Motivo)

**Tarea:** Quitar Detalle adicional en solicitud de edicion de datos al ciudadano y dejar solo Motivo.

**Archivos modificados:**
- configuracion/interfaces/web/forms/reclamos.py
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino campo detalle de ReclamoSolicitudDatoCampoForm.
- Se ajusto backend para no leer/guardar detalle en metadata/comentario.
- Se removio textarea Detalle adicional del modal.
- Flujo final: solicitud por campo con un unico campo Motivo.

**Pendientes:**
- Ninguno.
## 2026-05-08 - Errores de cambio de estado con toast + apertura de solapa

**Tarea:** Evitar que errores de cambio de estado queden ocultos dentro de la solapa sin aviso global.

**Archivos modificados:**
- configuracion/interfaces/web/views/reclamos.py
- configuracion/interfaces/templates/configuracion/reclamo_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En _post_cambiar_estado se agregaron messages.error(...) cuando:
  - el form es invalido
  - falla validacion de reglas de negocio (ej. requiere ubicacion)
- La pantalla ahora abre automaticamente la solapa con error:
  - Estados si falla estado_form
  - Derivaciones si falla derivacion_form
  - Seguimiento si falla seguimiento_form
- Resultado: siempre aparece toast y ademas el usuario cae directamente en la solapa donde esta el error.

**Pendientes:**
- Validar visualmente el flujo con distintos errores para confirmar UX consistente.## 2026-05-08 - Replica operativa de Reclamos en detalle/listado de Tramites

**Tarea:** Replicar en Tramites la experiencia operativa de Reclamos (listado con paginacion, detalle con solapas, historial y acciones con feedback).

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/forms/__init__.py`
- `configuracion/interfaces/web/views/tramites.py`
- `configuracion/interfaces/templates/configuracion/tramite_list.html`
- `configuracion/interfaces/templates/configuracion/tramite_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se exporto `TramiteSolicitudDatoCampoForm` en forms para evitar inconsistencias de import.
- Se agrego paginacion visible en `/configuracion/reclamos/tramites/listado/` con conservacion de filtros.
- En detalle de tramite se completo la UI por solapas con consistencia de Reclamos:
  - tab Persona con bloque visual completo de datos + acceso a legajo.
  - tab Estados con encabezado de cambio y estado actual + selector de nuevo estado.
  - tab Derivaciones con cards de ubicacion actual/destino seleccionado y preview en vivo (area/subarea/asignado).
  - tab Resumen con solicitud de actualizacion por campo (descripcion, direccion, adjuntos, campos dinamicos).
  - aviso explicito cuando no hay ciudadano asociado.
- Se mejoro JS de detalle para:
  - preview de destino de derivacion.
  - nombre legible del campo en modal de solicitud.
  - filtros exclusivos de seguimiento y toasts.
- En backend de detalle de tramite se agregaron `messages.error` en errores de derivacion y seguimiento para feedback via toast.

**Decisiones o supuestos:**
- Se mantuvo latitud/longitud visibles en backoffice de operador (interno), pero sin exponerlos como campo editable para solicitud al ciudadano.

**Pendientes:**
- Validacion visual final en navegador de todos los flujos de tabs en Tramites (estado, derivacion, seguimiento, solicitud de dato por campo).
## 2026-05-08 - Tramites con turno obligatorio + modalidad + agenda por tipo

**Tarea:** Integrar tramites con agenda de turnos para que el tipo de tramite defina recurso de agenda, modalidad (virtual/presencial) y validacion de turno requerido en portal ciudadano.

**Archivos creados:**
- `tramites/migrations/0005_tipotramite_recurso_turnos.py`

**Archivos modificados:**
- `tramites/models.py`
- `configuracion/interfaces/web/forms/tramites.py`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html`
- `portal_ciudadano/forms.py`
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego en `TipoTramite` el campo `recurso_turnos` (FK a `portal.RecursoTurnos`) para asociar cada tipo de tramite con una agenda concreta.
- En configuracion de tipo de tramite:
  - se agrego selector de `Agenda de turnos asociada`.
  - se valida que, si `requiere_turno=true`, exista agenda asociada.
  - se valida que siempre haya al menos una modalidad habilitada (`permite_online` o `permite_presencial`).
- En portal ciudadano (detalle de tramite):
  - se agrega selector de `Modalidad de atencion`.
  - si el tipo requiere turno, se muestra bloque con agenda asociada y boton para ir al calendario de turnos.
  - se valida que la modalidad elegida este permitida por el tipo.
  - se valida que el ciudadano tenga turno vigente (pendiente/confirmado, fecha futura) en la agenda asociada cuando el tramite requiere turno.
- En confirmacion/envio de tramite:
  - se persiste modalidad en borrador y se muestra en resumen.
  - si hay turno validado, se muestra codigo en resumen.
  - al crear el tramite se guarda:
    - `origen=presencial` si modalidad presencial, sino `web`.
    - `canal_detalle` con la modalidad.
    - `externo_id` con referencia a turno (`turno:<id>`) si aplica.
  - historial incluye metadata de modalidad y turno vinculado.

**Decisiones o supuestos:**
- Se vinculo agenda por `RecursoTurnos` (modelo usado por el flujo ciudadano actual).
- El requisito de turno se satisface con un turno vigente del ciudadano en la agenda asociada al tipo.

**Pendientes:**
- Ejecutar migraciones para aplicar `TipoTramite.recurso_turnos`.
- Si se quiere endurecer mas, se puede exigir que el turno sea del mismo dia/rango respecto a la solicitud.
## 2026-05-08 - Accesos directos a agenda de turnos desde Tipos de Tramite

**Tarea:** Agregar acceso directo desde configuracion de tipos de tramite hacia agenda/turnos, incluyendo acceso a grilla semanal de la agenda asociada.

**Archivos modificados:**
- `configuracion/interfaces/web/views/tramites.py`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego en listado de tipos de tramite:
  - referencia visible a `Turnos > Configuraciones`.
  - icono de acceso directo por fila:
    - si el tipo tiene agenda asociada con configuracion: va a `Agenda semanal`.
    - si no: va a `Configurar agenda`.
- Se agrego en detalle del tipo de tramite:
  - boton `Turnos` (lista de configuraciones).
  - boton `Agenda semanal` cuando existe configuracion de agenda asociada.
  - link contextual junto al campo `Agenda de turnos` para abrir semanal o configurar.
- Se optimizo queryset de tipos para traer `recurso_turnos` y `configuracion_turnos` con `select_related`.

**Pendientes:**
- Ninguno.
## 2026-05-08 - Agregado Turnos en menu de Configuracion

**Tarea:** Mostrar acceso visible a Turnos dentro del submenu Configuracion.

**Archivos modificados:**
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego flag `turnos_active` usando `module_active`.
- Se agrego item `Turnos` en `Configuracion` que apunta a `turnos:configuracion_lista`.
- Se agrego estado activo visual cuando la ruta actual pertenece a `turnos/`.

**Pendientes:**
- Ninguno.
## 2026-05-08 - Rediseño de creacion de Agenda (Area/Subarea/Tramite + carga semanal)

**Tarea:** Hacer más intuitiva la creación de agenda para turnos de trámites: seleccionar area/subarea/trámite, luego definir duración y cargar disponibilidad por múltiples días/rangos.

**Archivos modificados:**
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_form.html`
- `docs/tmp/WORKLOG.md`

**Archivos creados:**
- Ninguno

**Cambios realizados:**
- Form de creación de configuración de agenda:
  - se agregaron campos guiados `Area`, `Subarea`, `Tramite`.
  - se agregó validación de consistencia entre selección de área/subárea y trámite.
  - se mantuvo el resto de parámetros operativos de agenda (modo, anticipación, cancelación, etc.).
- Al crear una configuración de agenda con trámite:
  - se crea/obtiene `RecursoTurnos` para el trámite.
  - se vincula `RecursoTurnos.configuracion_turnos` a la nueva agenda.
  - se vincula `TipoTramite.recurso_turnos` al recurso creado.
- Form de disponibilidad semanal:
  - se agregó selección múltiple de `Días de la semana` en alta.
  - con un solo rango horario + duración + cupo, crea franjas para todos los días elegidos.
  - si algún día ya tenía esa franja, se omite y se informa en mensaje.
  - se conserva validación de rango horario y cálculo de slots según duración.
- UX:
  - en alta dice `Guardar franjas` (plural) para reflejar carga múltiple.

**Decisiones o supuestos:**
- "Cantidad de turnos por rango horario" se interpreta como slots generados por `rango / duración`; y `cupo_maximo` se mantiene como cupo por slot.
- La vinculación agenda-trámite se resuelve por `RecursoTurnos`, que es el puente ya existente con el flujo ciudadano.

**Pendientes:**
- Si se quiere, en un siguiente paso se puede ocultar campos avanzados (modo/anticipación/cancelación) detrás de "Opciones avanzadas" para simplificar aún más la primera carga.
## 2026-05-08 - Fix filtro Area/Subarea -> Tramite en Agenda nueva

**Tarea:** Corregir que en `/turnos/configuraciones/nueva/` no listaba tramites al elegir area/subarea y ajustar formato visual del formulario.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reemplazo el filtro de tramites por texto por un filtro por IDs reales (`data-area`, `data-subarea`).
- El select de tramites ahora se renderiza con metadata por opcion para filtrar correctamente al cambiar area/subarea.
- Se reorganizo visualmente el form en bloques:
  - `Relacion de Agenda` (area/subarea/tramite)
  - `Parametros de Agenda` (nombre y reglas)
- Se amplio el ancho del contenedor para mejor legibilidad y consistencia con formularios de configuracion.

**Pendientes:**
- Validacion visual final en navegador con casos de area sin subareas y area con varias subareas.
## 2026-05-08 - Nombre de Agenda fijo por tramite

**Tarea:** Hacer que el nombre de la agenda sea el nombre del tramite seleccionado.

**Archivos modificados:**
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Backend: en `ConfiguracionTurnosForm.clean()` se fuerza `nombre = tipo_tramite.nombre` cuando hay tramite seleccionado.
- UI: el campo `nombre` queda readonly y se sincroniza automaticamente al cambiar el tramite en pantalla.
- Se agrega texto de ayuda indicando que el nombre se completa automaticamente.

**Pendientes:**
- Ninguno.
## 2026-05-08 - Fix TemplateSyntaxError en grilla semanal de Agenda

**Tarea:** Resolver error `Invalid filter: 'dict_key'` en `/turnos/configuraciones/<id>/disponibilidad/`.

**Archivos modificados:**
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se eliminó dependencia del filtro `dict_key` en template.
- La vista ahora expone `dias_con_franjas` (dia_num, dia_nombre, lista_franjas).
- El template itera directamente `franjas` por cada día.

**Pendientes:**
- Ninguno.
## 2026-05-08 - Disponibilidad por inicio + duracion + slots

**Tarea:** Cambiar la carga de franjas para definir hora de inicio, duracion de turno y cantidad de slots por rango (en lugar de hora fin manual).

**Archivos modificados:**
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego campo `cantidad_slots` al formulario de disponibilidad.
- `hora_fin` ahora se calcula automaticamente en `clean()` como:
  - `hora_inicio + (duracion_turno_min * cantidad_slots)`.
- Se mantiene soporte de alta multiple por dias y la validacion existente.
- En edicion, se inicializa `cantidad_slots` a partir del rango ya guardado.
- UI de disponibilidad actualizada:
  - inputs visibles: `hora_inicio`, `duracion_turno_min`, `cantidad_slots`, `cupo_maximo`.
  - preview muestra slots, duracion y rango estimado calculado.

**Pendientes:**
- Ninguno.
## 2026-05-08 - Validacion: la franja no puede cruzar de día

**Tarea:** Impedir guardar franjas de agenda cuyo rango calculado pase al día siguiente.

**Archivos modificados:**
- `turnos/interfaces/web/forms/__init__.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En `DisponibilidadConfiguracionForm.clean()` se agrega validación:
  - si `hora_inicio + (duracion * slots)` cambia de fecha, se lanza error de validación.
- Mensaje mostrado: `El rango horario no puede cruzar de día. Ajusta duración o cantidad de slots.`

**Pendientes:**
- Ninguno.
## 2026-05-08 - Simplificacion de disponibilidad: slots sin cupo variable

**Tarea:** Reorganizar disponibilidad para evitar confusion entre cantidad de slots y cupo.

**Archivos modificados:**
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_form.html`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se dejo `cupo_maximo` fijo en 1 por slot (backend), ocultando el campo en formulario.
- Se mantiene la configuracion por `hora_inicio + duracion + cantidad_slots`.
- En UI se aclara: `Cada slot admite 1 turno (cupo fijo)`.
- En la grilla semanal se removio la visualizacion `c/x` para evitar ruido conceptual.

**Decisiones o supuestos:**
- Para este flujo, `slots` representa cantidad de turnos en el rango y no se necesita cupo adicional por slot.

**Pendientes:**
- Si mas adelante se requiere atender mas de 1 persona por horario, se puede reactivar `cupo_maximo` como opcion avanzada.
## 2026-05-08 - Ajuste semantico de slots por rango (cupo por turno)

**Tarea:** Corregir la logica para que `slots` represente cupo dentro del mismo rango y no cantidad de rangos consecutivos.

**Archivos modificados:**
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_form.html`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`
- `turnos/interfaces/web/views/configuracion.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Nuevo comportamiento:
  - `hora_fin = hora_inicio + duracion_turno_min`
  - `slots en este rango` se guarda en `cupo_maximo`.
- En edicion, `cantidad_slots` ahora se inicializa con `cupo_maximo`.
- Preview del form actualizado para mostrar cupo en el rango (no cantidad de sub-rangos).
- Grilla semanal actualizada para mostrar `{{ disp.cupo_maximo }} slots`.
- Mensaje de alta actualizado: rango por duracion y cantidad de slots de cupo.

**Pendientes:**
- Ninguno.

## 2026-05-08 - Fix crash PasswordResetView en portal ciudadano

**Tarea:** Corregir error de arranque en `portal_ciudadano/views.py` (`NameError: PasswordResetView is not defined`) reportado en logs de app.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregaron imports faltantes de vistas auth de Django:
  - `PasswordResetView`
  - `PasswordResetDoneView`
  - `PasswordResetConfirmView`
  - `PasswordResetCompleteView`
- Se agregó `reverse_lazy` al import de `django.urls`.
- Se agregó el import faltante de `CiudadanoPasswordResetForm` desde `.forms`.

**Decisiones o supuestos:**
- Se corrigió de forma mínima y segura sin tocar lógica adicional del flujo portal.

**Pendientes:**
- Verificar en contenedor/app levantada que el arranque ya no falle por ese NameError.
- Continuar ajuste visual de la grilla semanal de disponibilidad de turnos según feedback UX.

## 2026-05-08 - Campos dinámicos de reclamo: opciones en selección + tipo horario

**Tarea:** En editar tipo de reclamo (`/configuracion/reclamos/configuracion/<id>/editar/`), permitir cargar opciones cuando el tipo de campo dinámico sea selección y agregar tipo de dato horario.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `reclamos/models.py`
- `reclamos/services.py`
- `configuracion/interfaces/web/forms/reclamos.py`
- `configuracion/interfaces/web/views/reclamos.py`
- `configuracion/interfaces/templates/configuracion/reclamo_tipo_configuracion_form.html`
- `portal_ciudadano/views.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregó `horario` a `CampoDinamicoReclamo.TipoDato`.
- Se agregó validación de valores `horario` en services (`HH:MM`).
- En el inline form de campos dinámicos de reclamo se agregó `opciones_texto` (una opción por línea).
- Validación: si tipo es `selección`, exige al menos una opción.
- En el guardado del tipo de reclamo se sincronizan opciones:
  - crea/actualiza opciones activas según texto cargado
  - inactiva opciones removidas
  - si el tipo deja de ser `selección`, inactiva sus opciones.
- En UI del form de tipo de reclamo se agregó bloque de opciones por campo dinámico y lógica JS para mostrarlo solo cuando el tipo es `selección`.
- En portal ciudadano, `horario` se renderiza como input `time`.

**Decisiones o supuestos:**
- Para minimizar cambios de schema, se reutilizó `CampoDinamicoOpcion` existente y se administró inline desde el mismo form.
- El valor técnico de cada opción se guarda igual que su etiqueta (consistente con uso actual).

**Pendientes:**
- Validación visual manual del formulario en navegador.
- Si se quiere, puedo replicar exactamente el mismo patrón en tipos de trámite para mantener simetría total.

## 2026-05-08 - Ayudas de campos en tooltip con icono ?

**Tarea:** Cambiar la visualización de ayudas de campos dinámicos en portal ciudadano para mostrarlas en burbuja al pasar por un icono `?`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregó componente visual `help-tooltip` en ambos templates.
- El texto de ayuda (`campo.ayuda`) ahora se muestra dentro de una burbuja hover sobre un icono `?` al lado del label del campo.
- Se eliminó el render de ayuda como texto fijo debajo del input para campos dinámicos.

**Decisiones o supuestos:**
- Se aplicó solo a ayudas de campos dinámicos (`campos_extra`) en reclamos y trámites, manteniendo ayudas generales existentes (como mensaje de agenda) sin cambios.

**Pendientes:**
- Validación visual en mobile para verificar que el tooltip no quede cortado según ancho de pantalla.

## 2026-05-08 - Fix visual de campo horario en portal ciudadano

**Tarea:** Corregir visual de campos dinámicos tipo horario en front de reclamos/trámites.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregó `input[type="time"]` al bloque de estilos compartidos de inputs en ambos templates, para que herede el mismo look and feel de texto/fecha/etc.

**Pendientes:**
- Validar visualmente en navegador (desktop/mobile) que el control horario se vea consistente según el navegador.

## 2026-05-08 - Mostrar área seleccionada en detalle de reclamo ciudadano

**Tarea:** Hacer visible en `/portal-ciudadano/reclamos/detalle/` el área a la que se está cargando la solicitud.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregó un bloque visual en el hero con texto `Área seleccionada: <nombre>` usando `area` del contexto.
- Se añadieron estilos para presentar el área como chip legible y consistente con el encabezado.

**Pendientes:**
- Validar visualmente en mobile y con áreas de nombre largo.

## 2026-05-08 - Portal reclamos: destacados en cards + resto en listado

**Tarea:** En `/portal-ciudadano/reclamos/` mostrar tipos de reclamo (no áreas), con destacados en cards y no destacados en listado.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- La vista ahora carga `TipoReclamo` activos y separa en `tipos_destacados` y `tipos_otros`.
- Se dejó de renderizar la lista por `Area` en esa pantalla.
- El template muestra:
  - destacados en cards
  - no destacados en listado vertical
- En ambos casos se muestra `nombre` del tipo de reclamo.
- Los links al detalle envían `area=<area_id>&tipo=<tipo_id>` para mantener el flujo existente.
- Se ajustó copy del hero y el paso de progreso (`Tipo` en lugar de `Área`).

**Pendientes:**
- Validar visualmente casos con muchos destacados (posible paginado o límite visual si se desea).

## 2026-05-08 - Ranking automático de tipos de reclamo en portal ciudadano

**Tarea:** Mostrar Top 6 tipos de reclamo más usados como destacados y el resto en lista en 3 columnas en `/portal-ciudadano/reclamos/`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregó ranking por uso real de tipos de reclamo (`Count` de reclamos activos por tipo).
- Si hay datos de uso:
  - Top 6 se muestran en destacados.
  - El resto se muestra en bloque inferior.
- Si no hay datos de uso, se mantiene fallback por `destacado` manual.
- Se adaptó el bloque inferior para visualizarse en grilla de 3 columnas (responsive a 2 y 1 en breakpoints menores).

**Decisiones o supuestos:**
- Ranking basado en histórico de reclamos activos (no acotado por fecha) para una implementación mínima sin tareas programadas.

**Pendientes:**
- Si se requiere ventana temporal (ej. últimos 90 días), agregar filtro por fecha sobre `fecha_ingreso`.

## 2026-05-08 - Replicar mejoras de reclamos en trámites

**Tarea:** Aplicar en trámites el mismo enfoque que en reclamos: ranking en portal (top + resto), y mejoras de campos dinámicos (tipo horario y opciones inline para selección).

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `tramites/models.py`
- `tramites/application/services.py`
- `configuracion/interfaces/web/forms/tramites.py`
- `configuracion/interfaces/web/views/tramites.py`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html`
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregó `horario` como tipo de dato en `CampoDinamicoTramite`.
- Se agregó validación de horario `HH:MM` en servicios de trámites.
- En el inline de campos dinámicos de tipo de trámite:
  - se agregó `opciones_texto` (una por línea)
  - validación obligatoria cuando `tipo_dato = selección`
  - UI condicional para mostrar opciones solo en tipo selección.
- En guardado de tipo de trámite se sincronizan opciones dinámicas:
  - crea/actualiza activas
  - inactiva removidas
  - inactiva todas si el campo deja de ser selección.
- Portal ciudadano de trámites:
  - ranking por uso real (`Count` de trámites activos por tipo)
  - top 6 en cards destacadas
  - resto en grilla de 3 columnas (responsive 2/1)
  - fallback a destacados manuales cuando no hay historial de uso.

**Pendientes:**
- Validación visual manual de la pantalla de tipos de trámite y del formulario de edición de tipo de trámite.
- Si querés, puedo agregar período temporal al ranking (ej. últimos 90 días) igual que propusimos para reclamos.

## 2026-05-08 - Ranking por período editable + buscador en portal ciudadano

**Tarea:** Permitir ranking por período editable y agregar buscador en listados de reclamos/trámites del portal ciudadano.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En vistas de listado (`PortalCiudadanoReclamosView` y `PortalCiudadanoTramitesView`):
  - se agregó filtro `q` (buscador por nombre/descripción)
  - se agregó `ranking_days` editable por GET
  - ranking por uso ahora respeta período:
    - `ranking_days > 0`: últimos N días
    - `ranking_days = 0`: histórico total
- En templates de listados de reclamos y trámites:
  - se agregó barra de filtros con buscador + selector de período + botón aplicar
  - se mantienen top 6 en cards y resto en grilla/lista según diseño actual

**Decisiones o supuestos:**
- Se dejó editable desde el propio portal (sin nueva pantalla administrativa), para aplicar cambios inmediatos y visibles.
- Opciones de período: 30, 60, 90, 180, 365 y total histórico.

**Pendientes:**
- Si querés persistir una configuración global por municipio/instancia (en DB), puedo agregar modelo + pantalla de configuración y que estos valores sean default del portal.

## 2026-05-08 - Fix NameError timezone en listados portal ciudadano

**Tarea:** Corregir error `name 'timezone' is not defined` en `/portal-ciudadano/reclamos/` y `/portal-ciudadano/tramites/` tras agregar ranking por período.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregó import faltante: `from django.utils import timezone`.

**Resultado esperado:**
- Vuelven a funcionar ambos listados sin NameError.

## 2026-05-08 - Ajuste de flujo portal ciudadano (login/registro obligatorio antes de detalle)

**Tarea:** Implementar flujo: listado público de reclamos/trámites, selección de tipo, y acceso a detalle solo autenticado con retorno por `next` luego de login/registro.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `portal_ciudadano/templates/portal_ciudadano/login.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `PortalCiudadanoAuthTemplateView`: redirección a login con `?next=<ruta_actual>` para conservar destino exacto.
- `PortalCiudadanoReclamoDetalleView`: ahora requiere autenticación (hereda de `PortalCiudadanoAuthTemplateView`).
- `PortalCiudadanoTramitesView`: pasa a ser listado público (TemplateView), con soporte visual para usuario no logueado.
- `tramites.html`: ajustes de header para estado autenticado/no autenticado.
- `login.html`: link `Crear cuenta` ahora conserva `next` para volver al tipo seleccionado después del registro.
- `PortalCiudadanoReclamosView`: listado siempre visible (sin gating por anónimo), y se desactiva selector inicial.
- `PortalCiudadanoLoginView`: se desactiva botón de reclamo anónimo (`mostrar_boton_reclamo_anonimo = False`).

**Resultado esperado:**
- Usuario no logueado puede ver listados, al seleccionar tipo va a login/registro y luego vuelve directo al formulario elegido.

**Pendientes:**
- Validar manualmente navegación completa de ambos flujos (`reclamos` y `tramites`) incluyendo creación de cuenta nueva.

## 2026-05-08 - Restaurar camino de reclamo anónimo desde login

**Tarea:** Permitir continuar como anónimo cuando el usuario llega al login tras seleccionar un reclamo.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/login.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se restauró la lógica para mostrar botón de reclamo anónimo en login cuando el `next` pertenece a flujo de reclamos.
- Se agregó `anonimo_reclamo_url` dinámico:
  - si hay `next` de reclamos, redirige a ese destino con `anonimo_reclamo=1`
  - fallback a `/portal-ciudadano/reclamos/?anonimo=1`
- `PortalCiudadanoReclamoDetalleView` vuelve a permitir acceso sin login para soportar el flujo anónimo.

## 2026-05-08 - Limpieza de texto descriptivo en detalle de trámite

**Tarea:** Eliminar texto "Mostramos los requisitos y campos adicionales configurados para este trámite." en pantalla de detalle de trámite ciudadano.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se removió el párrafo solicitado del bloque `extra-card`.
- Se verificó `reclamos_detalle` y no tenía ese texto equivalente para eliminar.

## 2026-05-08 - Ranking interno oculto en portal ciudadano

**Tarea:** Ocultar cualquier control/indicio de ranking en portal ciudadano, manteniendo ranking solo para lógica interna de destacados.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se quitó selector de período de ranking de ambos listados del portal.
- Se removió propagación de `ranking_days` en enlaces del frontend.
- En backend se fijó período interno a 90 días (no visible para ciudadano).
- Se mantiene buscador visible y funcional.

## 2026-05-08 - Fix home logueado: acceso directo a listados de reclamos/trámites

**Tarea:** Evitar que usuario ya autenticado pase por login/mi perfil al elegir iniciar trámite o solicitud desde home.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/home.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En las cards de home:
  - `Trámites`: si está logueado va directo a `/portal-ciudadano/tramites/`, si no, a login con `next`.
  - `Solicitudes/Reclamos`: si está logueado va directo a `/portal-ciudadano/reclamos/`, si no, a login con `next`.

## 2026-05-08 - Fix visual buscador tapado por cards destacadas

**Tarea:** Corregir en portal ciudadano que la barra de búsqueda quede visible por encima de las cards destacadas en reclamos y trámites.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reajustó posicionamiento/espaciado entre hero, barra de filtros y cards:
  - filtros pasan a superponerse al hero con z-index superior
  - cards bajan por debajo del buscador
- Se ajustó también en breakpoint móvil para evitar solapamiento.

## 2026-05-08 - Encabezado claro Area/Subarea/Solicitud y eliminación de select incorrecto en reclamos detalle

**Tarea:** En formularios de portal ciudadano (reclamos y trámites), mostrar cabecera con Área/Subárea/Solicitud sobre y quitar select de subárea en reclamos.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Backend:
  - se calcula `area_principal_nombre` y `subarea_nombre` desde el tipo seleccionado (`tipo.area`/`tipo.area.parent`).
- Reclamos detalle:
  - se muestra cabecera con:
    - Área
    - Subárea
    - Solicitud sobre
  - se eliminó el select “Sub-Área” del form.
  - se mantiene `tipo_id` como campo hidden (tipo fijo elegido previamente).
- Trámites detalle:
  - se ajustó la cabecera para mostrar:
    - Área
    - Subárea
    - Solicitud sobre

**Resultado:**
- Ya no se puede cambiar erróneamente el tipo/subárea en la pantalla de carga.
- El ciudadano ve claramente contexto de lo que está cargando.

## 2026-05-08 - Mapa automático por dirección en reclamo ciudadano

**Tarea:** Activar mapa en formulario de reclamo cuando el ciudadano escribe dirección.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se integró Leaflet + OpenStreetMap en el detalle de reclamo.
- Se agregó bloque de mapa debajo de `Dirección / ubicación`.
- Se agregó geocodificación con Nominatim al escribir/blur de dirección (debounce 700ms).
- Se coloca marcador y centra el mapa en la ubicación aproximada encontrada.
- No se muestran ni se piden latitud/longitud al ciudadano.

## 2026-05-08 - Sedes para trámites y agendas por sede

**Tarea:** Incorporar sedes para que no todos los trámites estén en todas las sedes, y configurar agendas por `Sede + Trámite`.

**Archivos creados:**
- `turnos/interfaces/templates/turnos/backoffice/sedes_lista.html`
- `turnos/interfaces/templates/turnos/backoffice/sede_form.html`
- `turnos/migrations/0002_sedeturno_configuracion_sede.py`

**Archivos modificados:**
- `turnos/models.py`
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/web/views/backoffice.py`
- `turnos/interfaces/web/urls.py`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`
- `turnos/admin.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Nuevo modelo `SedeTurno` con:
  - nombre, direccion, telefono, activo
  - `tramites_habilitados` (M2M a `TipoTramite`)
- `ConfiguracionTurnos` ahora guarda:
  - `sede` (FK)
  - `tipo_tramite` (FK)
- En configuración de agenda:
  - se agrega selector de `Sede`
  - se valida que el `Trámite` pertenezca a la sede
  - se exige sede al seleccionar trámite
  - filtro frontend de trámites por sede/área/subárea
- Se agregaron pantallas de backoffice para sedes:
  - listado
  - crear
  - editar
- Se agregaron rutas nuevas en `turnos/` para sedes.
- Se agregó acceso “Sedes” en listado de configuraciones y acceso rápido desde form de configuración.

**Decisiones o supuestos:**
- Se mantuvo compatibilidad con el flujo existente de `RecursoTurnos` y agenda; el nombre/descripcion del recurso se arma con `Trámite + Sede`.

**Pendientes:**
- Aplicar migraciones en entorno (`python manage.py migrate`) para habilitar las nuevas tablas/campos.
- Ajustar flujo ciudadano de trámites con turno para, al elegir trámite con varias sedes, pedir sede antes de reservar turno (si querés lo hago en el siguiente paso).

## 2026-05-08 - Flujo ciudadano de tramite con turno por sede

**Tarea:** Ajustar portal ciudadano para que, si un tramite requiere turno y tiene varias sedes, primero se elija sede y luego se reserve turno en la agenda de esa sede.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En `PortalCiudadanoTramiteDetalleView`:
  - se agrego resolucion de sedes con agenda activa por `tipo_tramite` usando `ConfiguracionTurnos + RecursoTurnos`.
  - se expone al template `tramite_sedes_agenda` y `tramite_sede_seleccionada_id`.
  - al guardar draft:
    - valida sede seleccionada (si hay varias).
    - guarda `sede_id`, `sede_nombre`, `recurso_turnos_id`, `turno_id_vinculado`, `turno_codigo_vinculado`.
    - valida turno vigente contra la agenda (`recurso_turnos_id`) de la sede elegida.
- En `PortalCiudadanoTramiteConfirmarView`:
  - la validacion del turno vinculado ahora usa `draft.recurso_turnos_id` (agenda de sede), no `tipo.recurso_turnos_id`.
  - se agrega `sede_id` y `sede_nombre` al metadata del historial.
- En template `tramites_detalle.html`:
  - si hay varias sedes, muestra selector `Sede` obligatorio.
  - si hay una sola sede, la muestra fija y setea hidden `sede_id`.
  - boton `Elegir turno` actualiza dinamicamente el link de agenda segun sede seleccionada.

**Decisiones o supuestos:**
- Se toma como fuente de verdad de agenda por sede la entidad `ConfiguracionTurnos` asociada a `tipo_tramite` y `sede`, con `recursoturnos` activo.

**Pendientes:**
- Revisar UX final por navegador (confirmar redireccion a agenda correcta de sede y regreso al formulario con turno reservado).

## 2026-05-09 - Ajuste visual formulario de Sedes

**Tarea:** Homogeneizar layout de `/turnos/sedes/nueva/` con el resto de formularios del sitio.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/sede_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se unifico el contenedor al ancho `max-w-4xl` como otros forms de turnos.
- Se reorganizo en bloques con titulos: "Datos de la sede" y "Tramites habilitados".
- Se agregaron ayudas y errores por campo con el mismo patron visual del resto.
- El switch de activa se mostro como card/label consistente con configuraciones.
- Se mantuvieron acciones y breadcrumb del flujo actual.

**Pendientes:**
- Validar en pantalla mobile y desktop que el render de `tramites_habilitados` quede correcto segun cantidad de items.

## 2026-05-09 - Ajuste visual listado de Sedes

**Tarea:** Homogeneizar `/turnos/sedes/` con el layout de listados del sitio.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/sedes_lista.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se rearmo el encabezado con mismo patron visual (titulo, subtitulo y botones de accion).
- Se agrego boton secundario `Agenda` y boton primario `Nueva sede` consistente.
- Tabla con estilos unificados (thead, hover, pills de estado activa/inactiva, acciones).
- Estado vacio homogeneo con card dashed + CTA.

**Pendientes:**
- Ninguno funcional; solo validacion visual final en navegador.

## 2026-05-09 - Ajuste final formulario de Sedes (campos y boton atras)

**Tarea:** Homogeneizar visual de campos en `/turnos/sedes/nueva/` y agregar boton `Atras`.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/sede_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se estandarizo el bloque de `tramites_habilitados` con labels tipo card, borde y hover, igual al estilo de otros forms.
- Se mantuvieron inputs con clases `form-input` ya existentes en el form backend.
- Se agrego boton `Atras` (history.back) junto a `Cancelar` en acciones del formulario.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Sedes: acciones ver/editar y detalle con solapas

**Tarea:** Agregar acciones con iconos en listado de sedes y crear vista de detalle con solapas.

**Archivos creados:**
- `turnos/interfaces/templates/turnos/backoffice/sede_detalle.html`

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/sedes_lista.html`
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/web/views/backoffice.py`
- `turnos/interfaces/web/urls.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Listado de sedes:
  - se reemplazo accion textual por iconos `ver` (ojo) y `editar` (lapiz).
- Nueva pantalla de detalle de sede:
  - solapas: `Detalles de la sede` y `Tramites`.
  - boton `Atras` y `Editar` en cabecera.
  - en solapa `Tramites` se lista cada tramite habilitado y:
    - si ya tiene agenda activa para esa sede: link `Ir a agenda` (grilla de disponibilidad).
    - si no tiene: `Configurar agenda` (lista de configuraciones filtrada por sede).
- Se agrego ruta nueva:
  - `/turnos/sedes/<pk>/` -> `turnos:sede_detalle`.
- Se agrego filtro por sede en `ConfiguracionListView` cuando llega `?sede=<id>`.

**Pendientes:**
- Ninguno funcional para este alcance.

## 2026-05-09 - Sede editar/crear: selector dual de tramites

**Tarea:** Reemplazar seleccion de tramites por UI de dos cuadros con flechas (habilitados/no habilitados).

**Archivos modificados:**
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/templates/turnos/backoffice/sede_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `SedeTurnoForm`:
  - `tramites_habilitados` ahora usa `SelectMultiple` oculto como campo real del form.
- `sede_form.html`:
  - se agrego UI dual-listbox:
    - izquierda: no habilitados
    - derecha: habilitados
    - botones: `>`, `<`, `>>`, `<<`
  - soporte de doble click para mover items entre listas.
  - sincronizacion al campo real oculto antes de submit.

**Pendientes:**
- Si luego queres drag & drop puro entre columnas, se puede sumar sobre esta base.

## 2026-05-09 - Sede detalle estilo Reclamos

**Tarea:** Ajustar `/turnos/sedes/<id>/?tab=detalle` al estilo visual del detalle de reclamos.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/sede_detalle.html`
- `turnos/interfaces/web/views/configuracion.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se rehizo el detalle de sede con el mismo patron de `reclamo_detail`:
  - cabecera con volver/titulo/subtitulo/accion principal.
  - bloque resumen superior en card.
  - barra de tabs tipo botones (`Detalles`, `Tramites`).
  - paneles por tab con show/hide en frontend (sin recarga).
- Se mejoro el contenido:
  - tab `Detalles`: cards de datos clave de sede.
  - tab `Tramites`: tabla de tramites habilitados + accion agenda.
- Se agrego `pendientes_config` en vista para mostrar resumen de pendientes de agenda.

**Pendientes:**
- Ninguno funcional para este alcance.

## 2026-05-09 - Dual list de tramites con drag & drop real

**Tarea:** Agregar arrastrar y soltar entre columnas en crear/editar sede, manteniendo flechas.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/sede_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reemplazo la UI de selects por listas (`ul/li`) para permitir drag & drop real.
- Se integro `Sortable` (si esta disponible globalmente) con grupo compartido entre columnas.
- Se mantienen botones de flechas (`>`, `<`, `>>`, `<<`) y doble click.
- Se conserva sincronizacion al campo real oculto `tramites_habilitados` al enviar el form.

**Pendientes:**
- Ninguno funcional; validar UX final de seleccion multiple por click en navegador.

## 2026-05-09 - Unificacion de tabs estilo Programas

**Tarea:** Replicar estilo de tabs de `legajos/programas/<id>/` en pantallas de reclamos, tramites y sede.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_detail.html`
- `configuracion/interfaces/templates/configuracion/tramite_detail.html`
- `turnos/interfaces/templates/turnos/backoffice/sede_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reemplazo barra de tabs tipo pills por barra estilo Programas:
  - contenedor con `border-b`
  - tabs horizontales `overflow-x-auto`
  - estado activo por `border-b-2 border-blue-500 text-blue-600`
  - inactivos `border-transparent text-gray-500` + hover.
- Se ajusto JS de activacion en las 3 pantallas para alternar clases del nuevo patron.
- Se mantuvo la logica actual de paneles (`tab-panel`) y tab inicial por validaciones.

**Pendientes:**
- Ninguno funcional.

## 2026-05-09 - Listados estilo Programas

**Tarea:** Replicar estilo visual de listados de `legajos/programas` en listados de Turnos.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/sedes_lista.html`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Ambos listados pasaron de tabla a grilla de cards estilo Programas:
  - header con tipografia y espaciado equivalente.
  - cards con icono, titulo, subtitulo, metricas y CTA.
  - hover con elevacion (`hover:shadow-lg`).
- `Sedes`:
  - cards con estado, direccion, telefono y cantidad de tramites.
  - acciones directas `Ver detalle` y `Editar`.
- `Configuraciones de Turnos`:
  - cards con sede, estado, cantidad de franjas, pendientes y modo.
  - acciones `Disponibilidad`, `Editar` y `Agenda`.
- estados vacios tambien quedaron homologados a ese estilo.

**Pendientes:**
- Si queres, en siguiente paso replico este mismo patron en los listados de reclamos/tramites de configuracion.

## 2026-05-09 - Listados de Reclamos y Tramites estilo Programas

**Tarea:** Replicar formato de listados tipo Programas en `reclamo_list` y `tramite_list`.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/reclamo_list.html`
- `configuracion/interfaces/templates/configuracion/tramite_list.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se migraron ambos listados de tabla a grilla de cards con estilo visual equivalente a Programas.
- Se mantuvieron filtros superiores (busqueda, area, estado, prioridad).
- Se mantuvo paginacion y conservacion de query params.
- Cada card muestra:
  - numero
  - titulo
  - estado
  - area
  - prioridad
  - fecha (ingreso/inicio)
  - CTA `Ver detalle`.
- Se mantuvieron estados vacios con CTA de alta.

**Pendientes:**
- Ninguno funcional.

## 2026-05-09 - Menu: mover Sedes debajo de Localidades

**Tarea:** Reubicar el boton `Sedes` en el sidebar de Configuracion debajo de `Localidades`.

**Archivos modificados:**
- `templates/includes/sidebar/opciones.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego `Sedes` inmediatamente despues de `Localidades`.
- Se removio `Sedes` del bloque donde estaba junto a `Agenda`.
- Se mantuvo condicion de modulo activo (`turnos_active`) y estilos de item activo/inactivo.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Boton Turnos directo desde detalle de tipo de tramite

**Tarea:** Evitar que el boton `Turnos` vaya al listado general y llevarlo directo a crear/editar agenda del tramite.

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html`
- `turnos/interfaces/web/views/configuracion.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En detalle de tipo de tramite:
  - si el tramite ya tiene configuracion de agenda: `Turnos` ahora va a `turnos:configuracion_editar` de esa agenda.
  - si no tiene configuracion: `Turnos` va a `turnos:configuracion_crear?tipo_tramite=<id>`.
  - tambien se ajusto el link inline `Configurar agenda` con el mismo comportamiento directo.
- En `ConfiguracionCreateView` de turnos:
  - se agrego `get_initial()` para leer `?tipo_tramite=` y precargar:
    - `tipo_tramite`
    - `nombre`
    - `area_principal` / `subarea` segun el area del tramite.

**Pendientes:**
- Ninguno para este flujo.

## 2026-05-09 - Edicion de agenda: ocultar selector de tramite

**Tarea:** En `/turnos/configuraciones/<id>/editar/`, no mostrar selector de tramite y dejarlo fijo.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Si existe `config` y tiene `tipo_tramite`:
  - se oculta el select.
  - se muestra el tramite como campo solo lectura visual.
  - se mantiene hidden input con `tipo_tramite` para persistencia en submit.
- Se ajusto JS del formulario para no depender del select de tramite cuando no existe (caso edicion).

**Pendientes:**
- Ninguno.

## 2026-05-09 - Borrar agenda desde Editar (con modal)

**Tarea:** Agregar boton `Borrar` en editar agenda y eliminar tambien horarios de esa agenda.

**Archivos modificados:**
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/web/views/backoffice.py`
- `turnos/interfaces/web/urls.py`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Nueva ruta/vista POST:
  - `turnos:configuracion_eliminar` (`/turnos/configuraciones/<pk>/eliminar/`).
- En pantalla de editar agenda:
  - se agrego boton `Borrar`.
  - confirmacion modal (`Swal`) con fallback `confirm()`.
  - al confirmar, envia formulario POST a `configuracion_eliminar`.
- Comportamiento de borrado:
  - se elimina la configuracion completa.
  - por cascada, se eliminan tambien todas las disponibilidades/horarios asociados.

**Pendientes:**
- Ninguno funcional.

## 2026-05-09 - Regla de borrado de agendas con turnos

**Tarea:** Definir comportamiento al borrar agenda cuando hay turnos asociados.

**Archivos modificados:**
- `turnos/interfaces/web/views/configuracion.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En `configuracion_eliminar`:
  - si hay turnos futuros `PENDIENTE/CONFIRMADO`: bloquea borrado y muestra error.
  - si no hay futuros pero hay historial de turnos: baja logica (`config.activo=False`, disponibilidades inactivas y recurso inactivo) para conservar trazabilidad.
  - si no hay turnos asociados: elimina fisicamente la configuracion (y horarios por cascada).

**Pendientes:**
- Si queres, se puede mostrar este criterio tambien en el texto del modal previo para anticipar el resultado.

## 2026-05-09 - Baja logica de agenda con turnos futuros

**Tarea:** Ajustar comportamiento de borrar/inactivar agenda cuando hay turnos pendientes o futuros.

**Archivos modificados:**
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `configuracion_eliminar` ahora hace siempre baja logica (no borrado fisico):
  - `config.activo = False`
  - recurso de turnos asociado `activo = False`
- Si hay turnos futuros pendientes/confirmados:
  - se informa que esos turnos siguen su curso.
  - no se otorgaran nuevos turnos hasta reactivar.
- Si no hay turnos futuros:
  - queda dada de baja logica conservando historial.
- En edicion de configuracion:
  - al guardar, se sincroniza `recurso.activo` con `config.activo` (reactivar/inactivar desde checkbox).
- Se actualizo modal del boton borrar para reflejar este criterio ("dar de baja").

**Pendientes:**
- Ninguno funcional.

## 2026-05-09 - Sede editar: tab Tramites con estado de agenda y accesos directos

**Tarea:** En `/turnos/sedes/<id>/editar/`, mostrar gestion de tramites en solapa y acceso directo a crear/editar agenda por tramite.

**Archivos modificados:**
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/templates/turnos/backoffice/sede_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `SedeTurnoUpdateView`:
  - agrega contexto `tramites_agenda` por cada tramite habilitado:
    - si tiene agenda (`config_id`)
    - si la agenda esta activa/inactiva.
  - luego de guardar, redirige al mismo editar sede para continuar gestionando.
- `ConfiguracionCreateView.get_initial`:
  - ahora toma `?sede=<id>` ademas de `?tipo_tramite=<id>` para precargar creacion de agenda desde sede.
- `sede_form.html`:
  - en edicion agrega tabs estilo sistema: `Datos de sede` y `Tramites`.
  - en tab `Tramites` mantiene selector dual para pasar tramites a la sede.
  - agrega tabla "Agenda por tramite" con:
    - estado (sin agenda / agenda inactiva / agenda activa)
    - accion directa `Crear agenda` o `Editar agenda`.

**Pendientes:**
- Ninguno funcional.

## 2026-05-09 - Diagnostico filtrado de tramites en alta de agenda

**Tarea:** Revisar por que en /turnos/configuraciones/nueva/ no aparecen opciones de tramite al elegir area/subarea.

**Archivos creados:**
- Ninguno.

**Archivos modificados:**
- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se inspecciono 	urnos/interfaces/web/forms/__init__.py y 	urnos/interfaces/templates/turnos/backoffice/configuracion_form.html.
- Se verifico que el listado de 	ipo_tramite se filtra por: ctivo=True, coincidencia area/subarea, y pertenencia del tramite a la sede seleccionada (data-sedes + validacion en clean).
- No se aplicaron cambios de codigo funcionales en esta iteracion.

**Decisiones o supuestos:**
- La causa mas probable es de configuracion de datos (tramite no habilitado en la sede seleccionada o tramite/area inactivos), no un error de renderizado del select.

**Pendientes:**
- Si el problema persiste con tramite habilitado en sede y ctivo, capturar IDs concretos (sede/area/subarea/tramite) para ajustar el filtro JS con un caso reproducible.


## 2026-05-09 - Doble camino sede/tramite para crear agendas

**Tarea:** Permitir ambos flujos: (1) habilitar tramite desde Sede y luego crear agenda, y (2) crear agenda desde Configuracion eligiendo tramite aunque no este habilitado aun, agregandolo automaticamente a la sede.

**Archivos creados:**
- Ninguno.

**Archivos modificados:**
- 	urnos/interfaces/web/forms/__init__.py`n- 	urnos/interfaces/templates/turnos/backoffice/configuracion_form.html`n- 	urnos/interfaces/web/views/configuracion.py`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se elimino la validacion que bloqueaba seleccionar un tramite si no estaba previamente en sede.tramites_habilitados.
- En el formulario de alta de configuracion se removio el filtro JS por sede en el select de tramites; ahora filtra solo por area/subarea.
- En ConfiguracionCreateView.form_valid y ConfiguracionUpdateView.form_valid, al guardar con sede+tramite se agrega automaticamente el tramite a la sede (sede.tramites_habilitados.add(tipo_tramite)).
- Se mantiene el flujo desde Sede: en la tabla Agenda por tramite sigue disponible Crear agenda o Editar agenda por tramite habilitado.

**Decisiones o supuestos:**
- Se priorizo UX operativa: la sede ya no bloquea la seleccion del tramite al crear agenda; la consistencia se garantiza al guardar por alta/actualizacion automatica de la relacion sede-tramite.

**Pendientes:**
- Ninguno tecnico inmediato; validar manualmente en UI ambos caminos.


## 2026-05-09 - Ajuste visual grilla de disponibilidad (sin superposicion)

**Tarea:** Corregir visualizacion de franjas en /turnos/configuraciones/<id>/disponibilidad/ para que se repartan bien y no se superpongan.

**Archivos creados:**
- Ninguno.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- En _enriquecer_franjas, height_px ahora respeta duracion real en minutos (max(1, fin-inicio)), eliminando el forzado a 44px que producia pisado visual.
- En template de grilla se removio min-height:22px de cada bloque horario para evitar crecimiento artificial.
- Se ajusto el umbral de detalle secundario a height_px >= 36 para no saturar franjas cortas.

**Decisiones o supuestos:**
- Se prioriza fidelidad temporal (1 min = 1 px) sobre altura minima visual para prevenir superposiciones entre franjas contiguas o cortas.

**Pendientes:**
- Validacion manual en UI con franjas de distinta duracion y contiguas.


## 2026-05-09 - Grilla disponibilidad: restaurar tamano y evitar solapado visual

**Tarea:** Mantener tamanos/datos originales de las cajas y evitar superposicion separandolas verticalmente.

**Archivos creados:**
- Ninguno.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se restauro la altura original de franja (height_px = max(44, duracion_real)).
- Se restauro en template min-height:22px y regla de detalle secundario para height_px >= 44.
- Se agrego separacion visual por dia con helper _separar_franjas_vertical (gap de 4px) para evitar superposiciones entre cajas.
- Se ajusta grilla_height al maximo fondo renderizado para que no se corten cajas desplazadas.

**Pendientes:**
- Validacion visual manual en /turnos/configuraciones/2/disponibilidad/ con refresco completo.


## 2026-05-09 - Fix NameError en disponibilidad grilla

**Tarea:** Resolver NameError: _separar_franjas_vertical en /turnos/configuraciones/2/disponibilidad/.

**Archivos modificados:**
- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se verifico que 	urnos/interfaces/web/views/configuracion.py contiene def _separar_franjas_vertical(...) antes de DisponibilidadGrillaView.
- Se reinicio contenedor pp (docker compose restart app) para forzar recarga de codigo en Django.

**Pendientes:**
- Confirmar en navegador que la URL ya carga sin NameError.


## 2026-05-09 - Unificacion de look & feel en configuracion de agendas

**Tarea:** Alinear vistas de configuracion de turnos con el estilo visual de referencia (legajos/programas/2).

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`n- 	urnos/interfaces/templates/turnos/backoffice/sedes_lista.html`n- 	urnos/interfaces/templates/turnos/backoffice/configuracion_form.html`n- 	urnos/interfaces/templates/turnos/backoffice/sede_form.html`n- 	urnos/interfaces/templates/turnos/backoffice/sede_detalle.html`n- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_form.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Unificacion de cards y contenedores a ounded-2xl, order-[#E5E7EB], shadow-sm.
- Unificacion de paleta tipografica principal/secundaria a #252F40, #4A5565, #8C8C8C.
- Unificacion de tablas/tabs con g-[#F9FAFB] y divisores #E5E7EB en vistas de sede, configuracion y disponibilidad.
- Se mantuvo intacta la logica funcional (formularios, filtros, acciones, JS de negocio).

**Pendientes:**
- Validacion visual manual en cada pantalla para microajustes de contraste/espaciado segun preferencia.


## 2026-05-09 - Filtros en listado de configuraciones de turnos

**Tarea:** Agregar filtros por sede, area, subarea y tramite en /turnos/configuraciones/.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- 	urnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Backend: se agregaron filtros GET combinables sobre ConfiguracionListView:
  - sede -> sede_id`n  - rea -> 	ipo_tramite__area__parent_id`n  - subarea -> 	ipo_tramite__area_id`n  - 	ramite -> 	ipo_tramite_id`n- Contexto: se envian opciones para selects (sedes, reas, subareas, 	ramites) y estado actual (iltros).
- Frontend: se agrego barra de filtros con boton Filtrar y Limpiar.
- Frontend: filtros encadenados en cliente (area -> subarea -> tramite) para evitar combinaciones inconsistentes visualmente.

**Pendientes:**
- Validacion manual en UI con combinaciones de filtros y resultados vacios.


## 2026-05-09 - Ajuste grilla disponibilidad: correspondencia exacta con eje horario

**Tarea:** Corregir desalineacion entre horarios del eje izquierdo y cards en /turnos/configuraciones/2/disponibilidad/.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se elimino el desplazamiento vertical artificial de franjas (helper _separar_franjas_vertical y su uso).
- Se restauro grilla_height al alto temporal real de la grilla.
- Resultado: cada card vuelve a posicionarse estrictamente por su hora (	op_px) y coincide con la escala del eje horario.

**Pendientes:**
- Validacion visual en navegador con refresh completo.


## 2026-05-09 - Correccion de fin de franja en grilla horaria

**Tarea:** Ajustar cards para que no se superpongan al horario siguiente por el extremo inferior.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se agrego ox-sizing:border-box al estilo inline de cada card de disponibilidad.
- Con esto, height pasa a incluir borde y padding, alineando correctamente el final de cada franja con el eje horario.

**Pendientes:**
- Verificacion visual en navegador (hard refresh) para confirmar que ya no pisa la siguiente linea horaria.


## 2026-05-09 - Disponibilidad: look & feel + contexto de tramite/sede/area

**Tarea:** Mejorar pantalla de disponibilidad para alinearla visualmente con el resto y mostrar mejor contexto de agenda.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se reemplazo el encabezado plano por header-card (ounded-2xl, borde, sombra suave, fondo gradiente) consistente con la linea visual del sistema.
- Se muestra de forma destacada: Tramite y Sede en la cabecera.
- Se agrego Area/Subarea en texto secundario pequeño para contexto.
- Se mantuvo intacta la logica de la grilla horaria.

**Pendientes:**
- Validacion visual final en navegador para ajustar contraste/tamanos si hiciera falta.


## 2026-05-09 - Fix UnicodeDecodeError en disponibilidad

**Tarea:** Resolver error UTF-8 en /turnos/configuraciones/2/disponibilidad/.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se detecto y corrigio codificacion invalida en el template (byte CP1252 conflictivo).
- Se reescribio el archivo completo en UTF-8 y se reemplazo el separador problematico por - para evitar nuevos errores de decode.

**Pendientes:**
- Refrescar la vista y confirmar carga correcta.


## 2026-05-09 - Disponibilidad: header estilo programa_detail + saneo UTF-8

**Tarea:** Aplicar look & feel avanzado (icono, badges/metrica en cards) en disponibilidad y evitar problemas de codificacion.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se reconstruyo el template completo en UTF-8 para eliminar mojibake y errores de decode.
- Nuevo header-card con icono principal, breadcrumb, tramite+sede destacados y area/subarea en texto secundario.
- Se agrego bloque de metricas chicas en cards (modo, aprobacion, anticipacion minima/maxima), en linea con programa_detail.
- Se preservo la logica de grilla horaria y alineacion temporal de bloques.

**Pendientes:**
- Validacion visual final en navegador.


## 2026-05-09 - Reestilo disponibilidad grilla al look de sede detalle

**Tarea:** Hacer disponibilidad_grilla con look & feel de /turnos/sedes/1/.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se reemplazo estructura visual por el mismo patron de sede_detalle: header con volver+titulo, card de detalle, card de contenido principal y bordes/sombras consistentes.
- Se mantuvo la grilla horaria y su logica de posicionamiento tal como estaba funcionando.
- Se conservaron datos de tramite, sede, area/subarea y metricas operativas en bloques compactos.

**Pendientes:**
- Validar visualmente en navegador y ajustar microespaciados si hiciera falta.


## 2026-05-09 - Remover altura minima 44px en cards de disponibilidad

**Tarea:** Quitar forzado de height 44 en cards de horarios dentro de la grilla.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- En _enriquecer_franjas, se cambio height_px de max(44, duracion) a max(1, duracion) para que cada card use altura real segun minutos.

**Pendientes:**
- Validar en UI que la legibilidad de franjas cortas siga siendo aceptable.


## 2026-05-09 - Badge de estado en disponibilidad igual a sede_detalle

**Tarea:** Unificar estilo/ubicacion de estado Activa/Inactiva en disponibilidad grilla.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se agrego bloque Estado en card de detalle de agenda.
- Badge Activa/Inactiva usa el mismo estilo de sede_detalle (clases y colores consistentes).


## 2026-05-09 - Slots visibles siempre en grilla de disponibilidad

**Tarea:** Recuperar visualizacion de cantidad de slots tras quitar altura minima de 44px.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se elimino la condicion height_px >= 44 para el texto secundario.
- Ahora duracion + slots se muestra siempre, en formato compacto (	runcate) para franjas bajas.

**Nota:**
- Si varias franjas tienen igual duracion (ej. todas de 30 min), su altura sera igual por definicion temporal.


## 2026-05-09 - Reversion de altura minima en cards de disponibilidad

**Tarea:** Volver al comportamiento previo a quitar height 44 en la grilla.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se restauro d.height_px = max(44, duracion_real) en backend.
- Se restauro condicion visual para mostrar texto secundario solo cuando disp.height_px >= 44.


## 2026-05-09 - Plus de agregar franja mas visible en grilla

**Tarea:** Hacer mas llamativo el boton + por dia en disponibilidad.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se aumento tamaño del boton (w-7 h-7) y del icono (11px).
- Se aplico fondo/borde indigo, sombra y hover fuerte (indigo solido con icono blanco).
- Se agrego 	itle de ayuda: Agregar franja.


## 2026-05-09 - disponibilidad_form alineado al look de disponibilidad_grilla

**Tarea:** Igualar look & feel de /turnos/configuraciones/<id>/disponibilidad/agregar/ con la pagina de grilla.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_form.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se reestilizo la pantalla con el mismo patron visual: header, card de detalle de agenda y card principal de formulario.
- Se mantuvo la logica del formulario y preview de slots/rango.
- Se corrigio la funcion JS disponibilidadForm() para que retorne un objeto valido (eturn {...}) y funcione correctamente con Alpine.
- Se separo el form de eliminacion fuera del formulario principal para evitar anidamiento invalido de forms.


## 2026-05-09 - Disponibilidad grilla: boton general + listado de franjas creadas

**Tarea:** Agregar un acceso general para crear franjas sin dia preseleccionado y mostrar las franjas ya creadas.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se agrego boton superior Agregar franja (ruta sin ?dia=...) para alta general.
- Se agrego bloque Franjas creadas debajo de la grilla con links directos para editar cada franja.
- Si no existen franjas, se muestra mensaje informativo.


## 2026-05-09 - Aviso por superposicion de franjas (sin bloqueo)

**Tarea:** Permitir superposicion de franjas pero mostrar cartel de advertencia al guardar.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se agrego helper _hay_solapamiento(...) para detectar cruces de horarios por configuracion y dia.
- En alta de disponibilidad: si una franja nueva se cruza con otra existente, se crea igual y se muestra messages.warning.
- En edicion de franja: si el rango actualizado se cruza con otra franja del mismo dia, se guarda igual y se muestra messages.warning.
- Se mantiene la validacion previa de hora_inicio duplicada exacta (comportamiento existente), y no se bloquea por solape.


## 2026-05-09 - sede_editar alineado visualmente a sede_detalle

**Tarea:** Hacer que /turnos/sedes/<id>/editar/ tenga el mismo look & feel que /turnos/sedes/<id>/.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/sede_form.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se cambio estructura superior al patron de sede_detalle: header con Volver al listado, titulo grande y subtitulo contextual.
- Se agrego badge de estado Activa/Inactiva en cabecera de edicion.
- Se agrego card Detalle de la sede previa al formulario con resumen (nombre, direccion, telefono, tramites habilitados).
- Se mantuvo logica de formulario, tabs y acciones sin cambios funcionales.


## 2026-05-09 - sede_editar: fix tab tramites vacia + tramites con agenda

**Tarea:** Corregir en /turnos/sedes/<id>/editar/ que no aparecia el listado para habilitar tramites y faltaban tramites ya usados en agenda.

**Archivos modificados:**
- 	urnos/interfaces/web/forms/__init__.py`n- 	urnos/interfaces/templates/turnos/backoffice/sede_form.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- JS: se separo la inicializacion de tabs del bloque de lista dual para que la tab Tramites funcione siempre, aun si falla la inicializacion del selector dual.
- Form: SedeTurnoForm ahora incluye en 	ramites_habilitados no solo tramites activos, sino tambien tramites ya habilitados o vinculados por agenda en esa sede (aunque esten inactivos), evitando que desaparezcan del editor.


## 2026-05-09 - Sede: mostrar tramites vinculados por agenda aunque no esten en M2M

**Tarea:** Corregir que no aparecian tramites con agenda creada (ej. Renovacion Licencia Conducir) cuando 	ramites_habilitados estaba vacio.

**Archivos modificados:**
- 	urnos/interfaces/web/views/configuracion.py`n- 	urnos/interfaces/web/forms/__init__.py`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- SedeTurnoUpdateView y SedeTurnoDetailView: el listado de tramites ahora usa union de:
  - tramites habilitados en sede (M2M)
  - tramites presentes en configuraciones de agenda de esa sede.
- SedeTurnoForm: en edicion, el queryset incluye esos tramites y se precargan como seleccionados en 	ramites_habilitados para que aparezcan en la columna de habilitados.

**Resultado esperado:**
- En /turnos/sedes/1/ y /turnos/sedes/1/editar/ debe aparecer Renovacion Licencia Conducir aunque antes no estuviera en M2M.


## 2026-05-09 - Fix lista dual de tramites vacia en sede_editar

**Tarea:** Corregir que en tab Tramites los boxes aparecian vacios pese a tener queryset.

**Archivos modificados:**
- 	urnos/interfaces/web/forms/__init__.py`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se detecto que el select oculto (id_tramites_habilitados_real) se renderizaba sin <option> aunque el queryset tenia datos.
- Se forzo el enlace de opciones al widget: widget.choices = field.choices.
- Verificacion en shell: ahora el HTML del select incluye opciones y Renovacion Licencia Conducir seleccionado.


## 2026-05-09 - Quitar card redundante de franjas creadas

**Tarea:** Eliminar bloque Franjas creadas de disponibilidad grilla por redundancia con la grilla principal.

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Se removio card completa Franjas creadas y su mensaje de vacio.
- Se mantiene solo la grilla horaria como fuente principal de visualizacion/edicion.


## 2026-05-09 - Portal home: flujo de Iniciar tramite

**Tarea:** Cambiar CTA Iniciar tramite para ir primero al listado de tramites y no al login directo.

**Archivos modificados:**
- portal/interfaces/templates/portal/home.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- CTA Iniciar tramite ahora apunta a 	ramites:lista_tramites (listado publico).
- Se restauraron enlaces de Instituciones/Registrar institucion a portal:crear_usuario para no afectar ese flujo.


## 2026-05-09 - portal_ciudadano home: iniciar tramites sin login previo

**Tarea:** En /portal-ciudadano/, que Iniciá/Iniciar trámite lleve al listado de trámites antes del login.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/home.html`n- docs/tmp/WORKLOG.md`n
**Cambios realizados:**
- Quick card Iniciá trámites: se removió redirección condicional a login; ahora apunta directo a portal_ciudadano:tramites.
- Botón Iniciar trámite del bloque inferior: ahora también apunta directo a portal_ciudadano:tramites.

## 2026-05-09 - Portal Ciudadano: iniciar tramite por sede o por fecha

**Tarea:** Cambiar el flujo de inicio de tramites para que primero permita elegir modalidad (`por sede` o `por fecha`) y desde ahi continuar con la seleccion de turno.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/urls.py`
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `portal_ciudadano/templates/portal_ciudadano/turnos_solicitar.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego endpoint `portal_ciudadano:turnos_disponibles_por_fecha` para consultar slots disponibles por fecha entre todos los recursos/sedes activas.
- `portal_ciudadano_solicitar_turno` ahora soporta `modo=sede` y `modo=fecha`.
- En `modo=sede` se mantiene el camino de elegir sede/recurso y luego ver su agenda.
- En `modo=fecha` se muestra selector de fecha y listado dinamico de horarios disponibles por sede/recurso, con acceso directo a confirmar turno.
- `portal_ciudadano_turno_slots` y `portal_ciudadano_turno_calendario` permiten consulta publica de disponibilidad (sin exigir login), dejando autenticacion para la confirmacion final.
- En `tramites.html` se agregaron dos cards iniciales para elegir `por sede` o `por fecha`.

**Decisiones o supuestos:**
- Se mantiene la pantalla de tipos de tramite existente y se agrega la nueva decision de modalidad como primer paso visible.
- La reserva/confirmacion del turno sigue protegida por login ciudadano.

**Pendientes:**
- Validacion funcional en navegador del flujo completo anonimo -> eleccion -> login en confirmacion (si corresponde).
- Si se quiere ocultar completamente la seccion de tipos de tramite, requiere ajuste adicional en `tramites.html`.
## 2026-05-09 - Ajuste flujo: fecha/sede solo dentro de detalle de tramite

**Tarea:** Quitar la eleccion `por sede / por fecha` de `/portal-ciudadano/tramites/` y dejarla solo dentro del flujo interno del tramite.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se removieron de `tramites.html` las cards y estilos de `Elegir por sede` y `Elegir por fecha`.
- En `tramites_detalle.html`, dentro del bloque `Este tramite requiere turno previo`, se agregaron dos acciones:
  - `Elegir por sede` (usa la sede seleccionada y abre su agenda)
  - `Elegir por fecha` (abre la busqueda general por fecha)
- Se ajusto el JS para apuntar el boton `Elegir por sede` al recurso correcto segun la sede seleccionada.

**Pendientes:**
- Validar visualmente en navegador el flujo de ambos botones dentro de `tramites/detalle`.
## 2026-05-09 - Tramite detalle solo con 2 cards de modalidad

**Tarea:** En `/portal-ciudadano/tramites/detalle/?tipo=...` mostrar solo 2 cards grandes arriba (por sede / por fecha) y eliminar cualquier otro formulario.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se elimino del detalle todo el formulario de carga y campos dinamicos.
- Se reemplazo por dos cards grandes:
  - `Ir por sede`
  - `Ir por fecha`
- Se ajusto el script para que `Ir por sede` abra directamente el calendario del primer recurso configurado para el tramite (o fallback a modo sede si no hay agenda).

**Pendientes:**
- Si se requiere mantener info de area/subarea/tramite en esta pantalla, agregarlo sin reintroducir formulario.
## 2026-05-09 - Quitar agenda relacionada unica en editar tipo de tramite

**Tarea:** En `/configuracion/tramites/configuracion/<id>/editar/` eliminar la referencia a agenda relacionada unica porque un tramite puede tener multiples agendas.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/forms/tramites.py`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se removio `recurso_turnos` del `TipoTramiteConfigForm`.
- Se removio su validacion obligatoria cuando `requiere_turno=True`.
- Se elimino del template el bloque "Agenda de turnos asociada" en la pantalla de editar/crear tipo de tramite.

**Pendientes:**
- Si se desea, en detalle de tipo de tramite tambien se puede quitar/ajustar cualquier texto de agenda unica.
## 2026-05-09 - Detalle tipo tramite con look&feel de detalle reclamo + tabs en listas

**Tarea:** Ajustar `/configuracion/tramites/configuracion/<id>/` al look&feel de `/configuracion/reclamos/listado/<id>/` y mostrar tabs con sedes/agendas en formato lista.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/web/views/tramites.py`
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se homologo el detalle de tipo de tramite al mismo estilo base del detalle de reclamo (header, card de datos, estructura visual).
- Se eliminaron referencias de agenda unica en el detalle.
- Se agregaron tabs:
  - `Sedes`: lista de sedes asociadas/habilitadas para el tramite.
  - `Agendas`: lista de configuraciones/agendas del tramite con accesos a editar y disponibilidad.
  - `Campos dinamicos`: lista de campos extra.
- Se agrego en la vista el contexto `sedes_turno` y `agendas_turno` para alimentar esas listas.

**Pendientes:**
- Validar visualmente con datos reales que los nombres/links de sedes y agendas se muestren como esperado.
## 2026-05-09 - Configuraciones de turnos en formato lista

**Tarea:** Cambiar `/turnos/configuraciones/` de cards a formato lista para soportar volumen alto.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reemplazo la grilla de cards por una tabla/lista responsiva con columnas:
  - Configuracion
  - Sede
  - Tramite
  - Estado
  - Franjas
  - Pendientes
  - Modo
  - Acciones
- Se mantuvieron filtros y acciones existentes (`Disponibilidad`, `Editar`, `Agenda`).

**Pendientes:**
- Si se requiere, agregar paginacion real del lado servidor para listas muy grandes.
## 2026-05-09 - Card de detalle de tramite antes de opciones por sede/fecha

**Tarea:** En `/portal-ciudadano/tramites/detalle/?tipo=...` mostrar una card con detalles del tramite seleccionado antes de las 2 cards de modalidad.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego una card superior con resumen del tramite:
  - Nombre del tramite
  - Area
  - Subarea
  - Descripcion
- Esta card aparece inmediatamente antes de las cards `Elegir por sede` y `Elegir por fecha`.

**Pendientes:**
- Si se desea, agregar badges visuales (requiere turno, online/presencial) en esa misma card.
## 2026-05-09 - Todo en tabs en detalle de tipo de tramite

**Tarea:** En `/configuracion/tramites/configuracion/<id>/` mostrar todo en tabs (datos, sedes y agendas).

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se movio `Datos principales` dentro de una tab `Datos`.
- Se mantuvieron y ordenaron tabs: `Datos`, `Sedes`, `Agendas`, `Campos dinamicos`.
- La pantalla queda unificada en un solo bloque tabulado.

**Pendientes:**
- Ninguno.
## 2026-05-09 - Tramite detalle dinamico en una sola pantalla + stepper ajustado

**Tarea:** En `/portal-ciudadano/tramites/detalle/?tipo=...` permitir seleccionar modalidad y disponibilidad dinamicamente en la misma pantalla, y ajustar el stepper.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reemplazaron los links de salida por flujo dinamico en la misma pantalla:
  - `Ir por sede` abre panel con sede + fecha y muestra horarios disponibles.
  - `Ir por fecha` abre panel con fecha y muestra sedes/horarios disponibles.
- Los horarios se cargan por fetch y se muestran debajo para seleccionar/continuar a confirmar.
- Se ajusto el stepper a pasos reales: `Tipo > Modalidad > Horario > Confirmar`.

**Pendientes:**
- Ajustar estilo activo del stepper segun interaccion en vivo (opcional).
## 2026-05-09 - Tramites sin descripcion/fecha/adjuntos fijos

**Tarea:** Quitar del flujo de tramites los campos fijos `descripcion`, `fecha_aproximada` y `adjuntos`, dejando modalidad + dinamicos + turno.

**Archivos modificados:**
- `portal_ciudadano/forms.py`
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `TramiteDetalleForm` ya no hereda de `SolicitudDetalleBaseForm` (se eliminaron esos campos del formulario de tramite).
- En `PortalCiudadanoTramiteDetalleView.post` se elimino el manejo de `request.FILES['adjuntos']`, descripcion y fecha aproximada del draft.
- En confirmacion de tramite se ajusto el resumen para no mostrar fecha/adjuntos/descripcion.
- En creacion final de `Tramite` se deja `descripcion` vacia y `detalle_interno` generico desde portal ciudadano.

**Pendientes:**
- Si se necesita adjuntar archivos en tramites, implementarlo via campo dinamico tipo `archivo` con persistencia explicita en backend.
## 2026-05-09 - Campos dinamicos tipo archivo se guardan como adjuntos reales (tramites)

**Tarea:** Implementar que campos dinamicos tipo `archivo` en portal ciudadano se persistan como `TramiteAdjunto` al confirmar tramite.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En `PortalCiudadanoTramiteDetalleView.post`:
  - Se detectan campos dinamicos de tipo `archivo` para el tipo de tramite.
  - Se toman archivos desde `request.FILES` en claves `extra_<campo_id>`.
  - Se guardan temporalmente en storage (`tramites_draft`) y se agregan a `adjuntos_meta` del draft.
  - Se carga en `extras` el nombre del archivo para cumplir validacion dinamica del campo.
- En `PortalCiudadanoTramiteConfirmarView.post`:
  - Se reactivo la persistencia de `adjuntos_meta` a `TramiteAdjunto` real mediante `_persist_adjuntos`.

**Resultado funcional:**
- Un campo dinamico tipo archivo ahora:
  - queda cargado en datos dinamicos (nombre de archivo), y
  - ademas se guarda como adjunto real del tramite al confirmar.

**Pendientes:**
- Si se quiere, mostrar en la UI de confirmacion el listado de archivos dinamicos antes de enviar.
## 2026-05-09 - Tramite detalle con agendita de proximos dias (sin datepicker)

**Tarea:** En `/portal-ciudadano/tramites/detalle/?tipo=...` reemplazar seleccion por datepicker por agenda de proximos dias, tanto para modo sede como modo fecha.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/urls.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agregaron endpoints JSON:
  - `portal_ciudadano:agenda_sede` -> agenda por sede/recurso para proximos dias.
  - `portal_ciudadano:agenda_general` -> agenda general por fecha con sedes y horarios.
- En `tramites_detalle`:
  - Modo `por sede`: se selecciona sede y se lista agenda de proximos dias + horarios.
  - Modo `por fecha`: se lista agenda de proximos dias agrupada por dia y por sede.
  - Se removio el uso de datepicker para ambos caminos.

**Pendientes:**
- Si se requiere, parametrizar cantidad de dias segun configuracion por tramite/sede en lugar de default tecnico.
## 2026-05-09 - Fix agendita portal: soportar DisponibilidadConfiguracion

**Tarea:** Corregir mensaje "No hay horarios disponibles" cuando existe agenda creada en configuraciones nuevas.

**Archivos modificados:**
- `portal/turnos_utils.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `get_slots_disponibles` ahora usa fallback a `turnos.DisponibilidadConfiguracion` cuando el recurso no tiene `DisponibilidadTurnos` legacy y esta vinculado a `configuracion_turnos`.
- `get_calendario_mensual` idem: fallback a dias activos desde `DisponibilidadConfiguracion`.

**Resultado:**
- La agendita del portal muestra horarios para agendas creadas en `/turnos/configuraciones/...`.
## 2026-05-09 - Confirmar turno: solo hora inicio y sin motivo

**Tarea:** En `/portal-ciudadano/turnos/solicitar/<recurso>/confirmar/` mostrar solo hora de inicio y quitar el campo motivo de consulta.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En resumen de turno se muestra `Horario: {{ hora_inicio }}` (sin hora fin visible).
- Se removio del formulario visible el campo `motivo`.
- Se mantienen hidden inputs de fecha/hora inicio/hora fin para no romper la reserva actual del backend.

## 2026-05-09 - Unificar visual de Mis Turnos en Portal Ciudadano

**Tarea:** Hacer que `portal-ciudadano/turnos/` muestre los turnos con el mismo formato de `portal/mi-perfil/turnos/`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se rearmo la seccion de `Mis Turnos` para replicar la estructura visual del portal principal: encabezado, bloque de proximos turnos con tarjeta por turno y bloque de historial compacto.
- En proximos turnos se paso a un layout resumido (fecha corta, sede, franja horaria, direccion y codigo), con badges de estado y accion `Cancelar` solo para estados pendientes/confirmados.
- En historial se simplifico la tarjeta para mostrar fecha, sede, hora/codigo y estado con etiquetas equivalentes al flujo de `mi-perfil/turnos`.
- No se tocaron vistas, rutas ni logica de negocio; se reutilizo el contexto existente (`turnos_proximos`, `turnos_historial`).

**Decisiones o supuestos:**
- Se mantuvo `base_seccion.html` de `portal_ciudadano` y se adapto solo el contenido interno para evitar cambios colaterales en otras pantallas.

**Pendientes:**
- Validacion visual en navegador en `http://localhost:8000/portal-ciudadano/turnos/` para confirmar que el resultado coincide con el esperado.

## 2026-05-09 - Mis Turnos: mostrar solo sede, agenda y hora de inicio

**Tarea:** En `portal-ciudadano/turnos/`, mostrar por turno solo sede, agenda y horario de inicio.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se simplifico el contenido de cada tarjeta (proximos e historial) para mostrar unicamente:
  - `Sede`: `turno.recurso.nombre`
  - `Agenda`: `Agenda <tipo_tramite> - <sede>`
  - `Horario`: solo `hora_inicio`
- Se removieron direccion, codigo de turno, fecha destacada y hora fin del bloque principal de datos.

**Pendientes:**
- Validar en navegador con el caso de `Sede 2` para confirmar salida exacta esperada.

## 2026-05-09 - Mis Turnos: quitar prefijo Agenda duplicado y agregar codigo

**Tarea:** Ajustar salida de turnos para no repetir `Agenda ... - Sede ...`, mostrar solo sede, tramite, codigo y horario de inicio.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se elimino el texto compuesto `Agenda <tramite> - <sede>`.
- Se dejo la segunda linea solo con el nombre del tramite.
- Se agrego linea `Codigo: <codigo_turno>`.
- Se mantuvo `Horario: <hora_inicio>` sin hora fin.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Mis Turnos: usar nombre/direccion de sede real

**Tarea:** Corregir que se mostraba nombre de agenda en lugar de nombre de sede.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se cambio el campo principal para mostrar `configuracion_turnos.sede.nombre` cuando existe.
- Se agrego linea de direccion de sede usando `configuracion_turnos.sede.direccion` (con fallback).
- Se mantuvieron las lineas: nombre de tramite, codigo y horario (solo hora inicio).

**Pendientes:**
- Ninguno.

## 2026-05-09 - Mis Turnos: reponer badge de fecha con dia abreviado

**Tarea:** Volver a mostrar cuadrado de fecha en tarjetas de turnos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego badge cuadrado a la izquierda con:
  - dia del mes en numero grande
  - dia de semana abreviado en mayusculas (`LUN`, `MAR`, `MIE`, `JUE`, `VIE`, `SAB`, `DOM`)
- Se aplico tanto en `Proximos turnos` como en `Historial`.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Mis Turnos: agregar solapas proximos/pasados

**Tarea:** Separar la pantalla de turnos en dos solapas: Proximos turnos y Turnos pasados.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/turnos.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agregaron dos botones de solapa en la card principal.
- Se envolvieron los listados en paneles 	ab-proximos y 	ab-pasados.
- Se agrego JS simple (mostrarTabTurnos) para alternar visibilidad y estilo de boton activo.
- Se agrego estado vacio para Turnos pasados cuando no hay historial.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Mis Turnos: quitar botones de solicitar turno

**Tarea:** Remover CTA de solicitud de turno en la pantalla de mis turnos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/turnos.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino el boton Solicitar nuevo turno del encabezado.
- Se elimino el boton Solicitar un turno del estado vacio de proximos.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix visual en alta de sede: campos ocultos

**Tarea:** Corregir visual de /turnos/sedes/nueva/ donde no se veian los campos del formulario.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/sede_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se ajustaron clases de los bloques 	ab-datos y 	ab-tramites para que solo usen 	ab-panel cuando es edicion (object.pk).
- En creacion (nueva sede), ambos bloques quedan visibles y no dependen del sistema de tabs.
- En edicion se mantiene el comportamiento con tabs.

**Pendientes:**
- Validar visualmente en navegador que /turnos/sedes/nueva/ ya renderiza los campos.

## 2026-05-09 - Sede nueva: fix visual de inputs sin borde/sombra

**Tarea:** Homologar estilo visual de campos en /turnos/sedes/nueva/ con otros forms del backoffice.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- 	urnos/interfaces/web/forms/__init__.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En SedeTurnoForm se forzaron clases visuales explicitas para 
ombre, direccion y 	elefono:
  - borde visible
  - fondo blanco
  - padding
  - sombra suave
  - foco con ring/border indigo
- Se mantuvo intacta la logica funcional del formulario.

**Pendientes:**
- Validar visualmente en navegador que los tres campos ya se vean con el mismo formato del resto de formularios.

## 2026-05-09 - Sede nueva: mejorar separacion visual de bloque Tramites habilitados

**Tarea:** Dar mas aire entre datos principales y bloque Tramites habilitados en /turnos/sedes/nueva/.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/sede_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se aumento el espaciado general entre secciones (space-y-8).
- Se agrego margen superior al bloque de tramites en modo alta (mt-6).
- Se incremento el padding superior del bloque con la linea divisoria (pt-6).
- En edicion se mantiene sin margen extra (mt-0) para no alterar el layout por tabs.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Sedes lista: quitar boton Agenda

**Tarea:** Remover el boton Agenda de /turnos/sedes/.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- 	urnos/interfaces/templates/turnos/backoffice/sedes_lista.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino el enlace/boton superior Agenda que apuntaba a 	urnos:configuracion_lista.
- Se mantuvo el boton Nueva sede.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites configuracion: limpieza de reglas fuera de uso

**Tarea:** Quitar de UI reglas sin uso funcional actual en alta/edicion de tipo de tramite.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html
- configuracion/interfaces/web/forms/tramites.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino de bloque Reglas en form de tipo de tramite:
  - Requiere pago
  - Requiere validacion manual
- Se elimino de vista detalle de tipo de tramite la fila Requiere pago.
- Se removio variable no utilizada equiere_turno en TipoTramiteConfigForm.clean().

**Pendientes:**
- Si se decide retirar definitivamente estos flags del dominio, implicaria cambio de modelo/migracion/API (no realizado en este ajuste).

## 2026-05-09 - Agregar campos en creacion de tipos de tramite

**Tarea:** Incorporar en alta/edicion de tipo de tramite los campos Costo, Requisitos e Informacion extra.

**Archivos creados:**
- 	ramites/migrations/0006_tipotramite_costo_requisitos_info_extra.py

**Archivos modificados:**
- 	ramites/models.py
- configuracion/interfaces/web/forms/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agregaron campos al modelo TipoTramite:
  - costo (DecimalField)
  - equisitos (TextField)
  - informacion_extra (TextField)
- Se agregaron al TipoTramiteConfigForm para alta/edicion.
- Se renderizaron en la pantalla de crear/editar (	ramite_tipo_configuracion_form.html).
- Se agregaron al detalle (	ramite_tipo_configuracion_detail.html).
- Se creo migracion  006 para persistencia en BD.

**Pendientes:**
- Ejecutar migracion en entorno (python manage.py migrate) para que los campos queden disponibles en base de datos.

## 2026-05-09 - Fix conflicto E302/E303 por campo requisitos en TipoTramite

**Tarea:** Resolver choque entre campo nuevo de TipoTramite y elated_name='requisitos' de RequisitoTramite.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- 	ramites/models.py
- 	ramites/migrations/0006_tipotramite_costo_requisitos_info_extra.py
- configuracion/interfaces/web/forms/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se renombro el campo nuevo de TipoTramite de equisitos a equisitos_info.
- Se ajusto la migracion  006 para crear equisitos_info.
- Se actualizaron formulario y templates para usar equisitos_info manteniendo etiqueta visible Requisitos.

**Pendientes:**
- Reintentar migraciones del contenedor para confirmar que desaparece el SystemCheckError.

## 2026-05-09 - Tramites configuracion: nuevo paso 3 "Template"

**Tarea:** En alta/edicion de tipo de tramite, definir el punto 3 como Template y ubicar ahi los campos nuevos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se movieron Costo, Requisitos y Informacion extra fuera de Datos principales.
- Se creo nuevo bloque 3. Template con esos tres campos.
- Se renumero Campos extra dinamicos como 4.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites configuracion: mover imagen de portada a bloque Template

**Tarea:** Ubicar Imagen de portada dentro del paso 3 Template.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se removio Imagen de portada de Datos principales.
- Se agrego Imagen de portada en 3. Template, junto a Costo, Requisitos e Informacion extra.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites configuracion: requisitos e informacion extra formateables

**Tarea:** Hacer que Requisitos e Informacion extra sean campos con formato enriquecido.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se inicializo Summernote sobre los textareas equisitos_info e informacion_extra.
- Se uso el editor ya disponible globalmente en el proyecto (sin nuevas dependencias).
- Se configuro toolbar basica (negrita/cursiva/subrayado, listas, link y vista codigo).

**Pendientes:**
- Validar en navegador que Summernote cargue en el entorno actual y que el guardado persista HTML.

## 2026-05-09 - Fix visual: editor formateable no visible en tramite tipo form

**Tarea:** Corregir que Requisitos e Informacion extra no mostraban editor enriquecido.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego CSS de Summernote en bloque head de la vista.
- Se movio la inicializacion del editor a bloque customJS (final de pagina), junto con carga explicita de jquery + summernote.
- Se elimino inicializacion temprana dentro del script principal para evitar ejecutar antes de cargar librerias.

**Pendientes:**
- Hard refresh del navegador para limpiar cache y verificar que ambos campos se rendericen como editor.

## 2026-05-09 - Fallback editor enriquecido para requisitos/info extra

**Tarea:** Garantizar campos formateables aunque Summernote no cargue.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego fallback nativo con contenteditable para Requisitos e Informacion extra.
- Si Summernote carga: usa Summernote.
- Si Summernote no carga: se muestra toolbar basica (negrita/cursiva/subrayado/lista/link) y se sincroniza HTML al textarea al guardar.

**Pendientes:**
- Validar visualmente en navegador que el fallback aparezca correctamente en el entorno actual.

## 2026-05-09 - Tramites form: reducir altura visual de descripciones

**Tarea:** Achicar visualmente los campos de descripcion en alta/edicion de tipo de tramite.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Descripcion principal del tipo de tramite: se renderiza con ows=3.
- Descripcion de cada campo dinamico: se renderiza con ows=2.
- Descripcion del empty form de campos dinamicos (al agregar nuevos): tambien ows=2.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites form: forzar toolbar visible en campos enriquecidos

**Tarea:** Garantizar que se vean herramientas de formato en Requisitos e Informacion extra.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se desactivo el intento de inicializar Summernote en esta vista.
- Se forzo el uso del editor fallback (contenteditable) con toolbar propia siempre.
- Se removio carga JS de jQuery/Summernote en este template para evitar estados mixtos.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites detalle: mover Volver a card y simplificar datos

**Tarea:** En /portal-ciudadano/tramites/detalle/, mover boton Volver al header de la card de detalle y simplificar contenido.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino boton Volver fuera de la card.
- Se agrego boton Volver dentro de la card, alineado a la derecha del titulo.
- Se mantuvo titulo del tramite.
- Se removio Descripcion.
- Se reemplazo Area y Subarea por una sola linea: Area - Subarea.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites detalle: agregar card de requisitos e informacion extra

**Tarea:** En detalle de tramite ciudadano, agregar card debajo del resumen con Requisitos e Informacion extra.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego una segunda card debajo de la card principal.
- La card muestra:
  - Requisitos (desde 	ipo_seleccionado.requisitos_info)
  - Informacion extra (desde 	ipo_seleccionado.informacion_extra)
- Se renderiza contenido con formato (|safe) y mensajes de fallback cuando no hay datos.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites detalle: requisitos/info extra sin card

**Tarea:** Quitar el contenedor tipo card para la seccion de Requisitos e Informacion extra.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se removio clase/estilo de card (extra-card) para esa seccion.
- Se dejo como bloque simple de contenido debajo del resumen del tramite.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites detalle: aumentar separacion vertical de secciones informativas

**Tarea:** Separar mas Requisitos respecto de la card superior y tambien Informacion extra.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se aumento margen superior del bloque informativo (Requisitos) respecto de la card de titulo.
- Se aumento margen entre Requisitos e Informacion extra.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites configuracion editar: ordenar campos nombre luego area/subarea

**Tarea:** En /configuracion/tramites/configuracion/<id>/editar/, mostrar primero Nombre y luego Area/Subarea.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En bloque Datos principales se movio Nombre al inicio.
- Area y Subarea quedaron inmediatamente despues.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites detalle: mas espaciado + bloque Costo

**Tarea:** Aumentar separacion en Requisitos/Informacion extra y agregar Costo debajo.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se incremento aun mas el espaciado vertical entre secciones informativas.
- Se agrego nuevo bloque Costo debajo de Informacion extra.
- Se muestra valor de 	ipo_seleccionado.costo con fallback cuando no hay dato.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites detalle: costo destacado + formato moneda sin centavos

**Tarea:** Destacar visualmente el costo y mostrarlo como $ 34.000 (sin centavos).

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se movio Costo a la card principal del tramite para mayor visibilidad.
- Se agrego badge destacado con label COSTO.
- Se elimino bloque de costo al final para evitar duplicacion.
- Se formatea el importe en frontend con Intl.NumberFormat('es-AR', { maximumFractionDigits: 0 }) para mostrar miles con punto y sin decimales.
- Se antepone simbolo $ al valor.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Ajuste integral detalle de tipo de tramite

**Tarea:** Ordenar y alinear /configuracion/tramites/configuracion/<id>/ con los cambios recientes de template/costo/requisitos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En tab Datos se ordenaron campos clave: nombre/codigo, area/subarea.
- Costo ahora muestra fallback Sin Costo y formato moneda sin centavos con miles ($ 34.000).
- Requisitos e Informacion extra se muestran con HTML (safe) y solo si tienen contenido real (evita titulos vacios por HTML en blanco).
- Se agrego formateo JS para costo en locale es-AR.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Tramites ciudadano: separar detalle e inicio de tramite en 2 pantallas

**Tarea:** En 	ramites/detalle, dejar boton Iniciar Tramite y mover selector sede/fecha a pantalla siguiente.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/views.py
- portal_ciudadano/urls.py
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego vista PortalCiudadanoTramiteInicioView que reutiliza el mismo template y activa mostrar_selector_turno=True.
- Se agrego nueva ruta: portal_ciudadano:tramites_detalle_iniciar (/portal-ciudadano/tramites/detalle/iniciar/).
- En 	ramites/detalle/ ahora se muestra boton Iniciar Tramite (con ?tipo=<id>).
- El bloque actual de Elegir por sede / Elegir por fecha y el stepper se muestran solo cuando mostrar_selector_turno=True (pantalla siguiente).
- Se mantiene header y card de titulo en ambas pantallas.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix rango de fechas en seleccion por fecha (tramites iniciar)

**Tarea:** Evitar que en Elegir por fecha se puedan seleccionar fechas fuera de la anticipacion maxima de agenda.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Backend (	urnos_disponibles_por_fecha):
  - acepta 	ipo_id para acotar recursos al tramite.
  - calcula max_dias desde ConfiguracionTurnos activa del tramite.
  - bloquea fecha mayor a hoy + max_dias con error 400.
- Contexto de detalle/inicio:
  - agrega 	ramite_max_anticipacion_dias.
- Frontend calendario por fecha:
  - envia 	ipo_id al endpoint.
  - deshabilita dias pasados y dias posteriores a la fecha maxima permitida.
  - bloquea navegacion a meses fuera del rango permitido.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Badge de estado en header de detalle de tramite

**Tarea:** Agregar un badge informativo en el banner del detalle de tramite con estado resumido del tipo de gestion.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego estilo `.hero-status-badge` en el banner.
- Se inserto badge arriba del nombre del tramite con texto dinamico segun combinacion de:
  - `tramite_permite_online`
  - `tramite_permite_presencial`
  - `tramite_requiere_turno`
- Etiquetas posibles: `Online / Presencial`, `Disponible online`, `Presencial con turno`, `Presencial sin turno`, `Tramite disponible`.
- Se mantuvo el boton Volver en el extremo superior derecho del header.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Ajuste de altura de header en detalle de tramite

**Tarea:** Reducir largo visual del header/banner en portal ciudadano detalle de tramite.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se redujo padding vertical del bloque `.hero` en desktop: `56px 100px 92px` -> `42px 100px 56px`.
- Se redujo padding vertical del bloque `.hero` en mobile (`max-width: 900px`): `32px 20px 80px` -> `26px 20px 44px`.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Portada como fondo del banner en detalle de tramite

**Tarea:** Probar opcion 2 para mostrar imagen de portada en el header/hero de detalle de tramite.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se aplico `background-image` condicional en el `<section class="hero">` cuando existe `tipo_seleccionado.imagen_portada`.
- Se uso capa de gradiente + overlay para mantener legibilidad del titulo, subtitulo y badge.
- Se mantuvo fallback actual (gradiente liso) cuando el tramite no tiene portada.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Reversion portada en fondo de hero

**Tarea:** Volver atras la prueba de imagen de portada como fondo del banner en detalle de tramite.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino el `background-image` inline condicional del `<section class="hero">`.
- Se restauro el comportamiento anterior del header con gradiente fijo.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Portada en cards de listado de tramites

**Tarea:** Implementar imagen de portada en `/portal-ciudadano/tramites/`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego estilo `.tipo-thumb` para miniatura de portada.
- En cards destacadas (`.area-card`):
  - si `tipo.imagen_portada` existe, se muestra miniatura.
  - si no existe, se mantiene icono como fallback.
- En lista de otros tramites (`.tipos-lista-item`):
  - misma logica de portada/fallback a icono.
- Se ajusto `.area-main` para alinear mejor miniatura/icono con el nombre.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix portada no visible en listado de tramites

**Tarea:** Corregir que las imagenes de portada no aparecian en `/portal-ciudadano/tramites/`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- portal_ciudadano/views.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego `imagen_portada` al dict de cada item en `tipos_items` dentro de `PortalCiudadanoTramitesView`.
- Se agrego `imagen_portada: None` en el fallback estatico para mantener estructura consistente.
- Con esto, el template ya puede evaluar `{% if tipo.imagen_portada %}` correctamente.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Selector de icono para Tipo de Tramite + fallback

**Tarea:** Permitir seleccionar un icono desde configuracion de tramites y aplicar fallback a icono por defecto o portada.

**Archivos creados:**
- tramites/migrations/0007_tipotramite_icono.py

**Archivos modificados:**
- tramites/models.py
- configuracion/interfaces/web/forms/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- portal_ciudadano/views.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Modelo `TipoTramite`:
  - nuevo campo `icono` (`CharField`, opcional).
- Configuracion de tramites (formulario crear/editar):
  - se agrego campo `icono` en `TipoTramiteConfigForm`.
  - se forzo widget `Select` con lista predefinida de iconos.
  - se agrego opcion `Automatico (portada o icono por defecto)`.
  - se renderiza el selector en paso 3 "Template".
- Portal ciudadano (listado de tramites):
  - al armar `tipos_items`, el icono ahora se resuelve como `tipo.icono` o fallback por nombre (`_icon_for_tipo`).
  - la portada sigue teniendo prioridad visual en la card (si existe, se muestra imagen).

**Decisiones/supuestos:**
- Se mantiene comportamiento visual actual: portada > icono.
- Si no hay portada ni icono manual, queda icono por defecto inferido por nombre.

**Pendientes:**
- Aplicar migracion `0007_tipotramite_icono` en el entorno donde se pruebe.

## 2026-05-09 - Selector visual de iconos en configuracion de tramites

**Tarea:** Convertir seleccion de icono en grilla visual con click y agregar mas iconos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- configuracion/interfaces/web/forms/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se amplio `ICON_CHOICES` en `TipoTramiteConfigForm` con mas opciones de Font Awesome.
- En el form de alta/edicion de tipo de tramite:
  - se oculto el `select` tradicional de `icono`.
  - se agrego `#icono-picker` con botones visuales (icono + etiqueta).
  - seleccion por click con JS, sincronizando el valor real del campo `icono` para guardar.
  - se marca visualmente la opcion activa.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix visual iconos + labels mas en negrita

**Tarea:** Corregir que no se vean los iconos del picker y aumentar negrita en titulos de campos del form.

**Archivos modificados:**
- configuracion/interfaces/web/forms/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se cambio el catalogo de iconos a clases `fas/far` (compatibles con el uso actual del backoffice).
- Se ajusto render del icono en los botones del picker para asegurar visualizacion.
- Se agrego estilo `.field-label-strong` y se aplico a labels principales del formulario para mayor negrita.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix grilla de iconos no visible

**Tarea:** Corregir que no se mostraba la seleccion visual de iconos en editar tipo de tramite.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se cambio el loop del picker de `form.icono.field.choices` a `form.icono.field.widget.choices`.
- Motivo: las opciones del icono se cargan en el widget Select en `__init__`, no en `field.choices`.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Refuerzo de negrita en labels del form de tramites

**Tarea:** Hacer mas visible la negrita en titulos de campos del formulario de configuracion de tramites.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego estilo global para labels de bloque dentro del formulario:
  - `.tramite-config-form label.block { font-weight: 700; color: #111827; }`
- Se agrego clase `tramite-config-form` al `<form>` para scope local.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Estado seleccionado de icono mas visible

**Tarea:** Hacer mas evidente la opcion de icono seleccionada en el picker visual.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego estilo de seleccionado por `aria-pressed="true"`:
  - borde azul mas grueso
  - fondo azul claro
  - color de texto/icono resaltado
- Se agrego badge de check dentro del boton seleccionado.
- Se simplifico JS para que la marca dependa de `aria-pressed` y CSS.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Seleccion de icono con colores del template

**Tarea:** Ajustar estado seleccionado del picker de iconos para usar paleta del template.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- El estado seleccionado del icono ahora usa `--color-primario` del theme para borde, texto y check.
- Se elimino el azul fijo anterior.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Boton de icono seleccionado con color completo

**Tarea:** Hacer que el icono seleccionado se vea con todo el boton en color de marca.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Estado seleccionado de `.icon-option` ahora rellena todo el boton con `--color-primario`.
- Texto e icono del boton seleccionado pasan a blanco.
- Check se invierte (fondo blanco, icono en color de marca) para contraste.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Quitar tilde del icono seleccionado

**Tarea:** Eliminar check/tilde del picker de iconos y dejar solo boton relleno para estado seleccionado.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino markup del check visual en cada opcion de icono.
- Se eliminaron estilos `.icon-option-check`.
- El seleccionado queda solo por color completo del boton.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Refuerzo de estado activo en picker de iconos

**Tarea:** Resolver que no se aplique visualmente el boton seleccionado en picker de iconos.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego clase explicita `is-active` ademas de `aria-pressed` para marcar seleccion.
- CSS del estado seleccionado aplica para ambos selectores (`[aria-pressed="true"]` y `.is-active`).
- JS ahora hace `classList.toggle("is-active", active)` al sincronizar seleccion.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Color fijo de seleccion en picker de iconos

**Tarea:** Dejar boton seleccionado del icon picker con fondo rosa marca y texto/icono blancos.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Estado seleccionado (`.icon-option.is-active` / `aria-pressed=true`) ahora usa:
  - `background: #ff0080`
  - `border-color: #ff0080`
  - `color: #ffffff`

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix forzado de color en seleccion de icono

**Tarea:** Resolver que el boton seleccionado del icon picker no cambie de color al click.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se forzo el estado visual seleccionado por JS con estilos inline:
  - `background: #ff0080`
  - `borderColor: #ff0080`
  - `color: #ffffff`
- Al deseleccionar, se limpian estilos inline para volver al estado base.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Forzado !important en color de seleccion de iconos

**Tarea:** Corregir que visualmente no cambie el color del boton al seleccionar icono, aunque el valor se guarde.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En `syncIcono`, estilos inline ahora se aplican con prioridad `!important` via `style.setProperty(..., 'important')`.
- Al desactivar, se remueven propiedades inline con `removeProperty`.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Ajuste seleccionar por fecha: navegacion de mes y filtro por anticipacion real de agenda

**Tarea:** En `/portal-ciudadano/tramites/detalle/iniciar/`, permitir cambiar de mes en modo "Elegir por fecha" y evitar mostrar sedes/horarios cuando ninguna agenda llega a esa fecha.

**Archivos modificados:**
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Backend (`portal_ciudadano_turnos_disponibles_por_fecha`):
  - Se agrego filtro por recurso/agenda usando `configuracion_turnos.anticipacion_maxima_dias`.
  - Si la fecha pedida excede la anticipacion maxima de una agenda, ese recurso se omite y no aporta sedes/horarios.
- Frontend (modo fecha):
  - Se habilito avance de mes en calendario (se removio tope de mes maximo en boton siguiente).
  - Se mantiene bloqueo por dia para fechas pasadas o fuera de rango permitido por tramite.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Bloqueo de duplicados por tipo de tramite + refuerzo visual botones confirmar turno

**Tarea:** Evitar iniciar/confirmar tramites duplicados del mismo tipo y mostrar aviso en confirmar turno; destacar botones Volver/Confirmar turno.

**Archivos modificados:**
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agregaron helpers en `portal_ciudadano/views.py`:
  - `_get_tramite_abierto_mismo_tipo(ciudadano, tipo_tramite)`
  - `_get_turno_activo_mismo_tipo(ciudadano, tipo_tramite)`
- En `portal_ciudadano_confirmar_turno`:
  - antes de reservar, se verifica si ya existe tramite abierto del mismo tipo.
  - si no, se verifica si ya existe turno vigente del mismo tipo.
  - si hay bloqueo: se muestra mensaje en la pagina y se deshabilita Confirmar turno; en POST devuelve error y no reserva.
- En `PortalCiudadanoTramiteDetalleView.post`:
  - se bloquea continuar si ya hay tramite abierto del mismo tipo.
- En `PortalCiudadanoTramiteConfirmarView.post`:
  - se vuelve a validar duplicado de tramite abierto (doble control server-side).
- UI `turnos_confirmar.html`:
  - se agrego bloque visual para `bloqueo_mensaje`.
  - se destacaron botones:
    - Volver: fondo gris oscuro + texto blanco.
    - Confirmar turno: fondo gradiente magenta + mayor peso y sombra.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Reemplazo de turno vigente + aviso ampliado con detalle

**Tarea:** Permitir cambiar a un nuevo turno del mismo tramite, cancelando el anterior; mostrar aviso mas claro y grande con detalle del turno vigente.

**Archivos modificados:**
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En `portal_ciudadano_confirmar_turno`:
  - Si hay tramite abierto del mismo tipo, se mantiene bloqueo.
  - Si hay turno vigente del mismo tipo, ya NO bloquea; muestra aviso de reemplazo.
  - Al confirmar nuevo turno, se cancela automaticamente el turno vigente anterior (si es distinto).
- Se agrego aviso contextual ampliado en `turnos_confirmar.html`:
  - texto destacado y mas grande
  - detalle del turno vigente: sede, fecha, horario y codigo

**Pendientes:**
- Ninguno.

## 2026-05-09 - Aviso de reemplazo: mostrar solo hora de inicio

**Tarea:** En el aviso de turno vigente, mostrar solo horario de inicio.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se actualizo la linea de Horario para renderizar solo `hora_inicio` y no mostrar `hora_fin`.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Boton Modificar en Mis Turnos

**Tarea:** Agregar boton `Modificar` en `/portal-ciudadano/turnos/` y dirigir a pantalla de seleccion para reprogramar.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/turnos.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En turnos proximos con estado `PENDIENTE` o `CONFIRMADO` se agrego boton `Modificar`.
- El boton dirige a `portal_ciudadano:turno_calendario` del recurso del turno (`/turnos/solicitar/<recurso_id>/calendario/`) para elegir nueva fecha/horario.
- Se mantiene boton `Cancelar` existente.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Ajuste boton Modificar: redirigir a flujo de tramite

**Tarea:** Corregir boton `Modificar` en Mis Turnos para que no vaya al calendario legacy y vaya al inicio del tramite.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/turnos.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- `Modificar` ahora redirige a:
  - `portal_ciudadano:tramites_detalle_iniciar?tipo=<tipo_tramite_id>`
- Se muestra solo cuando el turno tiene `configuracion_turnos.tipo_tramite` asociado.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Cursor pointer en boton Confirmar turno

**Tarea:** Hacer que `Confirmar turno` muestre cursor tipo mano.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agrego `cursor: pointer;` a `.cta-confirmar`.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Botones Confirmar Turno alineados al template

**Tarea:** Usar botones del template en pantalla de confirmar turno.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se removieron estilos custom de `cta-volver` y `cta-confirmar`.
- Se reemplazo por clases del sistema:
  - `btn btn-secondary` para Volver
  - `btn btn-primary` para Confirmar turno
- Se mantiene una clase liviana `turno-cta` solo para tamaño/peso consistente.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Trazabilidad de reprogramacion de turnos (turno anterior/nuevo)

**Tarea:** Guardar historial explicito cuando se reemplaza un turno por otro del mismo tramite.

**Archivos creados:**
- portal/migrations/0004_turnociudadano_reprogramacion_relaciones.py

**Archivos modificados:**
- portal/models.py
- portal_ciudadano/views.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Modelo `TurnoCiudadano`:
  - nuevo campo `reemplaza_turno` (FK a `TurnoCiudadano`, nullable)
  - nuevo campo `reemplazado_por_turno` (FK a `TurnoCiudadano`, nullable)
- Flujo `portal_ciudadano_confirmar_turno`:
  - cuando se confirma un nuevo turno y habia uno vigente del mismo tipo:
    - se cancela el anterior
    - se vincula el nuevo con `reemplaza_turno = turno_anterior`
    - se vincula el anterior con `reemplazado_por_turno = turno_nuevo`
- Resultado: queda trazabilidad explicita del reemplazo en ambos sentidos.

**Pendientes:**
- Aplicar migracion `portal 0004_turnociudadano_reprogramacion_relaciones` en el entorno.

## 2026-05-09 - Estados de trazabilidad por reprogramacion (ciudadano/municipio)

**Tarea:** Incorporar estados mas trazables para distinguir cancelacion vs modificacion (reprogramacion) por ciudadano o municipio.

**Archivos creados:**
- portal/migrations/0005_turnociudadano_estado_reprogramado.py

**Archivos modificados:**
- portal/models.py
- turnos/domain/policies.py
- turnos/domain/__init__.py
- portal_ciudadano/views.py
- turnos/infrastructure/selectors/backoffice.py
- portal_ciudadano/templates/portal_ciudadano/turnos.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se agregaron estados nuevos en `TurnoCiudadano.Estado`:
  - `REPROG_CIU` = Modificado por el ciudadano
  - `REPROG_SIS` = Modificado por el municipio
- En reemplazo automatico por nuevo turno (portal ciudadano):
  - el turno anterior ya no queda `CANCELADO_CIU`, ahora queda `REPROG_CIU`.
- Se mantienen estados de cancelacion existentes:
  - `CANCELADO_CIU` (cancelacion voluntaria)
  - `CANCELADO_SIS` (cancelacion por sistema/municipio)
- Se actualizaron constantes de dominio para incluir estados reprogramados.
- En backoffice, contador de "cancelados" ahora incluye tambien reprogramados para vista agregada.
- En portal ciudadano (`Mis Turnos` historial), se muestran etiquetas especificas para `REPROG_CIU` y `REPROG_SIS`.

**Pendientes:**
- Aplicar migraciones `portal 0004` y `portal 0005` en el entorno.

## 2026-05-09 - Texto de estado: municipio -> sistema

**Tarea:** Cambiar referencias de "Modificado por el municipio" a "Modificado por el sistema".

**Archivos modificados:**
- portal/models.py
- portal/migrations/0005_turnociudadano_estado_reprogramado.py
- portal_ciudadano/templates/portal_ciudadano/turnos.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Etiqueta del estado `REPROG_SIS` actualizada a "Modificado por el sistema" en modelo/migracion.
- Texto visible en historial de Mis Turnos actualizado a "Modificado por el sistema".

**Pendientes:**
- Ninguno.

## 2026-05-09 - Iniciar tramite sin turno: render de campos en lugar de agenda

**Tarea:** En `/portal-ciudadano/tramites/detalle/iniciar/`, cuando el tramite no requiere turno, mostrar formulario de continuidad en vez de agenda/turnos.

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En el bloque de `mostrar_selector_turno`, se agrego condicion:
  - `tramite_requiere_turno=True`: mantiene selector por sede/fecha y agenda.
  - `tramite_requiere_turno=False`: muestra formulario para continuar tramite.
- Formulario nuevo (sin turno):
  - `tipo_id` hidden
  - selector de modalidad (`virtual` / `presencial`) segun configuracion del tipo
  - render de `campos_extra` dinamicos (`select`, `checkbox`, `file`, inputs varios)
  - boton `Continuar tramite` (submit al post actual)
- Se reutiliza el flujo backend existente de `PortalCiudadanoTramiteDetalleView.post` para guardar draft y continuar.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Detalle tipo de tramite: campos dinamicos dentro de Datos + layout sin tarjetas por dato

**Tarea:** En `/configuracion/tramites/configuracion/<id>/`, mover campos dinamicos a tab Datos y mejorar composicion visual (sin tarjeta por cada dato).

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino la pestaña/tab `Campos dinamicos`.
- Se movio el bloque de `campos_dinamicos` al final de la tab `Datos`.
- Se remaqueto tab `Datos` para mostrar informacion en formato mas similar al formulario:
  - labels y valores en grilla
  - sin tarjetas individuales para cada campo
  - se mantiene formateo de costo y bloques ricos (requisitos/info extra/portada)

**Pendientes:**
- Ninguno.

## 2026-05-09 - Detalle tipo de tramite con estructura 1/2/3/4 como formulario

**Tarea:** Ajustar tab Datos del detalle para replicar estructura del form con secciones numeradas 1, 2, 3, 4.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se reorganizo `data-panel="datos"` con bloques numerados:
  1. Datos principales
  2. Reglas
  3. Template
  4. Campos extra dinamicos
- Se mantuvo tab Sedes y tab Agendas.
- Campos dinamicos quedan al final de Datos (no en tab separada).
- Se conserva formato de costo y contenido enriquecido (requisitos/info extra).

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix guardado campos extra: mostrar errores de formset

**Tarea:** Resolver caso donde al agregar campo extra en editar tipo de tramite no guarda y vuelve a la misma pagina sin error visible.

**Archivos modificados:**
- configuracion/interfaces/web/views/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_form.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En `form_valid` de `_TramiteTipoConfiguracionBaseView`:
  - si `campos_formset` es invalido, ahora se agrega `messages.error` explicito.
- En template de formulario de tipo de tramite:
  - se muestran `campos_formset.non_form_errors` arriba del bloque de campos extra.
  - se muestran `campo_form.non_field_errors` por item.
  - se muestran errores por campo (`nombre`, `codigo`, `tipo_dato`, `orden`, etc.).

**Resultado esperado:**
- Si falla guardado de un campo extra, ahora se ve claramente que campo/validacion lo bloquea.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Campo codigo no obligatorio en campos extra dinamicos

**Tarea:** Evitar que `codigo` sea obligatorio al agregar/editar campos extra dinamicos de tipo tramite.

**Archivos modificados:**
- configuracion/interfaces/web/forms/tramites.py
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En `CampoDinamicoTramiteInlineConfigForm.__init__` se agrego:
  - `self.fields["codigo"].required = False`

**Pendientes:**
- Ninguno.

## 2026-05-09 - Iniciar tramite sin turno: ocultar modalidad cuando no corresponde

**Tarea:** Evitar mostrar selector de modalidad en `/portal-ciudadano/tramites/detalle/iniciar/` cuando el tramite no requiere eleccion.

**Archivos modificados:**
- portal_ciudadano/views.py
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Template: en formulario sin turno, el selector de `modalidad_atencion` solo se muestra si el tramite permite ambas (`online` y `presencial`).
- Backend: si no llega modalidad y solo hay una habilitada, se autocompleta automaticamente antes de validar.

**Resultado esperado:**
- No aparece selector de modalidad cuando solo hay una modalidad posible.
- El guardado continua sin error de modalidad faltante en esos casos.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Iniciar tramite sin turno: unificar titulo y quitar card superior

**Tarea:** Quitar duplicacion de titulos en flujo sin turno; dejar solo un bloque con titulo "Completa los datos para continuar".

**Archivos modificados:**
- portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se elimino la card superior redundante del formulario sin turno.
- Se cambio el titulo del bloque principal de "Datos del tramite" a "Completa los datos para continuar".
- El selector de modalidad (si aplica) se movio dentro de ese mismo bloque.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Bloqueo de agendas para tramites sin turno

**Tarea:** Si un tipo de tramite no requiere turno, impedir crear/editar agenda desde cualquier acceso relacionado.

**Archivos modificados:**
- turnos/interfaces/web/forms/__init__.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_detail.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Backend (form de ConfiguracionTurnos):
  - `tipo_tramite` ahora lista solo tipos con `requiere_turno=True`.
  - validacion extra en `clean`: si llega un tipo sin turno (por URL/manipulacion), agrega error y bloquea guardado.
- Frontend (detalle de tipo de tramite):
  - si `requiere_turno=False`, se ocultan tabs y paneles de `Sedes` y `Agendas`.

**Resultado esperado:**
- No hay forma de crear agenda para un tramite sin turno ni desde UI ni forzando request.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Listado de tipos: accion de agenda segun estado real

**Tarea:** En `/configuracion/tramites/configuracion/`, ajustar accion de agenda por tipo de tramite:
- si requiere turno y tiene agenda -> ir directo a agenda
- si requiere turno y no tiene agenda -> ir a crear agenda
- si no requiere turno -> no mostrar accion de agenda (mostrar "Sin turno")

**Archivos modificados:**
- configuracion/interfaces/web/views/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- En queryset de `TramiteTipoConfiguracionListView` se agrego annotacion `agenda_config_id` con subquery a `ConfiguracionTurnos` por tipo.
- En columna Acciones del template:
  - `tipo.requiere_turno=False` -> badge `Sin turno`.
  - `tipo.requiere_turno=True` y `agenda_config_id` -> link a `turnos:disponibilidad_grilla`.
  - `tipo.requiere_turno=True` y sin agenda -> link a `turnos:configuracion_crear?tipo_tramite=<id>`.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Filtro Con turno / Sin turno en listado de tipos de tramite

**Tarea:** Agregar filtro para distinguir tramites con turno y sin turno en `/configuracion/tramites/configuracion/`.

**Archivos modificados:**
- configuracion/interfaces/web/views/tramites.py
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- View:
  - nuevo parametro GET `requiere_turno`.
  - aplica filtro booleano cuando vale `1` o `0`.
  - se guarda en `context["filtros"]` para mantener seleccion en UI.
- Template:
  - nuevo select `Turno (todos / con turno / sin turno)` en barra de filtros.
  - paginacion conserva `requiere_turno` en querystring.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Color de icono agenda en listado de tramites

**Tarea:** Diferenciar visualmente estado de agenda en acciones del listado de tipos de tramite.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Si `agenda_config_id` existe: icono/link agenda en verde.
- Si no existe agenda: icono/link crear agenda en rojo.
- Se mantiene logica previa de ocultar agenda para tramites sin turno.

**Pendientes:**
- Ninguno.

## 2026-05-09 - Fix color de iconos agenda (forzado inline)

**Tarea:** Resolver que los iconos de agenda no reflejaban verde/rojo por estilos globales heredados.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Se removieron clases de color en el enlace y se aplico color inline en el icono:
  - agenda existente: `#15803d` (verde)
  - agenda faltante: `#b91c1c` (rojo)

**Pendientes:**
- Ninguno.

## 2026-05-09 - Destino de icono agenda: listado por tramite (multi-sede)

**Tarea:** Ajustar destino del icono de agenda en listado de tipos para contemplar tramites con varias agendas por sede.

**Archivos modificados:**
- configuracion/interfaces/templates/configuracion/tramite_tipo_configuracion_list.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- El icono de agenda (verde/rojo) ahora lleva a:
  - `turnos:configuracion_lista?tramite=<tipo.id>`
- Esto aplica tanto cuando ya hay agenda como cuando no hay agenda.
- Objetivo: entrar al listado filtrado del tramite y desde ahi crear/editar agenda especifica por sede.

**Pendientes:**
- Ninguno.

## 2026-05-10 - Boton en configuraciones de turnos: volver a listado de tramites

**Tarea:** En `/turnos/configuraciones/`, reemplazar boton superior que iba a Sedes para que vaya al listado de tramites.

**Archivos modificados:**
- turnos/interfaces/templates/turnos/backoffice/configuracion_lista.html
- docs/tmp/WORKLOG.md

**Cambios realizados:**
- Boton superior izquierdo actualizado:
  - URL: `configuracion:tramites_configuracion`
  - Texto: `Tramites`
  - Icono: `fa-list`

**Pendientes:**
- Ninguno.

## 2026-05-10 - Sedes: campo permite turnos y filtro en agendas

**Tarea:** Agregar en Sede el campo `permite_turnos` y evitar que sedes sin turnos aparezcan en la creacion de agendas.

**Archivos creados:**
- `turnos/migrations/0004_sedeturno_permite_turnos.py`

**Archivos modificados:**
- `turnos/models.py`
- `turnos/interfaces/web/forms/__init__.py`
- `turnos/interfaces/templates/turnos/backoffice/sede_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego `permite_turnos` en `SedeTurno` con `default=True`.
- En `ConfiguracionTurnosForm`, el selector de sede ahora filtra por `activo=True` y `permite_turnos=True`.
- Se agrego validacion defensiva para impedir guardar agenda si la sede no permite turnos.
- En el form de alta/edicion de sede se agrego checkbox visual `Permite turnos`.

**Decisiones o supuestos:**
- Se mantiene `default=True` para no cortar flujo en sedes existentes.

**Pendientes:**
- Aplicar migracion en entorno (`python manage.py migrate`) cuando se ejecute el flujo operativo.

## 2026-05-10 - Agenda desde tramite: contexto bloqueado

**Tarea:** Ajustar flujo desde `configuracion/tramites/configuracion/` hacia `turnos/configuraciones/?tramite=...` para ocultar filtros y crear agenda con tramite precargado/bloqueado.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_form.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En listado de configuraciones, cuando llega `?tramite=<id>`:
  - se detecta contexto de tramite,
  - se oculta el bloque de filtros,
  - se actualiza texto contextual,
  - el boton principal pasa a `Nueva agenda` y conserva `?tramite=<id>`.
- En alta de configuracion:
  - titulo: `Nueva agenda`,
  - acepta contexto por `tramite` o `tipo_tramite`,
  - precarga `Area`, `Subarea`, `Tramite`,
  - bloquea esos campos en UI,
  - envia sus valores por `hidden` para mantener integridad en POST.
- En formulario, breadcrumb/cancelar vuelven al listado con `?tramite=<id>` cuando corresponde.

**Decisiones o supuestos:**
- `Sede` queda editable, porque el requerimiento pide bloquear solo area/subarea/tramite.

**Pendientes:**
- Validacion visual en navegador del flujo exacto con links desde icono de agenda.

## 2026-05-10 - Filtro Activa en configuraciones de turnos

**Tarea:** Agregar filtro por estado activa/inactiva en `turnos/configuraciones/`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego lectura de query param `activo` en el listado.
- Se aplica filtro backend por `config.activo` cuando `activo` es `1` o `0`.
- Se agrego selector visual `Activa` al bloque de filtros con opciones `Todas / Si / No`.
- Se persiste valor seleccionado en recarga de filtros.

**Pendientes:**
- Validacion visual en navegador.

## 2026-05-10 - Agenda backoffice: card principal de resumen

**Tarea:** En `turnos/agenda/?config=<id>` agregar card principal con datos de la agenda seleccionada.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `turnos/infrastructure/selectors/backoffice.py`
- `turnos/interfaces/templates/turnos/backoffice/agenda.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrega `config_actual` al contexto de agenda cuando viene `config` por querystring.
- Se renderiza una card superior de resumen con:
  - nombre de agenda,
  - tramite,
  - sede,
  - estado activa/inactiva,
  - modo,
  - anticipacion minima/maxima,
  - regla de cancelacion ciudadana.

**Pendientes:**
- Validacion visual en navegador para ajustes finos de espaciado/textos.

## 2026-05-10 - Agenda: quitar filtro de configuracion

**Tarea:** En `turnos/agenda/?config=...` quitar selector de configuracion en filtros.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/agenda.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se elimino el selector visual de `Configuracion`.
- Se mantiene `config` por `input hidden` cuando viene por querystring, para no perder contexto al filtrar por estado.

## 2026-05-10 - Turnos ciudadano: mes en cuadrado de fecha

**Tarea:** En `portal-ciudadano/turnos/` agregar mes en el badge de fecha para evitar ambiguedad.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se agrego el mes abreviado (`{{ turno.fecha|date:"M"|upper }}`) en el cuadrado de fecha para turnos proximos y pasados.

## 2026-05-10 - Disponibilidad: volver al listado correcto segun origen

**Tarea:** Desde `turnos/configuraciones/<id>/disponibilidad/`, que `Volver al listado` respete si se ingreso desde listado por tramite o desde listado general.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/configuracion_lista.html`
- `turnos/interfaces/web/views/configuracion.py`
- `turnos/interfaces/templates/turnos/backoffice/disponibilidad_grilla.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En listado de configuraciones, el link `Disponibilidad` ahora propaga `?tramite=<id>` cuando el listado esta en contexto de tramite.
- En `DisponibilidadGrillaView`, se calcula `volver_url`:
  - si viene `tramite` -> vuelve a `turnos/configuraciones/?tramite=<id>`
  - si no -> vuelve a `turnos/configuraciones/`.
- El boton `Volver al listado` usa `{{ volver_url }}`.

## 2026-05-10 - Tramites iniciar: mostrar todas las sedes en modo por fecha

**Tarea:** Evitar percepcion de restriccion por sede al cambiar turno; permitir visualizar y seleccionar cualquier sede del tramite en modo por fecha.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- API `turnos_disponibles_por_fecha` ahora devuelve todas las sedes/recursos del tramite (aunque en una fecha no tengan slots).
- En UI de `tramites/detalle/iniciar` (modo por fecha):
  - se listan todas las sedes,
  - si una sede no tiene horarios para la fecha seleccionada se muestra ` (sin horarios)`,
  - al seleccionarla se muestra mensaje explicito en lugar de lista vacia,
  - el hint distingue cuando ninguna sede tiene disponibilidad ese dia.

**Nota funcional:**
- No hay restriccion por tener un turno previo; la disponibilidad sigue dependiendo de agenda activa, fecha y cupos.

## 2026-05-10 - Diagnostico y correccion de Sede 1 no visible en iniciar tramite

**Tarea:** Verificar por que `Sede 1` no aparecia en `portal-ciudadano/tramites/detalle/iniciar/?tipo=14` y corregirlo.

**Acciones realizadas:**
- Se inspecciono base de datos en contenedor.
- Hallazgo: `ConfiguracionTurnos` id=2 (Sede 1, tramite 14) estaba activa pero sin `RecursoTurnos` vinculado (`recursoturnos=None`).
- Se creo/vinculo `RecursoTurnos` faltante para esa configuracion:
  - nombre: `Agenda Renovacion Licencia Conducir - Sede 1`
  - recurso id: 2
  - activo: `True`
- Verificacion final: tramite 14 quedo con ambas configuraciones activas y recurso activo en Sede 1 y Sede 2.

**Nota:**
- Esta fue una correccion de datos (no de codigo) para normalizar configuraciones preexistentes.

## 2026-05-10 - Agenda backoffice: incluir turnos vinculados por recurso al filtrar por config

**Tarea:** Corregir `turnos/agenda/?config=<id>` para mostrar turnos que no tienen `configuracion_id` directo pero si `recurso.configuracion_turnos_id`.

**Archivos modificados:**
- `turnos/infrastructure/selectors/backoffice.py`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En `build_agenda_context`, el filtro por `config_id` paso de:
  - `turnos.filter(configuracion_id=config_id)`
  a:
  - `turnos.filter(Q(configuracion_id=config_id) | Q(recurso__configuracion_turnos_id=config_id))`

**Diagnostico de dato real:**
- Turno `3M03N8RX`: `configuracion_id=None`, `recurso_id=2`, `recurso.configuracion_turnos_id=2`.
- Por eso no aparecia con el filtro anterior.

## 2026-05-10 - Detalle de turno backoffice: datos completos y justificativo de cancelacion

**Tarea:** Mejorar `turnos/turnos/<id>/` mostrando mas detalle y reforzar cancelacion por sistema con justificativo.

**Archivos modificados:**
- `turnos/interfaces/templates/turnos/backoffice/turno_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reorganizo el bloque de detalle con datos mas completos: codigo, fecha, horario (inicio), tramite, sede, direccion, motivo y solicitado.
- Se mantuvo la trazabilidad de procesado por operador cuando aplica.
- En la accion de cancelar turno se explicita justificativo obligatorio con texto de trazabilidad.

## 2026-05-10 - Ciudadano: visibilidad de turnos cancelados y re-agendado

**Tarea:** Mostrar al ciudadano cuando un turno fue cancelado y ofrecer accion para generar uno nuevo del mismo tramite, visible en Mis Turnos y Mi Perfil.

**Archivos modificados:**
- `portal/infrastructure/selectors/turnos_ciudadano.py`
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/mi_perfil.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Selector de turnos ciudadano:
  - agrega `turnos_cancelados` (futuros) para estados cancelado/reprogramado,
  - mantiene `turnos_proximos` solo pendiente/confirmado,
  - mejora `select_related` para render de tramite/sede sin consultas extra.
- `Mis Turnos`:
  - se agrega bloque visual superior de `Turno cancelado` con fecha, horario inicio y codigo,
  - incluye boton `Generar nuevo turno` al flujo iniciar del mismo tramite.
- `Mi Perfil`:
  - se agrega contador `turnos_cancelados_count` en contexto,
  - se renderiza banner de aviso con acceso directo a `Mis Turnos`.

## 2026-05-10 - Ajuste final cancelaciones de turno para ciudadano

**Tarea:** Mostrar solo cancelaciones por sistema como aviso/accion y mover cancelaciones por ciudadano a pasados.

**Archivos modificados:**
- `portal/infrastructure/selectors/turnos_ciudadano.py`
- `portal_ciudadano/templates/portal_ciudadano/turnos.html`
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/mi_perfil.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `turnos_cancelados_sistema`: solo estados `CANCELADO_SIS` y `REPROG_SIS` (futuros).
- `turnos_historial`: incluye `fecha < hoy` y tambien cancelados/modificados por ciudadano (`CANCELADO_CIU`, `REPROG_CIU`) aunque la fecha sea futura.
- En `Mis Turnos`:
  - bloque especial de proximos solo para cancelados por sistema,
  - muestra motivo (`notas_backoffice`),
  - mantiene boton `Generar nuevo turno`.
- En `Mi Perfil`:
  - se elimina la card informativa,
  - se usa campanita con badge de cantidad (solo cancelados por sistema), linkeada a `Mis Turnos`.
- En contexto de perfil, `turnos_cancelados_count` ahora cuenta solo cancelados/modificados por sistema.

## 2026-05-10 - Header portal ciudadano: iconos mas grandes y renovados (mi perfil)

**Tarea:** Agrandar iconos del header y usar iconos mas modernos.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/mi_perfil.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Iconos del header pasaron a 34x34 con fondo circular translúcido y hover.
- Se reemplazaron SVG chicos por iconos Font Awesome mas legibles:
  - Inicio (`fa-house`)
  - Perfil (`fa-user`)
  - Turnos (`fa-calendar-days`)
  - Avisos (`fa-bell`)
  - Chat (`fa-comments`)
- Se mantuvo badge de campanita para cancelaciones por sistema.

## 2026-05-10 - Campanita con indicador y desplegable de notificaciones (mi perfil)

**Tarea:** Reemplazar acceso simple de campanita por notificador visual con dropdown de ultimas notificaciones, sin crear pagina nueva.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/mi_perfil.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En contexto de `Mi Perfil` se agrega `turnos_cancelados_notificaciones` (ultimos 5 turnos cancelados/modificados por sistema).
- Campanita ahora:
  - muestra indicador visual con estrellita (`?`) cuando hay notificaciones,
  - abre dropdown con detalle de cada notificacion (fecha, hora inicio, codigo, tramite, motivo),
  - incluye link `Ver mis turnos`.
- Si no hay notificaciones, muestra estado vacio en dropdown.
- Se agrego JS liviano para abrir/cerrar dropdown sin navegar.

## 2026-05-10 - Campanita con dropdown replicada en headers del portal

**Tarea:** Replicar campanita con indicador y desplegable de notificaciones en mas pantallas del portal ciudadano.

**Archivos modificados:**
- `portal_ciudadano/views.py`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `PortalCiudadanoAuthTemplateView` ahora inyecta contexto global de notificaciones de turnos cancelados por sistema:
  - `turnos_cancelados_count`
  - `turnos_cancelados_notificaciones` (ultimas 5)
- En los headers de templates con iconos se reemplazo campanita por:
  - indicador visual `?` cuando hay notificaciones,
  - desplegable con fecha, hora, codigo, tramite y motivo,
  - link a `Mis turnos`.
- Se agrego JS liviano para toggle/cierre del dropdown sin redireccionar.

## 2026-05-10 - Unificacion visual de iconos de header en portal ciudadano

**Tarea:** Unificar estilo visual de iconos de header en pantallas del portal ciudadano.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Iconos del header unificados en 34x34 con fondo circular translúcido y hover.
- Iconografia de header migrada a Font Awesome (home/perfil/turnos/campanita/chat).
- Ajuste responsive unificado para mobile (`30x30`).
- Campanita conserva dropdown de notificaciones y badge `?`.

## 2026-05-10 - Pulido final de header iconos (spacing/alineacion)

**Tarea:** Ajuste fino de espaciado y alineacion de iconos de header en portal ciudadano.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html`
- `portal_ciudadano/templates/portal_ciudadano/mi_perfil.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- `top-links` unificado con `gap: 12px` desktop.
- Ajuste de alineacion vertical de iconos (`.icon-link i { line-height: 1; }`).
- Se mantuvieron dimensiones unificadas de iconos y estilo hover previamente definidos.

## 2026-05-10 - Header con iconos en base_seccion (pantalla Mis Turnos)

**Tarea:** Unificar header de `base_seccion.html` al estilo de iconos (pantalla `portal-ciudadano/turnos/`).

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/base_seccion.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se reemplazo nav de texto por iconos circulares (Inicio, Perfil, Turnos, Programas, Chat).
- Se unifico estilo de iconos (34x34, hover, responsive 30x30).
- Se mantuvo boton `Mi perfil`.

## 2026-05-10 - Ajuste global mobile: gap iconos header a 8px

**Tarea:** Aplicar en todas las paginas de portal ciudadano el ajuste de compactacion mobile del bloque de iconos.

**Archivos modificados:**
- `portal_ciudadano/templates/portal_ciudadano/base_seccion.html`
- `portal_ciudadano/templates/portal_ciudadano/mi_perfil.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html`
- `portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html`
- `portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html`
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- En media query mobile se unifico `top-links` con `gap: 8px` para todos los headers con iconos.
- tarea: Agenda backoffice: reemplazo de cards por tabs con conteos por estado y sin filtro de estado.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Eliminado bloque de filtro por estado.
    - Reemplazadas cards de contadores por tabs (Pendientes, Confirmados, Completados, Cancelados) con cantidad.
    - Tabla del dÃ­a filtrable por tab en cliente (JS) con estado vacÃ­o por solapa.
    - Ajuste de clases activas para que no queden tabs con estilos acumulados.
  - decisiones/supuestos:
    - Se mantuvo navegaciÃ³n por fecha y filtro por configuraciÃ³n cuando existe `config` en querystring.
    - El pedido de â€œsacar filtroâ€ se interpreta como quitar filtro manual de estado.
  - pendientes:
    - ValidaciÃ³n visual final con el usuario contra patrÃ³n de `/legajos/programas/2/`.
- tarea: CorrecciÃ³n de acentos y texto con codificaciÃ³n daÃ±ada en agenda backoffice.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - CorrecciÃ³n de mojibake y acentos en tÃ­tulo, comentarios y textos visibles (navegaciÃ³n, anticipaciÃ³n, cancelaciÃ³n, sÃ­, cÃ³digo, dÃ­a).
  - decisiones/supuestos:
    - Se mantuvo el guion largo en el tÃ­tulo `Agenda â€” fecha`.
  - pendientes: ninguno

- tarea: Ajuste visual de contadores en tabs de agenda.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Contadores de tabs mÃ¡s grandes (	ext-base) y sin fondo (se quitaron badges circulares).
  - pendientes: ninguno

- tarea: RediseÃ±o de navegaciÃ³n de fechas en agenda backoffice como tira horizontal.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/infrastructure/selectors/backoffice.py
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Se generÃ³ genda_dias (7 dÃ­as) con abreviaturas ES de dÃ­a/mes para render uniforme (LUN/MAR..., ENE/FEB...).
    - Se reemplazÃ³ bloque de fecha anterior/Hoy/siguiente por tira horizontal sin card y chevrones en puntas.
    - Cada dÃ­a se muestra en formato: dÃ­a (arriba), nÃºmero grande (centro), mes (abajo).
    - Hoy se destaca en color rosa de branding; fecha seleccionada en oscuro.
  - decisiones/supuestos:
    - La tira se centra en la fecha seleccionada (comportamiento de desplazamiento con chevrones).
  - pendientes:
    - Ajuste visual fino de tamaÃ±o/ancho de cada casillero segÃºn preferencia final.


- tarea: Ajuste UX de tira de fechas en agenda (ubicaciÃ³n, tamaÃ±o y desplazamiento).
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - La tira de fechas se moviÃ³ entre la card de detalles y la card de tabs.
    - Se redujo tamaÃ±o de casilleros y chevrones para una lÃ­nea mÃ¡s compacta.
    - Chevrones ahora desplazan horizontalmente sin recargar pÃ¡gina.
    - Se agregÃ³ desplazamiento con mouse (drag horizontal) y bloqueo de click accidental al arrastrar.
  - pendientes: ninguno


- tarea: CompactaciÃ³n visual extra de tira de fechas en agenda.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Se redujo tamaÃ±o general del casillero y tipografÃ­as (dÃ­a, nÃºmero, mes).
    - Se centrÃ³ mejor el bloque completo y el contenido interno de cada fecha.
  - pendientes: ninguno


- tarea: ConversiÃ³n de tira de dÃ­as a carrusel con mÃ¡s rango.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/infrastructure/selectors/backoffice.py
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Rango de fechas ampliado a 61 dÃ­as (30 previos, fecha actual, 30 siguientes).
    - Se marca la fecha seleccionada con id y se centra automÃ¡ticamente al cargar (scrollIntoView).
    - Se mantiene desplazamiento por drag y botones laterales.
  - pendientes: ninguno


- tarea: Mejoras de fluidez del carrusel de fechas en agenda.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Barra de desplazamiento oculta (Firefox/Chrome/Edge).
    - Scroll suave habilitado en el carrusel.
    - Drag migrado a Pointer Events para interacciÃ³n mÃ¡s estable y sin trabas.
    - Ajuste de paso de chevron para desplazamiento mÃ¡s corto y fluido.
  - pendientes: ninguno


- tarea: Cambio de UX de selecciÃ³n de fecha en agenda (reemplazo de carrusel).
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Se eliminÃ³ el carrusel horizontal de fechas.
    - Se incorporÃ³ selector nativo input type=date con botÃ³n Ir para selecciÃ³n directa.
    - Se mantuvieron botones de dÃ­a anterior/siguiente y acceso rÃ¡pido Hoy.
    - Se mantiene preservaciÃ³n del query param config cuando aplica.
  - decisiones/supuestos:
    - Se priorizÃ³ facilidad y fluidez de selecciÃ³n frente a scroll horizontal.
  - pendientes: ninguno


- tarea: Ajuste visual del botÃ³n 'Ir' en selector de fecha de agenda.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - BotÃ³n Ir reducido (alto, padding, radio y tipografÃ­a) para menor protagonismo visual.
  - pendientes: ninguno


- tarea: Segunda reducciÃ³n del botÃ³n 'Ir' en agenda (tamaÃ±o real compacto).
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Se redujo altura a h-7, ancho mÃ­nimo y padding lateral para botÃ³n mini.
    - Se ajustÃ³ tamaÃ±o tipogrÃ¡fico a 11px y leading-none.
  - pendientes: ninguno


- tarea: BotÃ³n de envÃ­o de fecha en formato cuadrado con Ã­cono.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Reemplazo del texto Ir por Ã­cono a-arrow-right.
    - BotÃ³n compacto cuadrado (h-7 w-7) con accesibilidad (ria-label y 	itle).
  - pendientes: ninguno


- tarea: Aumento de tamaÃ±o de nÃºmeros en tabs de estados (agenda).
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
  - cambios realizados:
    - Contadores de tabs pasaron de 	ext-base a 	ext-lg.
  - pendientes: ninguno


- tarea: Corregir retorno desde detalle de turno a agenda de origen + unificar botÃ³n Volver.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/agenda.html
    - turnos/interfaces/templates/turnos/backoffice/turno_detalle.html
    - turnos/interfaces/web/views/turnos.py
  - cambios realizados:
    - Desde agenda, Ver detalle ahora envÃ­a 
ext con la URL actual (echa/config).
    - En detalle de turno, se reemplazÃ³ breadcrumb por botÃ³n Volver estilo estÃ¡ndar (flecha + texto).
    - La vista de detalle calcula genda_url (usa 
ext; fallback: agenda con fecha del turno y config efectiva).
    - Formularios de acciones (aprobar/rechazar/completar/cancelar) envÃ­an 
ext para volver al mismo contexto de agenda.
    - Redirects de acciones y validaciones preservan 
ext hacia detalle o agenda segÃºn corresponda.
  - decisiones/supuestos:
    - Se priorizÃ³ conservar siempre el contexto de origen (fecha/config) al navegar desde agenda.
  - pendientes: ninguno


- tarea: Arreglo de detalle de turno: notas internas tipo historial y cancelaciÃ³n.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/web/views/turnos.py
    - turnos/interfaces/templates/turnos/backoffice/turno_detalle.html
  - cambios realizados:
    - Notas internas ahora se guardan en modo historial (append), con marca de tiempo y usuario.
    - Mensaje de guardado actualizado a â€˜Nota agregada al historial internoâ€™.
    - Se muestra historial actual de notas en un bloque de lectura arriba del textarea.
    - Textarea de notas queda vacÃ­o para nueva entrada (no sobreescribe visualmente).
    - JS de mostrar formularios (rechazar/cancelar) movido al bloque correcto customJS para que cargue en ase.html.
  - decisiones/supuestos:
    - Se asume formato de historial en texto plano por lÃ­nea: [dd/mm/yyyy hh:mm] usuario: nota.
  - pendientes: ninguno


- tarea: Visibilidad explÃ­cita de historial de notas internas en detalle de turno.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/turno_detalle.html
  - cambios realizados:
    - Bloque de historial de notas siempre visible.
    - Si no hay contenido, muestra Sin notas internas registradas..
  - decisiones/supuestos:
    - Se prioriza feedback visual claro para distinguir falta de guardado vs historial vacÃ­o.
  - pendientes: verificar en entorno local persistencia real de DB.


- tarea: Ajuste de notas internas vs motivo de cancelaciÃ³n + notificaciones leÃ­das en campanita.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/application/services.py
    - portal_ciudadano/views.py
    - portal_ciudadano/urls.py
    - portal/infrastructure/selectors/turnos_ciudadano.py
    - portal_ciudadano/templates/portal_ciudadano/mi_perfil.html
    - portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html
    - portal_ciudadano/templates/portal_ciudadano/tramites.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/turnos.html
  - cambios realizados:
    - Cancelar/Rechazar por sistema ya no pisan 
otas_backoffice; ahora agregan lÃ­nea de historial con marcador [CANCELACION_SISTEMA] / [RECHAZO_SISTEMA].
    - En portal ciudadano, el motivo de notificaciÃ³n usa motivo_notificacion_cancelacion (motivo legible extraÃ­do del marcador) en lugar de mostrar todo 
otas_backoffice.
    - Campanita: agregado endpoint POST portal_ciudadano:notificaciones_turnos_leidas para marcar como leÃ­das.
    - Contexto autenticado de portal ciudadano ahora calcula notificaciones no vistas con sesiÃ³n (pc_notifs_turnos_vistas) y count no visto.
    - Al abrir dropdown de campanita, se marca leÃ­do por AJAX y se oculta badge visual en el momento.
  - decisiones/supuestos:
    - Marcado de leÃ­do implementado con sesiÃ³n (sin migraciÃ³n de DB) para mantener cambio chico y seguro.
  - pendientes:
    - ValidaciÃ³n funcional en entorno local del flujo completo (guardar/cancelar/abrir campanita/recargar).


- tarea: Mostrar quiÃ©n cancelÃ³ en detalle de turno + persistir operador en cancelaciÃ³n de backoffice.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/templates/turnos/backoffice/turno_detalle.html
    - turnos/interfaces/web/views/turnos.py
    - turnos/interfaces/module_api.py
    - turnos/application/services.py
  - cambios realizados:
    - En detalle de turno se agrega campo Cancelado por para estados cancelado/reprogramado.
    - LÃ³gica de visualizaciÃ³n: Ciudadano (cancelaciÃ³n/reprogramaciÃ³n ciudadana), operador (probado_por) o Sistema.
    - CancelaciÃ³n backoffice ahora recibe equest.user y lo guarda en probado_por + echa_aprobacion para trazabilidad.
  - decisiones/supuestos:
    - El campo tambiÃ©n aplica a estados reprogramados para mantener consistencia de trazabilidad.
  - pendientes: ninguno


- tarea: Fix IntegrityError en ediciÃ³n de tipo de trÃ¡mite por cÃ³digos vacÃ­os de campos dinÃ¡micos.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/tramites.py
  - cambios realizados:
    - Se incorporÃ³ normalizaciÃ³n/autogeneraciÃ³n de codigo para campos dinÃ¡micos cuando viene vacÃ­o en el formset.
    - Se valida colisiÃ³n de codigo contra existentes del mismo tipo y duplicados del mismo submit antes de guardar.
    - Si hay error de cÃ³digo, se corta el guardado y se muestran errores en formulario (evita IntegrityError 1062).
  - decisiones/supuestos:
    - Formato autogenerado: slugify(nombre) con _ y sufijo incremental (_2, _3, ...) cuando hay colisiÃ³n.
  - pendientes: ninguno


- tarea: Ajuste de pantalla de confirmaciÃ³n de trÃ¡mite (portal ciudadano).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Eliminada barra de botones/links: Inicio, Mis solicitudes, Nueva solicitud.
    - Resumen reformateado al estilo de confirmaciÃ³n con turno, en filas tipo data-row (Tipo, Modalidad, Campos adicionales).
    - Campos adicionales ahora renderiza en bloque legible (lÃ­nea por campo) en lugar de lista desalineada.
  - decisiones/supuestos:
    - Se mantiene fuera del resumen el campo Turno vinculado para simplificar como solicitÃ³ el usuario.
  - pendientes: ninguno


- tarea: Ajuste ciudadano de resumen en confirmar trÃ¡mite (nombre de campos + preview de imÃ¡genes).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - En backend se arma extras_resumen con nombre real del campo dinÃ¡mico (no ID tÃ©cnico), valor y metadata de adjunto (is_image, url).
    - En template se reemplaza bloque tÃ©cnico por Datos y se muestra Nombre: Valor para cada dato.
    - Si el dato corresponde a imagen adjunta, se muestra miniatura clickeable.
    - Se renombra modalidad irtual mostrada al usuario como Online.
  - pendientes: ninguno


- tarea: Reordenamiento de resumen en confirmar trÃ¡mite + datos de ciudadano.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Etiqueta Tipo reemplazada por TrÃ¡mite.
    - Resumen reformateado a grilla de tarjetas para mejor distribuciÃ³n visual.
    - Se agregaron datos del ciudadano: nombre/apellido, DNI, email y telÃ©fono.
    - Se mantiene bloque Datos cargados con preview de imÃ¡genes cuando corresponde.
  - pendientes: ninguno


- tarea: Unificar resumen de confirmar trÃ¡mite al estilo confirmar turno (sin datos de turno).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Resumen migrado a layout tipo data-row (como confirmaciÃ³n de turno).
    - Sede reemplazada conceptualmente por Modalidad como primer dato.
    - Se removieron datos de fecha/horario/lugar (no aplican para este flujo).
    - Campos extra: imagen se muestra con miniatura; archivo no imagen se muestra con Ã­cono y link.
  - pendientes: ninguno


- tarea: Igualar formato visual de card de confirmar trÃ¡mite con confirmar turno.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Card de resumen llevada a estilo base (ondo blanco, borde/sombra/padding del componente card).
    - Se agregÃ³ tÃ­tulo Resumen del trÃ¡mite con tipografÃ­a equivalente al flujo de turno.
    - Ajuste fino de espaciado interno en bloque de datos.
  - pendientes: ninguno


- tarea: Igualado estricto de card en confirmar trÃ¡mite respecto a confirmar turno.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Se cambiÃ³ el contenedor a card flush-top summary-card (misma convenciÃ³n visual de confirmar turno).
    - Se agregÃ³ definiciÃ³n base .card y .flush-top equivalente al patrÃ³n usado en el otro flujo.
    - Se unificÃ³ ancho del bloque de confirmaciÃ³n a min(620px, 100%) para igualar proporciÃ³n.
  - pendientes: validar visual en navegador con hard refresh.


- tarea: Remover rÃ³tulo 'Datos cargados' y renderizar extras como filas normales en resumen.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Se eliminÃ³ la fila agrupadora Datos cargados.
    - Cada campo extra ahora se muestra como data-row individual (label = nombre del campo, value = contenido/preview).
    - Se mantiene preview de imagen y link con Ã­cono para archivo.
  - pendientes: ninguno


- tarea: Igualado visual 1:1 de tramites/confirmar con turnos/confirmar (hero, solape y acciones).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Header: gap de iconos reducido a 8px.
    - Hero: tÃ­tulo/subtÃ­tulo reducidos a escala de turnos confirmar.
    - Card resumen: vuelve a superponerse sobre banner rosa (margin-top negativo + z-index).
    - Acciones: Editar y Enviar solicitud movidos dentro de la card y alineados al final con separaciÃ³n.
  - pendientes: validaciÃ³n visual final en navegador.


- tarea: Unificar botÃ³n de cabecera en portal ciudadano (sin duplicar perfil).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/base_seccion.html
  - cambios realizados:
    - Reemplazo de botÃ³n fijo Mi perfil por lÃ³gica condicional.
    - Usuario autenticado: botÃ³n Cerrar sesiÃ³n (POST logout).
    - Usuario no autenticado: botÃ³n Ingresar.
  - decisiones/supuestos:
    - El acceso a perfil queda Ãºnicamente por Ã­cono de persona, como pidiÃ³ el usuario.
  - pendientes: ninguno


- tarea: UnificaciÃ³n final de iconos de header en base_seccion al orden solicitado.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/base_seccion.html
  - cambios realizados:
    - Reemplazo del Ã­cono Programas por Campanita en el bloque de accesos rÃ¡pidos.
    - Orden final en este layout: Inicio, Perfil, Turnos, Campanita, Chat, Cerrar sesiÃ³n.
  - pendientes: ninguno


- tarea: Ajuste de header para usuarios no autenticados en base_seccion.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/base_seccion.html
  - cambios realizados:
    - Si no estÃ¡ autenticado, se muestra solo Ã­cono de Inicio + botÃ³n Iniciar sesiÃ³n.
    - Se ocultan Perfil, Turnos, Campanita y Chat para no autenticados.
    - Para autenticados se mantiene el set completo + Cerrar sesiÃ³n.
  - pendientes: ninguno


- tarea: UnificaciÃ³n global de gap en .top-links del portal ciudadano.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/base_seccion.html
    - portal_ciudadano/templates/portal_ciudadano/chat.html
    - portal_ciudadano/templates/portal_ciudadano/home.html
    - portal_ciudadano/templates/portal_ciudadano/login.html
    - portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html
    - portal_ciudadano/templates/portal_ciudadano/mi_perfil.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html
    - portal_ciudadano/templates/portal_ciudadano/tramites.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html
  - cambios realizados:
    - Se normalizÃ³ gap de .top-links a 8px en todas las pÃ¡ginas detectadas (desktop/mobile donde estaba definido).
  - pendientes: ninguno


- tarea: Unificar botones de confirmar turno al estilo de confirmar trÃ¡mite.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/turnos_confirmar.html
  - cambios realizados:
    - Reemplazo de estilos tn/	urno-cta por estilo 	iny-btn y 	iny-btn secondary (mismo look que Enviar solicitud/Editar).
    - Texto de acciones actualizado a Editar (secundario) y Confirmar (primario).
  - pendientes: ninguno


- tarea: Ajuste de tÃ­tulo en hero de tramites/confirmar.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Texto actualizado de ConfirmÃ¡ tu solicitud a Confirma tu trÃ¡mite.
  - pendientes: ninguno


- tarea: Cambiar texto de botÃ³n final en tramites/confirmar.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - BotÃ³n primario actualizado de Enviar solicitud a Confirmar.
  - pendientes: ninguno


- tarea: Reestructurar pantalla de turno confirmado con campos solicitados.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/turnos_confirmado.html
  - cambios realizados:
    - TrÃ¡mite mostrado en tÃ­tulo grande.
    - SecciÃ³n de detalle en formato filas: Sede, DirecciÃ³n sede, Fecha, Horario (solo inicio), CÃ³digo.
    - Se eliminÃ³ rango horario y foco anterior en nombre de recurso.
  - pendientes: ninguno


- tarea: Mover cancelados por sistema a historial cuando ya existe turno nuevo del mismo trÃ¡mite.
  - archivos creados: ninguno
  - archivos modificados:
    - portal/infrastructure/selectors/turnos_ciudadano.py
  - cambios realizados:
    - Se calcula conjunto de tipo_tramite con turnos vigentes (pendiente/confirmado).
    - Cancelados/reprogramados por sistema del mismo tipo se excluyen de 	urnos_cancelados_sistema (no aparecen en bloque de PrÃ³ximos con botÃ³n de generar nuevo turno).
    - Esos casos se incorporan a 	urnos_historial y se ordenan por fecha/hora descendente.
  - decisiones/supuestos:
    - Se usa config_efectiva.tipo_tramite y fallback a ecurso.configuracion_turnos.tipo_tramite para identificar el trÃ¡mite.
  - pendientes: ninguno


- tarea: Igualar pantalla portal-ciudadano/tramites/enviado con formato de turno confirmado.
  - archivos creados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_enviado.html
  - archivos modificados:
    - portal_ciudadano/views.py
  - cambios realizados:
    - Se cambió la vista `PortalCiudadanoTramiteEnviadoView` para usar template dedicado con mismo patrón visual que `turnos_confirmado`.
    - Se guarda `tramite_id` en sesión al confirmar para recuperar datos completos en la pantalla de enviado.
    - En contexto de enviado se exponen `tramite`, `modalidad` y `numero` para render consistente.
    - La nueva plantilla usa card superpuesta, icono de confirmación, filas de detalle y botones con el mismo layout/base visual que turno confirmado.
  - pendientes: ninguno
- tarea: Igualación 1:1 de textos/labels de tramites/enviado con turnos/confirmado.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_enviado.html
  - cambios realizados:
    - Hero actualizado con los mismos textos de `turnos_confirmado`.
    - Labels de detalle alineados al mismo set visual: Sede, Dirección sede, Fecha, Horario, Código.
    - CTA principal cambiado a `Ver mis turnos` para coincidir con confirmación de turnos.
  - pendientes: ninguno
- tarea: Ajustar textos y contenido de card en portal-ciudadano/tramites/enviado segun copy final.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/tramites_enviado.html
  - cambios realizados:
    - Hero actualizado a: "Trámite iniciado".
    - Texto descriptivo actualizado a "Tu trámite fue iniciado correctamente... Mis Trámites".
    - En la card se muestran: Modalidad, Fecha, Estado y Código, manteniendo icono verde y nombre del trámite.
    - CTA principal actualizado a "Ver mis trámites" apuntando a Mis Solicitudes.
  - pendientes: ninguno
- tarea: Cambiar boton secundario en confirmaciones a Mi Perfil.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/turnos_confirmado.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_enviado.html
  - cambios realizados:
    - En ambas vistas de confirmacion se reemplazo `Ir al inicio` por `Mi Perfil`.
    - El enlace ahora apunta a `portal_ciudadano:mi_perfil`.
  - pendientes: ninguno
- tarea: Agregar tabs Reclamos/Trámites en Mis Solicitudes y separar listado por tab.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html
  - cambios realizados:
    - Se incorporó parámetro `tab` (`reclamos`/`tramites`) con default `reclamos`.
    - Se reemplazó el filtro por tipo por tabs visuales con contador por sección.
    - El listado muestra solo la sección activa según tab.
    - Se mantiene búsqueda y filtro de estado, aplicado a la tab activa.
    - El botón Limpiar conserva la tab seleccionada.
  - pendientes: ninguno
- tarea: Cambiar configuracion/tramites/listado a formato listado y reforzar paginacion visual.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/templates/configuracion/tramite_list.html
  - cambios realizados:
    - Se reemplazo el render en cards por tabla/listado con columnas: Numero, Titulo, Tipo, Estado, Area, Prioridad, Inicio y Acciones.
    - Se mantuvo la paginacion existente del backend (20 por pagina).
    - Se mejoro la navegacion de paginacion mostrando numeros de pagina cercanos, ademas de Anterior/Siguiente.
  - pendientes: ninguno
- tarea: Cambiar configuracion/reclamos/listado a formato listado y reforzar paginacion visual.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/templates/configuracion/reclamo_list.html
  - cambios realizados:
    - Se reemplazo el render en cards por tabla/listado con columnas: Numero, Titulo, Tipo, Estado, Area, Prioridad, Ingreso y Acciones.
    - Se mantuvo la paginacion existente del backend (20 por pagina).
    - Se mejoro la navegacion de paginacion mostrando numeros de pagina cercanos, ademas de Anterior/Siguiente.
  - pendientes: ninguno
- tarea: Alinear look and feel de listados de Reclamos y Tramites con Conversaciones.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/templates/configuracion/tramite_list.html
    - configuracion/interfaces/templates/configuracion/reclamo_list.html
  - cambios realizados:
    - Se reestructuraron ambos listados con el mismo patron visual de `conversaciones/lista`: contenedor con `space-y-2`, header en card blanca, filtros en card blanca con labels y tabla en card blanca.
    - Tabla y estilos de filas/encabezados alineados con `w-full divide-y divide-gray-200`, `thead bg-gray-50` y acciones tipo link azul.
    - Se mantuvo paginacion existente y numerada, ajustando color activo al esquema azul de conversaciones.
  - pendientes: ninguno
- tarea: Ajustar ancho de listados de Reclamos/Tramites para evitar vista encajonada.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/templates/configuracion/tramite_list.html
    - configuracion/interfaces/templates/configuracion/reclamo_list.html
  - cambios realizados:
    - Contenedor principal cambiado de `max-w-7xl mx-4 lg:mx-8` a `w-full px-4 lg:px-8` para ocupar más ancho.
    - Wrapper de tabla ajustado con `w-full overflow-x-auto` para evitar scroll interno extraño por ancho.
  - pendientes: ninguno
- tarea: Mejorar historial de notas internas y mostrar cancelacion por sistema con motivo en detalle de turno.
  - archivos creados: ninguno
  - archivos modificados:
    - turnos/interfaces/web/views/turnos.py
    - turnos/interfaces/templates/turnos/backoffice/turno_detalle.html
  - cambios realizados:
    - Se parsea `notas_backoffice` para construir `notas_historial` en formato estructurado (fecha, autor, texto).
    - Se excluyen del historial visual las lineas de sistema (`[CANCELACION_SISTEMA]` y `[RECHAZO_SISTEMA]`) y se expone su contenido como `motivo_cancelacion_sistema`.
    - En template, Notas internas ahora se renderiza como listado cronologico legible con usuario y fecha.
    - Si estado es `CANCELADO_SIS`, se destaca badge "Cancelado por sistema" y se muestra bloque con motivo del operador.
  - pendientes: ninguno
- tarea: Notificaciones en campanita para solicitudes de cambio de datos (reclamos/tramites) con usuario y acceso directo.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - multiples templates en portal_ciudadano/templates/portal_ciudadano/*.html con bloque de campanita
  - cambios realizados:
    - Se agregaron notificaciones de accion `solicitud_datos_ciudadano` para ReclamoHistorial y TramiteHistorial.
    - Cada notificacion muestra tipo de solicitud, numero de tramite/reclamo, usuario solicitante y comentario/detalle.
    - Se agrego URL directa a detalle de reclamo/tramite para resolver la solicitud.
    - Se unifico menu de campanita para usar `portal_notificaciones` y `portal_notificaciones_count`.
    - Endpoint de marcar leidas ahora tambien registra como vistas las solicitudes de datos.
  - pendientes: ninguno
- tarea: Campanita mostrar ultimas 5 notificaciones y apagar vistas.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/*.html (bloques de campanita)
  - cambios realizados:
    - Se cambió la lógica para mostrar siempre las últimas 5 notificaciones combinadas (turnos + solicitudes de datos).
    - Se agregó estado `seen` por notificación y orden por fecha real.
    - El contador rojo ahora muestra solo no vistas.
    - Las notificaciones vistas quedan visualmente apagadas (fondo gris y opacidad menor).
  - pendientes: ninguno
- tarea: Mejorar solicitud de correccion de datos en detalle de solicitudes ciudadanas.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
  - cambios realizados:
    - Historial: normalizacion de comentarios para quitar prefijo tecnico `campo_dinamico:`.
    - Historial: agregado `comentario_label` para mostrar texto legible en UI.
    - Tramites: se implemento flujo de respuesta a `solicitud_datos_ciudadano` (GET+POST) con registro de historial `respuesta_solicitud_datos_ciudadano`.
    - UI detalle solicitud: bloque de “Solicitud de ampliacion de datos” ahora aplica tambien a tramites (no solo reclamos).
    - Formulario de tramite permite cargar nuevo valor del campo solicitado y comentario de respuesta.
    - Se expone `campo_objetivo`/`es_campo_dinamico` desde metadata para decidir input correcto.
  - pendientes: ninguno
- tarea: Corregir render de campanita en Mi Perfil (notificaciones con datos vacios).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/mi_perfil.html
  - cambios realizados:
    - Se reemplazo el bloque viejo que iteraba `portal_notificaciones` pero mostraba variables `turno.*` inexistentes.
    - Ahora Mi Perfil usa `notif.title/subtitle/detail/extra/url` igual que el resto de vistas del portal.
    - Se mantiene estilo diferencial por tipo (`solicitud_datos` vs `turno_cancelado_sistema`) y estado visto/no visto.
  - decisiones o supuestos:
    - El origen de tarjetas repetidas con `- -` era el template desalineado de Mi Perfil, no la generacion del contexto.
  - pendientes:
    - Validar visualmente con el usuario 24459123 que la campanita ya no muestre elementos vacios.
- tarea: Normalizar contenido de campanita (solicitudes de datos) para quitar texto técnico y actor vacío.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
  - cambios realizados:
    - Se agregó `import re`.
    - Se incorporó `_display_actor_name(user)` para fallback consistente: nombre completo -> username -> "Sistema".
    - Se incorporó `_format_solicitud_datos_notif_text(raw)` para limpiar `campo_dinamico:<nombre>` en notificaciones.
    - En notificaciones de reclamos/trámites se reemplazó:
      - `detail` para usar `_display_actor_name`.
      - `extra` para usar texto formateado sin prefijos técnicos.
  - decisiones o supuestos:
    - El bloque de campanita debe mostrar nombres amigables para ciudadano y no etiquetas internas de implementación.
  - pendientes:
    - Validación visual en usuario 24459123 del nuevo texto en campanita.
- tarea: Compactar cards de notificaciones en campanita.
  - archivos creados: ninguno
  - archivos modificados:
    - multiples templates en portal_ciudadano/templates/portal_ciudadano/*.html
    - portal_ciudadano/templates/portal_ciudadano/mi_perfil.html
  - cambios realizados:
    - Menú de notificaciones más compacto: menor ancho, menor padding y sombra más suave.
    - Cards de notificación más compactas: padding/márgenes reducidos.
    - Tipografía reducida y líneas más juntas para mostrar solo lo mínimo útil.
  - decisiones o supuestos:
    - Se mantuvo todo el contenido funcional (título, subtítulo, detalle y extra), solo se compactó visualmente.
  - pendientes:
    - Validación visual final en pantallas principales del portal ciudadano.
- tarea: Simplificar contenido de cards de campanita al mínimo solicitado.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/mi_perfil.html
    - portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html
    - portal_ciudadano/templates/portal_ciudadano/tramites.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
  - cambios realizados:
    - Notificación de solicitud de datos: título "Actualizacion de datos solicitada", luego "Tramite:"/"Reclamo:" y nombre del trámite/reclamo, sin texto extra técnico.
    - Notificación de turno: título "Turno cancelado por sistema".
    - En templates de campanita, `subtitle/detail/extra` se renderizan solo si tienen valor (sin líneas vacías).
  - pendientes: validación visual final.
- tarea: Agregar chevron derecho en cards de notificaciones de campanita.
  - archivos creados: ninguno
  - archivos modificados:
    - multiples templates en portal_ciudadano/templates/portal_ciudadano/*.html (bloques de campanita)
  - cambios realizados:
    - Cada card de notificación ahora usa layout flex (`justify-content: space-between; align-items: center`).
    - Se agregó chevron `>` a la derecha, centrado verticalmente, con color según tipo de notificación.
  - pendientes: validación visual final.
- tarea: Ocultar notificaciones resueltas/reemplazadas en campanita.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
  - cambios realizados:
    - Turnos cancelados por sistema: se filtran cuando ya existe un nuevo turno vigente (pendiente/confirmado) del mismo trámite creado luego de la cancelación.
    - Solicitudes de datos (reclamos/trámites): se filtran cuando ya existe respuesta `respuesta_solicitud_datos_ciudadano` posterior a la solicitud.
    - El contador de notificaciones ahora considera solo las notificaciones vigentes/no resueltas y no vistas.
  - decisiones o supuestos:
    - "Dato actualizado" se interpreta como existencia de historial de respuesta del ciudadano posterior a la solicitud.
  - pendientes:
    - Validación funcional en campanita con casos de reemplazo de turno y solicitud respondida.
- tarea: Ajustes finales de campanita (turnos vencidos y formato de solicitud de datos de trámite).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
  - cambios realizados:
    - Se fuerza ocultamiento de notificaciones de turnos cancelados con fecha anterior a hoy.
    - En solicitud de datos de trámite se quita el prefijo "Tramite:".
    - En esas notificaciones ahora se muestra nombre del trámite y debajo `Nro: <numero_tramite>`.
  - pendientes: validación visual.
- tarea: Ajustar formato de notificaciones de solicitud de datos (sin duplicados ni prefijos Reclamo/Tramite).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
  - cambios realizados:
    - Trámites: se elimina duplicación del nombre (queda una sola línea con el nombre y abajo `Nro: ...`).
    - Reclamos: se elimina prefijo `Reclamo:` y queda nombre del reclamo + `Nro: ...` abajo.
  - pendientes: validación visual final de campanita.
- tarea: Soportar múltiples solicitudes de cambio de datos en detalle de trámite y respetar tipo de campo.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
  - cambios realizados:
    - Trámite: se reemplazó lógica singular por lista de solicitudes pendientes (`_get_solicitudes_datos_pendientes`).
    - Se identifica la solicitud respondida por `metadata.solicitud_origen_id` para no ocultar/mezclar respuestas.
    - Cada solicitud pendiente ahora renderiza su propio formulario (con `solicitud_id`) y se procesa individualmente.
    - Si el campo dinámico pedido es de tipo `archivo`, el formulario muestra input file y el backend guarda archivo en `TramiteAdjunto` + actualiza valor dinámico.
    - Si no es archivo, mantiene input de texto.
    - Compatibilidad de plantilla con reclamos: se expone `solicitudes_datos_pendientes` también en contexto de reclamo.
  - decisiones o supuestos:
    - Para tipo `archivo`, se admite imagen o archivo genérico según lo que cargue el usuario.
  - pendientes:
    - Validar en UI del trámite `/portal-ciudadano/mis-solicitudes/tramite/7/` que aparezcan las 2 solicitudes pendientes y que cada una envíe su cambio correctamente.
- tarea: Ajuste visual en detalle de trámite (datos solicitados e imagen/archivo).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
  - cambios realizados:
    - Se renombró el bloque "Datos" a "Datos solicitados".
    - En campos dinámicos tipo `archivo` ya no se muestra el nombre del archivo.
    - Si el archivo parece imagen, se intenta mostrar preview; si falla carga, se oculta la imagen rota.
    - Para archivos no imagen se muestra "Archivo cargado".
  - pendientes: validación visual de la imagen en `/portal-ciudadano/mis-solicitudes/tramite/7/`.
- tarea: Estados internos de solicitudes de modificación para seguimiento de operador (trámites y reclamos).
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/tramites.py
    - configuracion/interfaces/web/views/reclamos.py
    - configuracion/interfaces/templates/configuracion/tramite_detail.html
    - configuracion/interfaces/templates/configuracion/reclamo_detail.html
  - cambios realizados:
    - Se agregó cálculo de estado interno derivado del historial:
      - `Sin solicitudes`
      - `Pendiente respuesta ciudadano`
      - `Respondida`
    - Se agregaron contadores para seguimiento: total, pendientes y respondidas.
    - Se muestra en el bloque principal de detalle de trámite y reclamo:
      - Estado solicitud de datos
      - Seguimiento solicitud de datos (pendientes/respondidas/total)
    - El matching de respuesta contempla `metadata.solicitud_origen_id` y fallback por fecha para compatibilidad con registros anteriores.
  - decisiones o supuestos:
    - No se creó nuevo campo/modelo; estado calculado en runtime para evitar migraciones y preservar datos actuales.
  - pendientes:
    - Validar con casos reales de múltiples solicitudes y respuestas históricas.
- tarea: Fix de arranque Django por SyntaxError en portal_ciudadano/views.py.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
  - cambios realizados:
    - Se corrigió string literal roto en `detalle_texto` dentro de `PortalCiudadanoTramiteDetalleSolicitudView.post`.
    - Quedó: `"\\n".join(detalle)`.
  - verificación:
    - `python -m py_compile portal_ciudadano/views.py` OK.
  - pendientes: volver a levantar contenedor/app para confirmar migraciones/boot.
- tarea: Incorporar estado interno de solicitud de datos en listados de trámites y reclamos + filtro.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/tramites.py
    - configuracion/interfaces/web/views/reclamos.py
    - configuracion/interfaces/templates/configuracion/tramite_list.html
    - configuracion/interfaces/templates/configuracion/reclamo_list.html
  - cambios realizados:
    - Listados: anotación por queryset de `ultima_solicitud_datos` y `ultima_respuesta_solicitud_datos`.
    - Se calcula y muestra columna `Solicitud de datos` con valores:
      - Sin solicitudes
      - Pendiente respuesta ciudadano
      - Respondida
    - Se agrega filtro `estado_solicitud_datos` en ambos listados.
    - Se preserva el filtro nuevo en links de paginación.
  - verificación:
    - `python -m py_compile` OK en ambas vistas.
  - pendientes:
    - Validación funcional en UI con datos reales.
- tarea: Mejorar UX de pedido de cambio de datos en detalle de trámite/reclamo.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/templates/configuracion/tramite_detail.html
    - configuracion/interfaces/templates/configuracion/reclamo_detail.html
  - cambios realizados:
    - Se agregó botón principal en resumen:
      - "Pedido de actualización de datos".
    - Los botoncitos por campo (`fa-file-pen`) ahora están ocultos por defecto.
    - Al activar el botón principal, se muestran los botoncitos para seleccionar campo.
    - Se puede desactivar con "Cancelar pedido de actualización".
    - Se mantuvo el comportamiento existente de modal y envío por campo.
  - pendientes:
    - Validación visual y de interacción en ambas pantallas de detalle.
- tarea: Nueva tab "Respuesta" en detalle de Trámites y Reclamos para respuesta del operador con texto formateable y archivos múltiples.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/tramites.py
    - configuracion/interfaces/web/views/reclamos.py
    - configuracion/interfaces/templates/configuracion/tramite_detail.html
    - configuracion/interfaces/templates/configuracion/reclamo_detail.html
  - cambios realizados:
    - Backend:
      - Nueva acción POST `respuesta_ciudadano` en ambos detalles.
      - Guarda comentario visible al ciudadano.
      - Permite múltiples archivos (`respuesta_adjuntos`) y crea adjuntos visibles al ciudadano.
      - Registra historial con acción `respuesta_operador_ciudadano` y metadata de trazabilidad.
    - Frontend:
      - Nueva tab `Respuesta` en Trámites y Reclamos.
      - Editor enriquecido básico (negrita, cursiva, lista, link) con `contenteditable`.
      - Campos ocultos `respuesta_html` y `respuesta_texto` para persistir contenido.
      - Input multiple file para adjuntar varios archivos.
  - verificación:
    - `python -m py_compile` OK para vistas de trámites y reclamos.
  - pendientes:
    - Validar visualmente el render HTML del comentario en portal ciudadano si se desea mostrar formato enriquecido en detalle/historial.
- tarea: Corregir toggle de pedido de actualización de datos en detalles de trámites/reclamos y mejorar estilo del botón.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/templates/configuracion/tramite_detail.html
    - configuracion/interfaces/templates/configuracion/reclamo_detail.html
  - cambios realizados:
    - El toggle ya no depende de clase `hidden`; ahora usa `style.display` para mostrar/ocultar botones de campo.
    - Se ocultaron botones de campo con `style="display:none;"` por defecto.
    - Botón principal se estilizó con look del template (`bg-arg-azul`, texto blanco) y se mantiene junto a "Resumen".
    - Se mantiene el texto dinámico del botón: activar/cancelar pedido.
  - pendientes:
    - Validación visual/interacción en ambas pantallas.
- tarea: Renombrar tab Respuesta a Finalizar (trámite/reclamo), mover al final y finalizar estado al enviar.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/tramites.py
    - configuracion/interfaces/web/views/reclamos.py
    - configuracion/interfaces/templates/configuracion/tramite_detail.html
    - configuracion/interfaces/templates/configuracion/reclamo_detail.html
  - cambios realizados:
    - Tabs:
      - `Respuesta` -> `Finalizar tramite` / `Finalizar reclamo`.
      - Se movió al final del set de tabs.
    - Botón submit:
      - `Enviar respuesta` -> `Enviar y finalizar tramite/reclamo`.
    - Backend:
      - Acción `respuesta_ciudadano` ahora cambia estado a uno final (`es_final=True`).
      - Trámite: usa estado final por municipio (fallback global), setea `fecha_finalizacion`.
      - Reclamo: usa estado final activo, setea `fecha_resolucion`.
      - Se registra historial con estado anterior/nuevo y metadata `finalizado=True`.
  - verificación:
    - `python -m py_compile` OK.
  - pendientes:
    - Validar funcionalmente en UI que al enviar desde tab Finalizar el estado cambie a final.
- tarea: Agregar icono de Seguimiento en header de Portal Ciudadano.
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/base_seccion.html
    - portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html
    - portal_ciudadano/templates/portal_ciudadano/mi_perfil.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/reclamos_confirmar.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_enviada.html
    - portal_ciudadano/templates/portal_ciudadano/tramites.html
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_detalle.html
    - portal_ciudadano/templates/portal_ciudadano/tramites_confirmar.html
  - cambios realizados:
    - Se agregó ícono `fa-rectangle-list` con enlace a `portal_ciudadano:mis_solicitudes`.
    - Ubicación: en header, a la izquierda del ícono de Turnos.
- tarea: Diferenciar colores de estados en Portal Ciudadano > Mis solicitudes.
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/mis_solicitudes.html
  - cambios realizados:
    - Se agregó helper backend `_estado_badge_class` para mapear estado a tipo visual: ok/info/warn/danger/neutral.
    - Se asigna `estado_badge_class` a trámites y reclamos en `PortalCiudadanoMisSolicitudesView`.
    - Se agregaron clases CSS de color para badges y se aplican en ambas tablas.
  - resultado:
    - Los estados ya no quedan todos rojos; varían según el tipo de estado.
- tarea: Mostrar imágenes en Datos solicitados y thumbnails en Adjuntos (detalle solicitud portal ciudadano).
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
  - cambios realizados:
    - Backend (trámite y reclamo): se prepara `valor_preview_url` para campos dinámicos tipo archivo, resolviendo URL real desde adjuntos cuando el valor guardado es solo nombre de archivo.
    - Template: en "Datos solicitados" se usa `valor_preview_url` para mostrar imagen cuando aplica.
    - Template: en "Adjuntos" se renderiza thumbnail para archivos de imagen.
- tarea: Unificar solicitud de modificación de datos en detalle de reclamo con el flujo de trámite (portal ciudadano).
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
    - docs/tmp/WORKLOG.md
  - cambios realizados:
    - Reclamo detalle: se reemplazó lógica singular por lista de solicitudes pendientes (`_get_solicitudes_datos_pendientes`) con vínculo por `metadata.solicitud_origen_id`.
    - Reclamo detalle: se agregó extracción de `campo_objetivo` y resolución de `input_type` por solicitud (`text`/`file`) igual que en trámites.
    - POST de reclamo: ahora responde una solicitud puntual por `solicitud_id` y actualiza solo el campo pedido (base, dinámico o adjunto).
    - Historial de reclamo: la respuesta del ciudadano se guarda con `solicitud_origen_id`, `campos_actualizados` y `campos_valores` para trazabilidad.
    - Template `solicitud_detalle.html`: se eliminó el formulario especial viejo de reclamos y se unificó con el bloque de "Nuevo valor" por solicitud.
  - verificación:
    - `python -m py_compile portal_ciudadano/views.py` OK.
  - pendientes:
    - Validación visual en `/portal-ciudadano/mis-solicitudes/reclamo/11/` con solicitudes múltiples y casos de archivo/imagen.
- tarea: Homologar historial de detalle de reclamo al mismo formato visual/funcional de detalle de trámite.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/reclamos.py
    - configuracion/interfaces/templates/configuracion/reclamo_detail.html
    - docs/tmp/WORKLOG.md
  - cambios realizados:
    - Vista de reclamo: se agregaron `accion_label`, `comentario_label` y `solicitud_datos_estado` para historial.
    - Vista de reclamo: normalización de `campos_valores` con fallback por `campos_actualizados`, igual criterio que trámites.
    - Template de reclamo: bloque `Historial completo` alineado al formato de trámites (Acción, Estado solicitud cuando aplica, Detalle y render de campos/archivos).
    - Se removieron del bloque de historial de reclamo las líneas extra de estado/área/asignado/visibilidad para que quede consistente con trámites.
  - verificación:
    - `python -m py_compile configuracion/interfaces/web/views/reclamos.py` OK.
  - pendientes:
    - Validación visual final en `/configuracion/reclamos/listado/11/`.
- tarea: Agregar badges de colores para estados en detalle de reclamos y detalle de trámites.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/reclamos.py
    - configuracion/interfaces/web/views/tramites.py
    - configuracion/interfaces/templates/configuracion/reclamo_detail.html
    - configuracion/interfaces/templates/configuracion/tramite_detail.html
    - docs/tmp/WORKLOG.md
  - cambios realizados:
    - Se incorporó mapeo de estado -> clase de badge en ambas vistas de detalle.
    - Se expone `estado_badge_class` para el estado actual.
    - En historiales de estados se agregaron clases para `estado_anterior` y `estado_nuevo`.
    - Se actualizó el render de estado en templates (encabezado de detalle, estado actual en tab Estados e historial de estados) para mostrarlos como badges coloreados.
  - verificación:
    - `python -m py_compile configuracion/interfaces/web/views/reclamos.py configuracion/interfaces/web/views/tramites.py` OK.
  - pendientes:
    - Validación visual en ambas pantallas de detalle.
- tarea: Aplicar badges de colores de estado en listados de Trámites y Reclamos.
  - archivos creados: ninguno
  - archivos modificados:
    - configuracion/interfaces/web/views/tramites.py
    - configuracion/interfaces/web/views/reclamos.py
    - configuracion/interfaces/templates/configuracion/tramite_list.html
    - configuracion/interfaces/templates/configuracion/reclamo_list.html
    - docs/tmp/WORKLOG.md
  - cambios realizados:
    - En ambos listados se agregó mapeo de estado a clase visual de badge (ok/info/warn/danger/neutral).
    - Se asignó `estado_badge_class` por fila en `get_context_data`.
    - Se reemplazó el badge gris fijo en las tablas por el badge dinámico por estado.
  - verificación:
    - `python -m py_compile configuracion/interfaces/web/views/tramites.py configuracion/interfaces/web/views/reclamos.py` OK.
  - pendientes:
    - Validación visual en `/configuracion/tramites/listado/` y `/configuracion/reclamos/listado/`.
- tarea: Agregar card de finalización en detalle ciudadano (reclamo y trámite) con observaciones y adjuntos descargables.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - portal_ciudadano/templates/portal_ciudadano/solicitud_detalle.html
    - docs/tmp/WORKLOG.md
  - cambios realizados:
    - Se incorporó `cierre_info` en contexto para reclamo y trámite, tomando la última acción `respuesta_operador_ciudadano` visible al ciudadano.
    - Observaciones: se prioriza comentario asociado por `metadata.comentario_id`, con fallback al comentario del historial.
    - Adjuntos de cierre: se toman según `metadata.adjuntos_nuevos` de la respuesta de finalización.
    - UI: nueva card `Finalización` en el detalle ciudadano con:
      - fecha
      - observaciones
      - adjuntos en grilla
      - thumbnails de imagen más grandes
      - iconos para archivos no imagen
      - botón de descarga por adjunto.
  - verificación:
    - `python -m py_compile portal_ciudadano/views.py` OK.
  - pendientes:
    - Validación visual en `/portal-ciudadano/mis-solicitudes/reclamo/11/` y detalle equivalente de trámite con caso finalizado y adjuntos.
- tarea: Notificar en campanita cuando trámite o reclamo pasa a finalizado.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/views.py
    - docs/tmp/WORKLOG.md
  - cambios realizados:
    - Se agregaron notificaciones portal para historial `respuesta_operador_ciudadano` (trámite/reclamo finalizado).
    - Las notificaciones de finalización se muestran con link directo al detalle correspondiente.
    - Se evita duplicar por solicitud: solo la última finalización por trámite/reclamo en el listado de notificaciones.
    - Se amplió el cálculo del contador no visto para incluir finalizaciones.
    - Se amplió el endpoint de marcar leídas para incluir tokens de finalización (`fr:` y `ft:`).
  - verificación:
    - `python -m py_compile portal_ciudadano/views.py` OK.
  - pendientes:
    - Validación visual en campanita con casos reales de finalización de trámite y reclamo.
- tarea: Corregir pantallas en blanco de sección Mi Datos/Consultas en Portal Ciudadano.
  - archivos creados: ninguno
  - archivos modificados:
    - portal_ciudadano/templates/portal_ciudadano/mis_datos.html
    - portal_ciudadano/templates/portal_ciudadano/cambio_password.html
    - portal_ciudadano/templates/portal_ciudadano/cambio_email.html
    - portal_ciudadano/templates/portal_ciudadano/mis_consultas.html
    - portal_ciudadano/templates/portal_ciudadano/nueva_consulta.html
    - portal_ciudadano/templates/portal_ciudadano/consulta_detalle.html
    - docs/tmp/WORKLOG.md
  - cambios realizados:
    - Se reemplazó el bloque incorrecto `{% block seccion_content %}` por `{% block content %}` para coincidir con `base_seccion.html`.
    - Con esto, las vistas vuelven a renderizar su contenido en lugar de quedar vacías.
  - pendientes:
    - Validación visual rápida de `/portal-ciudadano/mis-datos/` y sección de consultas.

## 2026-05-11 - Fix NameError registro portal ciudadano
- Tarea: resolver `NameError: RegistroStep1Form is not defined` en `/portal-ciudadano/registro/`.
- Archivos modificados:
  - `portal_ciudadano/views.py`
  - `docs/tmp/WORKLOG.md`
- Cambios realizados:
  - Agregué `RegistroStep1Form` y `RegistroStep2Form` al import local desde `.forms` en `portal_ciudadano/views.py`.
- Verificación:
  - Import de `PortalCiudadanoRegistroStep1View`, `RegistroStep1Form` y `RegistroStep2Form` OK.
  - `Client(HTTP_HOST='localhost').get('/portal-ciudadano/registro/')` devuelve HTTP 200.
- Pendientes:
  - Ninguno para este error puntual.

## 2026-05-11 - Registro portal ciudadano visual rama actual
- Tarea: hacer que `/portal-ciudadano/registro/` vuelva a verse como portal ciudadano en la rama actual, sin tocar branding.
- Archivos modificados:
  - `portal_ciudadano/templates/portal_ciudadano/registro_step1.html`
  - `portal_ciudadano/templates/portal_ciudadano/registro_step2.html`
  - `docs/tmp/WORKLOG.md`
- Cambios realizados:
  - Reemplacé los templates standalone viejos por una estructura visual alineada al login del portal de esta rama.
  - Mantengo colores, huella, header, hero, panel, card y footer propios del portal ciudadano actual.
  - Corregí textos visibles con acentos en ambos pasos.
  - No modifiqué branding ni configuración de marca.
- Verificación:
  - `get_template` OK para `registro_step1.html` y `registro_step2.html`.
  - `Client(HTTP_HOST='localhost').get('/portal-ciudadano/registro/')` devuelve HTTP 200.
  - HTML renderizado contiene `Crear cuenta`, `Verificá tu identidad` y `register-wrap`.
  - No hay secuencias mojibake en ambos templates.
- Pendientes:
  - Revisar visualmente en navegador si se quiere ajustar tamaños/espaciado fino.
