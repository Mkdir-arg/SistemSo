# Worklog temporal

## 2026-05-05 - Descolapsar cuerpo del popup de configuración

## 2026-05-05 - Rediseñar header del Editor de Flujo

**Tarea:** Llevar la información del header a una disposición horizontal más compacta y agrandar la altura útil del área de diseño del flujo.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/templates/flujos/editor.html`

**Cambios realizados:**
- Se rediseñó el hero superior como una banda horizontal con título a la izquierda y chips/métricas en línea a la derecha.
- Se compactó el encabezado interno de “Diseño del flujo” para que ocupe menos alto visible.
- Se convirtió la nota operativa en una franja más fina y se amplió el alto útil del canvas principal.

**Decisiones o supuestos:**
- El problema principal era de proporción vertical: demasiada altura consumida por textos y badges antes del canvas.
- Se preservó toda la información relevante, pero redistribuida a lo ancho para mejorar lectura y viewport útil.

**Pendientes:**
- Confirmar visualmente el nuevo balance entre header y canvas en desktop y tablet.

**Tarea:** Hacer visible el contenido del popup de configuración cuando hoy solo aparece el encabezado del modal.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/app.css`

**Cambios realizados:**
- Se le dio altura efectiva al diálogo del modal para que el body tenga espacio real y no quede colapsado.
- Se convirtió el body del modal en contenedor flex y el panel modal en hijo flex scrolleable.
- Se hizo que el bloque interno de propiedades también participe del alto disponible del modal.

**Decisiones o supuestos:**
- El síntoma visible era “solo header, sin contenido”, consistente con un colapso del body del modal más que con falta de datos del nodo.
- Se mantuvo el cambio en CSS porque el header ya probaba que el nodo seleccionado sí llegaba correctamente al popup.

**Pendientes:**
- Confirmar visualmente que el popup vuelve a mostrar el formulario completo de `Derivación` y que el scroll sigue funcionando en contenido largo.

## 2026-05-05 - Compactar encabezado del Editor de Flujo

**Tarea:** Reducir la sección superior del editor para darle más espacio útil visible al área de diseño del flujo.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/templates/flujos/editor.html`

**Cambios realizados:**
- Se eliminó la columna lateral de ayuda y el bloque grande de tarjetas de resumen del hero del editor.
- Se condensó la información relevante en chips y métricas inline más compactas.
- Se aumentó el alto útil del shell del editor aprovechando la reducción del encabezado superior.

**Decisiones o supuestos:**
- Se priorizó superficie visible para el canvas por encima de contenido explicativo redundante.
- Se mantuvieron solo los datos operativos mínimos: código, versión, estado, cantidad de versiones e instancias activas.

**Pendientes:**
- Si todavía querés más foco en el canvas, el siguiente paso natural es compactar también el header interno de `Diseño del flujo`.

## 2026-05-05 - Habilitar scroll real en popup de Configuración de Derivación

**Tarea:** Corregir el popup de configuración para que el contenido largo no quede cortado y pueda desplazarse dentro del modal.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/app.css`
- `static/flujos/dist/assets/index.css`

**Cambios realizados:**
- Se convirtió `flow-config-modal__body` en un flex item real con `flex: 1 1 0` para que ocupe el alto restante del diálogo.
- Se hizo que `flow-modal-panel` tome `height: 100%` y `min-height: 0` para que su `overflow-y: auto` opere sobre un alto acotado.
- Se replicó el ajuste en el bundle estático servido por Django mediante `npm run build` para que impacte en la vista real.

**Decisiones o supuestos:**
- El corte no estaba en el contenido del panel sino en la relación de alturas entre el body del modal y el panel scrolleable.
- Se evitó tocar JSX o estructura del modal porque el problema era estrictamente de layout CSS.

**Pendientes:**
- Verificar visualmente el caso de contenido muy largo dentro de `Pantalla` y `Operativa` para confirmar que el scroll aparece en todo el recorrido.

## 2026-05-05 - Agrandar un poco más el Canvas principal

**Tarea:** Darle más alto visible al `Canvas principal` del editor de flujo sin reabrir el problema del layout roto.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/templates/flujos/editor.html`

**Cambios realizados:**
- Se aumentó la altura mínima del `editor-root-shell` en desktop para darle más espacio útil al canvas.
- También se subió el `clamp(...)` máximo/intermedio para que el editor gane alto visible en resoluciones amplias.
- Se ajustó la altura responsive para que en pantallas menores no quede demasiado comprimido.

**Decisiones o supuestos:**
- Se mantuvo el cambio acotado al shell del editor porque el pedido fue agrandar el canvas, no remaquetar toolbar o paneles.
- Se evitó tocar React Flow o el layout interno del canvas para no alterar zoom, centrado o interacción.

**Pendientes:**
- Si todavía lo querés más alto, el siguiente ajuste natural es subir solo el `max` del `clamp(...)` en desktop.

## 2026-05-05 - Reducir espacio blanco del editor de flujo por altura excesiva

**Tarea:** Corregir el espacio blanco visible en `/flujos/programas/<id>/flujo/editar/` ajustando la altura del shell del editor.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/templates/flujos/editor.html`

**Cambios realizados:**
- Se redujo la altura mínima del contenedor `editor-root-shell`, que estaba fijada demasiado alta para pantallas como la del usuario.
- La altura del editor pasó a usar `clamp(...)` para mantener un canvas amplio sin inflar la vista con blanco innecesario.
- También se compactó la altura responsive en pantallas menores a `992px`.

**Decisiones o supuestos:**
- Se corrigió en el template Django porque el hueco venía del contenedor general del editor, no del render interno de React Flow.
- Se mantuvo un alto suficiente para trabajar cómodo con nodos y conexiones sin volver el editor demasiado corto.

**Pendientes:**
- Si después de usarlo con flujos más grandes todavía se siente alto o bajo, ajustar la cota máxima del `clamp(...)` según uso real.

## 2026-05-05 - Quitar encabezado heredado roto y subir el editor

**Tarea:** Corregir el espacio blanco superior del editor de flujo que seguía apareciendo por la herencia de `includes/main.html`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/templates/flujos/editor.html`

**Cambios realizados:**
- Se anuló correctamente el bloque `titulo-pagina` en vez de renderizar texto suelto, eliminando el `Editor de Flujo` colgado arriba del contenido.
- Se forzó a cero el padding superior heredado de `app-content` y `container-fluid` solo para esta vista.
- Se dejó el `editor-page` apenas más arriba para que el hero del editor arranque pegado al contenido útil.

**Decisiones o supuestos:**
- La pantalla ya tiene su propio encabezado visual dentro del hero, por lo que el header heredado del layout era duplicado y visualmente incorrecto.
- El ajuste se acotó al template del editor para no tocar el espaciado global del backoffice.

**Pendientes:**
- Si todavía queda demasiado aire arriba en alguna resolución puntual, medir en navegador autenticado y ajustar solo el margen superior local del `editor-page`.

## 2026-05-05 - Neutralizar layout legacy duplicado en el editor de flujo

**Tarea:** Eliminar el corrimiento y espacio extra que seguían viniendo del `app-main` legacy sobre una base nueva con sidebar/layout propio.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/templates/flujos/editor.html`

**Cambios realizados:**
- Se anuló localmente `margin-top`, `margin-left` y `min-height` de `.app-main` para esta vista.
- Se compactó a cero el padding heredado del `app-content`, del `container-fluid` interno y del wrapper superior `main.py-10`.
- Se dejó `editor-page` sin margen superior adicional para evitar acumulación de aire arriba.

**Decisiones o supuestos:**
- El problema no era solo el header vacío: esta pantalla estaba recibiendo espaciado de un layout legacy además del layout actual basado en Tailwind/sidebar.
- La neutralización se aplicó solo en el template del editor para no romper otras pantallas que todavía dependan del comportamiento viejo.

**Pendientes:**
- Verificar visualmente si además conviene sacar `py-10` del wrapper superior en una iteración posterior; por ahora se evitó tocar el layout global.

## 2026-05-05 - Integrar etapas del flujo dentro del panel operativo

**Tarea:** Reubicar las solapas generadas desde el flujo publicado dentro del `Panel operativo del programa`, dejando `Dashboard` primero y eliminando tabs legacy que ya no van.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `legajos/interfaces/templates/legajos/programas/programa_detail.html`

**Cambios realizados:**
- Se eliminó el bloque superior separado de `Flujo activo publicado` para que la navegación viva dentro del panel operativo principal.
- La barra de tabs ahora deja `Dashboard` fijo como primera solapa, agrega a continuación las etapas configuradas del flujo publicado y conserva `Indicadores` como vista histórica.
- Se removieron las tabs legacy de `Derivaciones`, `Acompañamientos` e `Instituciones`, junto con sus paneles asociados.
- La metadata de versión publicada e instancias activas del flujo se movió al encabezado del panel operativo.

**Decisiones o supuestos:**
- Se mantuvo `Indicadores` porque sigue representando lectura histórica y no fue señalado para eliminación.
- Las etapas del flujo se montan como tabs del mismo sistema existente para evitar duplicar navegación y JavaScript.

**Pendientes:**
- Si también hay que aplicar esta misma convención al detalle especial de Ñachec, replicarlo en su template específico.

## 2026-05-05 - Compactar proporción del modal de Pantalla en el editor de flujos

**Tarea:** Corregir la proporción del popup de configuración en la pestaña `Pantalla` para que no obligue a usar zoom extremo del navegador.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/app.css`
- `frontend/flow-editor/src/components/PropertiesPanel.jsx`
- `frontend/flow-editor/src/components/ScreenPreview.jsx`
- `static/flujos/dist/*`

**Cambios realizados:**
- El modal de configuración ahora usa más ancho útil del viewport y reduce padding interno cuando se abre en modo popup.
- La pestaña `Pantalla` usa una densidad más compacta en labels, inputs, cards y acciones cuando se edita dentro del modal.
- La vista previa viva se renderiza en modo compacto dentro del popup para que entre mejor sin depender del zoom del navegador.
- Se reinstalaron dependencias de `frontend/flow-editor` y se recompiló el bundle con Vite hacia `static/flujos/dist`.

**Decisiones o supuestos:**
- El ajuste se aplicó solo al modo modal para no achicar innecesariamente el panel lateral normal del editor.
- Se priorizó mejorar proporción y lectura general antes que rediseñar la estructura completa de la pestaña `Pantalla`.

**Pendientes:**
- Si todavía queda grande en ciertos monitores o escalas DPI, evaluar una segunda iteración con layout en dos columnas para la configuración y una preview colapsable.

## 2026-05-05 - Exponer etapas del flujo activo en detalle de programa

**Tarea:** Hacer visible dentro de Programas la versión publicada del flujo activo, mostrando sus nodos como solapas internas del detalle.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `legajos/interfaces/web/views/programas.py`
- `legajos/interfaces/templates/legajos/programas/programa_detail.html`

**Cambios realizados:**
- La vista `ProgramaDetailView` ahora arma un contexto `flujo_activo` desde la versión publicada del programa, ordenando nodos por recorrido y agrupando instancias activas y tareas pendientes por etapa.
- Se agregó una navegación nueva de etapas en `programa_detail.html`, donde cada solapa sale de los nodos del flujo publicado y muestra tipo, carga operativa y resumen de la etapa.
- Se dejó el panel operativo legacy debajo de esa capa para no perder derivaciones, acompañamientos, instituciones e indicadores existentes.
- Se validó con `py_compile` sobre la vista y con carga real de la plantilla vía `manage.py shell` dentro del contenedor `app`.

**Decisiones o supuestos:**
- Se interpretó “las solapas son los nodos del flujo” como etapas operativas visibles dentro del detalle del programa, sin reemplazar todavía la operatoria histórica.
- Se excluyó el nodo `inicio` de las solapas porque no representa una etapa útil de trabajo para el operador.

**Pendientes:**
- Si producto quiere reemplazo total y no convivencia, convertir también el panel operativo legacy en vistas derivadas del flujo o esconderlo cuando exista flujo publicado.

## 2026-05-05 - Corregir SyntaxError en formulario de derivación

**Tarea:** Reparar el `SyntaxError` introducido en el queryset de programas destino del formulario de derivación.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `legajos/interfaces/web/forms/derivacion.py`

**Cambios realizados:**
- Se envolvió la cadena del queryset en paréntesis para que `.distinct()` no quedara en una línea inválida para Python.
- Se validó el archivo con `python -m py_compile` dentro del contenedor `app`.

**Decisiones o supuestos:**
- Se mantuvo intacto el filtro funcional de programas activos con flujo publicado; el ajuste fue puramente sintáctico.

**Pendientes:**
- Ninguno para este fix puntual.

## 2026-05-05 - Filtrar programas destino por flujo publicado

**Tarea:** Ajustar la derivación de ciudadanos para que el selector de programa destino solo ofrezca destinos activos con flujo publicado.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `legajos/interfaces/web/forms/derivacion.py`
- `legajos/interfaces/web/templates/legajos/derivar_programa.html`

**Cambios realizados:**
- El queryset de `institucion_programa` ahora filtra por relación activa, programa activo y existencia de una versión de flujo `PUBLICADA`.
- Se agregó una ayuda visual en el formulario para aclarar que solo se muestran programas activos con flujo publicado.

**Decisiones o supuestos:**
- Se tomó `flujo publicado` como criterio operativo para habilitar un programa destino, porque en este circuito el flujo publicado es lo que realmente permite recibir y procesar derivaciones.
- Se mantuvo la selección por `InstitucionPrograma` para no romper el contrato actual de derivación institución-programa.

**Pendientes:**
- Si el producto necesita distinguir entre programas activos sin flujo y programas con flujo borrador, sumar estados o badges más explícitos en el selector.

## 2026-05-05 - Mover la configuración de nodos a un modal

**Tarea:** Sacar el panel fijo de configuración del costado del canvas y abrir la edición del nodo o transición en un popup desde un botón contextual.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/App.jsx`
- `frontend/flow-editor/src/components/PropertiesPanel.jsx`
- `frontend/flow-editor/src/app.css`
- `static/flujos/dist/*`

**Cambios realizados:**
- El layout del editor dejó de reservar una tercera columna fija para configuración al costado del canvas.
- Cuando hay un nodo o transición seleccionado, el toolbar del canvas ahora muestra un botón `Configurar nodo` o `Configurar transición`.
- La configuración existente se reutiliza dentro de un modal con scroll propio, sin duplicar la lógica del inspector.
- El modal ahora divide la configuración del nodo por solapas temáticas (`General`, `Operativa`, `Pantalla`, `Automatización`) para bajar el ruido visual cuando el paso tiene mucha configuración.
- El modal se puede cerrar desde el botón de cierre, tocando el backdrop o con `Escape`.
- Se recompiló `static/flujos/dist` con Vite y se volvió a limpiar `frontend/flow-editor/node_modules`.

**Decisiones o supuestos:**
- Se mantuvo el `PropertiesPanel` actual como fuente única de edición para no abrir divergencias entre un inspector lateral y un popup.
- El pedido se interpretó como sacar la configuración fija del costado del canvas, no como eliminar la capacidad de configurar transiciones.

**Pendientes:**
- Si hace falta una interacción todavía más directa, sumar un acceso rápido flotante sobre el nodo seleccionado, apertura automática del modal al doble click o tabs secundarias dentro del editor de pantalla.

## 2026-05-05 - Ajustar corrimiento inicial del canvas

**Tarea:** Corregir el encuadre inicial del editor para que el diagrama no quede tan corrido hacia abajo y a la derecha al abrir el flujo.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/App.jsx`
- `static/flujos/dist/*`

**Cambios realizados:**
- Se redujo el padding del `fitView` inicial de React Flow para que el diagrama arranque más cerca del origen visible del canvas.
- Se ajustaron las posiciones por defecto y de fallback de los nodos para evitar que los flujos nuevos o incompletos queden demasiado corridos hacia abajo y a la derecha.
- Se recompiló `static/flujos/dist` con Vite y se volvió a limpiar `frontend/flow-editor/node_modules`.

**Decisiones o supuestos:**
- Se atacó primero el encuadre inicial del viewport y los defaults del editor, porque era la corrección más chica y con menos riesgo sobre el resto del configurador.
- No se reescribieron posiciones ya guardadas en base; este ajuste mejora la apertura del canvas y los nodos creados con defaults del editor.

**Pendientes:**
- Si todavía aparece corrido en flujos viejos con posiciones persistidas raras, agregar una normalización opcional de coordenadas al cargar la definición.

## 2026-05-05 - Agregar colapso de secciones y campos al inspector

**Tarea:** Reducir el ruido del configurador de pantallas permitiendo colapsar y expandir secciones y campos dentro del inspector React del editor de flujos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/components/PropertiesPanel.jsx`
- `static/flujos/dist/*`

**Cambios realizados:**
- El inspector ahora mantiene estado local de colapso por nodo, sección y campo sin tocar la definición persistida del flujo.
- Cada sección muestra un encabezado compacto con cantidad de bloques y acción `Expandir/Colapsar`.
- Cada campo muestra su etiqueta, tipo y acción `Expandir/Colapsar`, manteniendo visibles las acciones rápidas de mover o duplicar.
- El inspector ahora suma acciones globales `Expandir todo / Colapsar todo` para abrir o cerrar de una vez todas las secciones y campos del nodo actual.
- La mejora reduce el ruido visual cuando la pantalla tiene muchas secciones, tablas o bloques de resumen dentro del mismo nodo.
- Se recompiló `static/flujos/dist` con Vite y se volvió a limpiar `frontend/flow-editor/node_modules`.

**Decisiones o supuestos:**
- El estado de colapso es puramente local del inspector; no forma parte del contrato `config.ui` ni se guarda en backend.
- Se priorizó colapso simple sobre drag & drop interno para cerrar un corte chico y usable sin abrir más complejidad de interacción.

**Pendientes:**
- Si sigue haciendo falta más velocidad de armado, sumar drag & drop interno dentro de una sección o acciones masivas por tipo de bloque.

## 2026-05-05 - Agregar bloque summary al configurador de pantallas

**Tarea:** Extender las pantallas declarativas del creador de flujos con un bloque visual `summary` para mostrar indicadores o tarjetas de contexto dentro de una tarea humana.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/dto.py`
- `flujos/interfaces/web/forms.py`
- `flujos/interfaces/templates/flujos/backoffice/tarea_detalle.html`
- `flujos/tests/test_flow_definition_form.py`
- `flujos/tests/test_backoffice_tasks.py`
- `frontend/flow-editor/src/components/PropertiesPanel.jsx`
- `frontend/flow-editor/src/components/ScreenPreview.jsx`
- `frontend/flow-editor/src/components/NodePanel.jsx`
- `frontend/flow-editor/src/utils/validators.js`
- `static/flujos/dist/*`

**Cambios realizados:**
- El contrato `config.ui` ahora acepta el bloque declarativo `summary` con `items` y `empty_message`.
- El renderer web de tareas muestra ese bloque como tarjetas/resumen visual dentro del detalle backoffice.
- El snapshot runtime reutiliza la interpolación existente, por lo que los placeholders dentro de `summary.items[].value` quedan resueltos al crear la tarea.
- El inspector React permite crear, editar y borrar items del resumen visual, además de agregarlo rápido desde una sección.
- La vista previa viva del editor ahora renderiza el bloque `summary` como grilla de métricas/cards.
- El editor dejó de sugerir bloques de display (`info`, `summary`, `table`) como campos evaluables para condiciones de transición.
- La plantilla `Pantalla + resumen` del panel de nodos ahora incluye también un bloque `summary` listo para usar.
- Se ejecutaron los tests focales `flujos.tests.test_flow_definition_form` y `flujos.tests.test_backoffice_tasks` dentro del contenedor `sistemso-app-1`: 50 tests OK.
- Se recompiló `static/flujos/dist` con Vite y se volvió a limpiar `frontend/flow-editor/node_modules`.

**Decisiones o supuestos:**
- `summary` se implementó como bloque de display, no como campo capturable; por eso no participa en condiciones ni en payload de respuesta.
- El resumen visual usa items `label/value` simples para mantener el contrato chico y versionable sin introducir layouts anidados todavía.

**Pendientes:**
- Si el producto lo necesita, sumar variantes visuales del resumen (`metric`, `card`, badges, tendencia) sin romper este contrato base.
- Evaluar drag & drop interno o colapso de secciones para seguir mejorando la composición en el inspector.

## 2026-05-05 - Agregar acciones automáticas al creador de flujos

**Tarea:** Extender el motor y el editor para que el flujo no solo arme pantallas humanas sino también acciones automáticas ejecutables dentro del mismo contrato versionado.

**Archivos creados:**
- `flujos/infrastructure/runtime_actions.py`
- `frontend/flow-editor/src/components/nodes/AccionEmailNode.jsx`
- `frontend/flow-editor/src/components/nodes/AccionHttpNode.jsx`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/dto.py`
- `flujos/runtime.py`
- `flujos/tests/test_flow_definition_form.py`
- `flujos/tests/test_runtime_action_tasks.py`
- `frontend/flow-editor/src/App.jsx`
- `frontend/flow-editor/src/app.css`
- `frontend/flow-editor/src/components/NodePanel.jsx`
- `frontend/flow-editor/src/components/PropertiesPanel.jsx`
- `frontend/flow-editor/src/utils/validators.js`

**Cambios realizados:**
- Se agregaron dos tipos de nodo nuevos al contrato del flujo: `accion_email` y `accion_http`.
- El contrato ahora usa `schema_version = 4` cuando el flujo incluye acciones automáticas y valida la configuración mínima de email y HTTP en backend.
- El runtime ahora resuelve paths anidados en condiciones, ejecuta acciones automáticas al entrar al nodo y deja sus resultados en `instancia.datos.acciones.<node_id>`.
- Se reutilizó `send_mail` de Django y `requests` ya presente en el repositorio para no abrir dependencias nuevas.
- El editor React ahora permite arrastrar, visualizar y configurar acciones email y HTTP desde el mismo panel lateral del canvas.
- El validador frontend bloquea publicaciones con acciones automáticas incompletas o inconsistentes.
- Se agregaron tests unitarios para contrato v4 y smokes de runtime para email y HTTP.
- Se regeneró `static/flujos/dist` con Vite para publicar los cambios del editor y luego se volvió a limpiar `frontend/flow-editor/node_modules`.
- El inspector de transiciones ahora permite configurar condiciones desde cualquier nodo origen, con sugerencias tipadas para resultados de acciones automáticas y campos runtime del paso anterior.
- El contrato de pantallas declarativas ahora soporta bloques `info` y `table`, con placeholders resueltos al crear la tarea para mezclar formulario y vista dentro del mismo nodo.
- La biblioteca del editor suma una plantilla `Pantalla + resumen` para crear más rápido nodos con contexto visible y captura operativa en una sola pantalla.
- El editor ahora muestra vista previa en vivo de la pantalla, soporta layout de dos columnas y descripciones por sección para acercar el configurador a una experiencia final de armado.
- Se recompiló `static/flujos/dist` con la preview viva del configurador y luego se volvió a limpiar `frontend/flow-editor/node_modules`.
- El inspector del configurador ahora permite subir, bajar y duplicar secciones y campos, para componer pantallas operativas sin rehacer bloques manualmente.
- Cada sección ahora ofrece quick-add de `campo`, `bloque info` y `tabla`, acelerando el armado de pantallas mixtas desde el panel lateral.

**Decisiones o supuestos:**
- Este corte no implementa todavía scheduler ni delays reales; las acciones automáticas iniciales son sincrónicas y encadenan el flujo en el mismo avance.
- Los resultados de las acciones se guardan bajo `acciones.<node_id>` para evitar colisiones con datos de formularios humanos.
- Las plantillas de acciones soportan interpolación simple con `{{ campo }}`, `{{ ciudadano.email }}` y metadata básica del caso.

**Pendientes:**
- Sumar más tipos de acción automática si el producto lo requiere: `delay`, `webhook firmado`, `notificacion interna`, `integraciones específicas`.
- Agregar un builder visual más fuerte para reglas complejas (`in`, múltiples comparaciones, grupos AND/OR) sin depender de edición manual de JSON o texto.
- Extender el mismo enfoque a bloques más ricos de pantalla (`summary`, grillas dinámicas, repetidores) para acercarse a tablas y vistas operativas más complejas.
- Si sigue haciendo falta una experiencia más cerrada de maquetación, sumar drag & drop interno o colapso de secciones dentro del inspector.

## 2026-05-05 - Llevar config.ui al editor visual de flujos

**Tarea:** Extender el editor React para crear y editar nodos `accion_humana` con pantalla declarativa v3 (`config.ui`), preservando compatibilidad con formularios tipados legacy.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/App.jsx`
- `frontend/flow-editor/src/components/NodePanel.jsx`
- `frontend/flow-editor/src/components/PropertiesPanel.jsx`
- `frontend/flow-editor/src/utils/validators.js`

**Cambios realizados:**
- El editor ahora serializa y reconstruye `actor`, `surface` y `config.ui` en nodos `accion_humana`.
- `flowToDefinicion` emite `schema_version = 3` cuando el flujo usa contrato declarativo v3.
- Se agrego una plantilla nueva de biblioteca para `Pantalla`, ya precargada con `actor`, `surface` y una UI declarativa base.
- El inspector derecho ahora permite alternar entre formulario tipado legacy y pantalla declarativa v3, y editar secciones, campos y opciones basicas.
- El validador frontend ahora bloquea publicaciones con pantallas declarativas incompletas o inconsistentes.

**Decisiones o supuestos:**
- El editor mantiene ambos contratos (`config.formulario` y `config.ui`) pero cada nodo usa uno u otro, no ambos a la vez.
- En este corte el editor declarativo solo soporta `ui.type = form`, `surface = backoffice` y `actor.mode = group`.
- Las validaciones frontend siguen el mismo recorte pragmático del backend, sin abrir todavía portal ni móvil.

**Pendientes:**
- Recompilar el bundle servido por Django y verificar que el editor renderice correctamente el nuevo inspector.
- Mejorar la presentación visual de campos/sections del editor declarativo para reducir ruido en el panel lateral.

## 2026-05-05 - Empezar Fase 2 de pantallas declarativas en tareas de flujo

**Tarea:** Extender la operatoria del backoffice para que un nodo `accion_humana` con `config.ui.type = form` deje snapshot en la tarea y pueda renderizarse/resolverse desde el detalle.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/runtime.py`
- `flujos/infrastructure/selectors.py`
- `flujos/interfaces/web/forms.py`
- `flujos/interfaces/templates/flujos/backoffice/tarea_detalle.html`
- `flujos/tests/test_backoffice_tasks.py`

**Cambios realizados:**
- El runtime ahora guarda snapshot de `actor`, `surface` y `ui_schema` al crear `TareaFlujo`.
- Al resolver una tarea humana, la tarea persistida guarda `response` y `response_meta` junto con el cierre.
- El selector de detalle ahora reconoce una pantalla declarativa `ui_form` antes de caer en formularios tipados legacy.
- Se agrego un formulario Django dinamico para renderizar pantallas declarativas simples desde metadata.
- El detalle web ya muestra secciones y campos de una pantalla `form` declarada en el flujo.
- Se agregaron tests de snapshot, API de detalle y resolucion web para un flujo `schema_version = 3`.

**Decisiones o supuestos:**
- El primer render declarativo soporta un set minimo de widgets y sigue restringido a backoffice.
- Se mantuvo compatibilidad con `config.formulario`; `config.ui` tiene prioridad solo cuando existe.
- La respuesta del formulario se persiste en `TareaFlujo.datos` antes de pensar en un modelo dedicado de respuestas.

**Pendientes:**
- Ampliar widgets y mejorar la presentacion visual del detalle declarativo.
- Llevar el mismo contrato al editor visual para no depender de definiciones JSON manuales.

## 2026-05-05 - Implementar Fase 1 del contrato v3 para pantallas en flujos

**Tarea:** Extender la validacion backend del modulo `flujos` para aceptar `schema_version = 3` con `actor`, `surface` y `config.ui`, manteniendo compatibilidad con el contrato actual.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/dto.py`
- `flujos/tests/test_flow_definition_form.py`
- `flujos/tests/test_publish_validation.py`

**Cambios realizados:**
- Se agrego soporte explicito para `schema_version = 3` dentro del normalizador central del flujo.
- Se validan `actor.mode`, `actor.value`, `surface` y un contrato minimo `config.ui` para nodos `accion_humana`.
- El tipo de pantalla inicial soportado en backend es `form`, con layout simple, secciones y campos basicos.
- Se agregaron tests unitarios para aceptar y rechazar contratos v3, y un smoke de round-trip API para persistencia del schema nuevo.

**Decisiones o supuestos:**
- El contrato v3 no cambia todavia el runtime ni el renderer productivo; solo habilita y valida el schema.
- Las surfaces iniciales siguen restringidas a `backoffice` y el actor inicial a `mode = group`.
- `schema_version` por default sigue siendo 2 para no alterar el comportamiento actual del editor ni los drafts legacy.

**Pendientes:**
- Ejecutar la Fase 2: snapshot de `config.ui` en `TareaFlujo` y render declarativo de la pantalla en backoffice.

## 2026-05-05 - Definir plan tecnico para pantallas ejecutables en flujos

**Tarea:** Bajar la vision funcional del creador de flujos a un plan tecnico implementable por fases, separando contrato, runtime, renderer y editor.

**Archivos creados:**
- `docs/tmp/flujos-pantallas-v3-plan.md`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se documento el estado real actual de `flujos` y su limite actual en `schema_version = 2`.
- Se propuso una taxonomia de nodos que mantiene `accion_humana` como contenedor de pantallas renderizables.
- Se definio un contrato objetivo `schema_version = 3` con `actor`, `surface` y `config.ui`.
- Se ordenaron fases concretas de implementacion para no mezclar editor visual avanzado con runtime incompleto.

**Decisiones o supuestos:**
- En el primer corte no conviene crear nodos separados para `Formulario`, `Encuesta` y `Tabla`; deben ser variantes de pantalla sobre `accion_humana`.
- En las primeras fases conviene soportar solo `backoffice` y asignacion por grupo, dejando portal, movil y nodos automaticos para etapas posteriores.
- La persistencia inicial puede reutilizar `TareaFlujo.datos` antes de extraer un modelo nuevo de respuestas.

**Pendientes:**
- Traducir este plan a una Fase 1 concreta de implementacion sobre `flujos/application/dto.py`, validaciones y tests.

## 2026-05-05 - Ampliar biblioteca del creador de flujos con plantillas operativas

**Tarea:** Hacer más útil la paleta del editor visual sin cambiar el runtime, agregando entradas ricas que se apoyen en los tipos base ya soportados.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/App.jsx`
- `frontend/flow-editor/src/components/NodePanel.jsx`

**Cambios realizados:**
- La biblioteca del editor ahora separa nodos base y plantillas operativas.
- Se agregaron plantillas `Aprobación`, `Formulario` y `Selección`, todas montadas sobre `accion_humana` con `config.formulario` precargado.
- El drag & drop ahora transporta la metadata de plantilla para crear nodos ya nombrados y preconfigurados al soltarlos en el canvas.

**Decisiones o supuestos:**
- No se agregaron tipos backend nuevos: las plantillas reutilizan los cinco tipos reales que hoy entiende el runtime.
- Este corte busca recuperar expresividad de la UI sin inventar nodos falsos como `Email` o `Tarea territorial`, que siguen requiriendo soporte backend específico.

**Pendientes:**
- Si se quiere volver a tener nodos semánticos de negocio reales, hay que extender `SUPPORTED_NODE_TYPES`, validación, editor y runtime en un corte propio.

## 2026-05-05 - Cubrir round-trip del editor visual de flujos

**Tarea:** Agregar un smoke test chico que cubra el flujo real del editor guardando una definicion, publicandola y volviendola a leer para verificar persistencia de `config.formulario`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/tests/test_publish_validation.py`

**Cambios realizados:**
- Se agrego un test de round-trip sobre `api_definicion` + `api_publicar`.
- El smoke valida que una definicion con `config.formulario` tipo `choice_select` se guarde, se publique y vuelva desde la API sin perder el contrato tipado.
- El test tambien verifica la normalizacion a `schema_version = 2` y que la version publicada sea la misma que se guardo como borrador.

**Decisiones o supuestos:**
- Se cubrio el round-trip desde la API del editor porque es el contrato real que consume React y permite validar persistencia sin meter una prueba end-to-end pesada.
- Se uso `choice_select` porque ejerce un payload mas rico que `text_input` y evita depender de heuristicas booleanas de transiciones.

**Pendientes:**
- Si sigue haciendo falta una validacion visual autenticada, resolverla aparte con una prueba de navegador o smoke manual controlado.

## 2026-05-01 - Rediseñar la pantalla del editor visual de flujos

**Tarea:** Mejorar la experiencia visual de `/flujos/programas/<id>/flujo/editar/` para que el editor se vea más claro, más operativo y le dé más protagonismo al canvas.

**Archivos creados:**
- `frontend/flow-editor/src/app.css`
- `frontend/flow-editor/src/components/nodes/FlowNodeCard.jsx`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/templates/flujos/editor.html`
- `frontend/flow-editor/src/App.jsx`
- `frontend/flow-editor/src/main.jsx`
- `frontend/flow-editor/src/components/NodePanel.jsx`
- `frontend/flow-editor/src/components/PropertiesPanel.jsx`
- `frontend/flow-editor/src/components/nodes/InicioNode.jsx`
- `frontend/flow-editor/src/components/nodes/FinNode.jsx`
- `frontend/flow-editor/src/components/nodes/EsperaNode.jsx`
- `frontend/flow-editor/src/components/nodes/DecisionNode.jsx`
- `frontend/flow-editor/src/components/nodes/AccionHumanaNode.jsx`
- `static/flujos/dist/index.html`
- `static/flujos/dist/assets/index.css`
- `static/flujos/dist/assets/index.js`

**Cambios realizados:**
- Se rehizo la shell Django del editor con una cabecera operativa, métricas de versión, guía de uso y un contenedor visual más limpio para el canvas.
- Se agregó un sistema de estilos propio para el editor React en `app.css`, reemplazando gran parte de los estilos inline dispersos.
- Se rediseñaron toolbar, panel de nodos, inspector lateral, canvas, minimapa y estado de carga/toast para dar una interfaz más consistente.
- Se creó `FlowNodeCard` para unificar la presentación de los nodos custom y hacer visible el estado/configuración de cada tipo.
- Se recompiló el bundle servido por Django en `static/flujos/dist` y luego se limpiaron los artefactos temporales de `npm install` para no dejar ruido en el árbol del repo.

**Decisiones o supuestos:**
- El rediseño se mantuvo estrictamente visual: no cambia contratos backend, endpoints ni comportamiento del runtime.
- No se versionaron `node_modules/` ni `package-lock.json`; solo se conservaron fuentes y bundle generado, porque el objetivo era UX del editor y no gestión de dependencias.

**Pendientes:**
- Hacer una verificación visual autenticada de la pantalla final, porque la revisión en navegador cayó en el login y no en la vista del editor.

## 2026-05-01 - Registrar Secretarias en Django admin

**Tarea:** Habilitar `Secretaria` y `Subsecretaria` en el Django admin, porque no estaban visibles para alta/edicion directa desde `/admin/`.

**Archivos creados:**
- `core/tests/test_admin_registry.py`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `core/admin.py`

**Cambios realizados:**
- Se importaron y registraron `Secretaria` y `Subsecretaria` en `core/admin.py`.
- Se agrego inline de subsecretarias dentro de `SecretariaAdmin` para facilitar la carga jerarquica.
- Se agrego `SubsecretariaAdmin` con listado, filtros, busqueda y `list_select_related` sobre `secretaria`.
- Se cubrio el fix con un test de registry del admin para asegurar que ambos modelos permanezcan publicados.

**Decisiones o supuestos:**
- Se registran ambos modelos, no solo `Subsecretaria`, porque la carga administrativa de subsecretarias depende naturalmente de contar con secretarias visibles en admin.
- Se prefirio una administracion liviana y directa en lugar de una customizacion mas profunda del admin, porque el problema era de publicacion del modelo y no de flujo complejo.

**Pendientes:**
- Ninguno para este fix puntual.

## 2026-05-01 - Corregir cambio de estado en listado de programas

**Tarea:** Reparar la accion de pausar/reactivar programas desde `/configuracion/programas/`, que mostraba el boton pero no ejecutaba nada al hacer click.

**Archivos creados:**
- `configuracion/tests/test_programas_templates.py`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `templates/includes/base.html`

**Cambios realizados:**
- Se agrego soporte global al bloque `extra_js` en la base del backoffice para que los scripts definidos por templates realmente se rendericen.
- Se incorporo SweetAlert2 en la base, porque varias pantallas del backoffice ya usan `Swal.fire` para confirmar acciones.
- Se agrego un test de regresion del listado de programas que verifica la presencia del handler `cambiarEstado`, el formulario oculto y el soporte JS necesario para pausar un programa activo.

**Decisiones o supuestos:**
- La falla no estaba en la view de cambio de estado sino en la base del backoffice: el template del listado definia el JS en `extra_js`, pero la base solo renderizaba `customJS`.
- Se corrigio en la base para reparar este listado y otros templates existentes que ya dependian del mismo patron.

**Pendientes:**
- Revisar progresivamente los templates del backoffice que usan `Swal.fire` para decidir si se estandarizan todos sobre SweetAlert2 o se migran al wrapper `ModernModal`.

## 2026-05-01 - Documentar formalmente la evolucion de flujos

**Tarea:** Registrar en documentacion funcional y tecnica el avance completo del modulo `flujos`, incluyendo runtime operativo, formularios tipados y evolucion del editor visual.

**Archivos creados:**
- `docs/funcionalidades/motor-flujos/v1.1_tareas-operativas-y-formularios-tipados.md`
- `docs/funcionalidades/editor-visual-flujos/v1.1_editor-operativo-y-formularios-tipados.md`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `docs/funcionalidades/_index.md`
- `docs/team/changelog.md`
- `docs/team/current-sprint.md`
- `docs/team/contexto-funcional.md`
- `docs/team/arquitectura.md`
- `docs/team/decisions.md`

**Cambios realizados:**
- Se versiono formalmente el backend de `flujos` como evolucion funcional del motor, documentando `TareaFlujo`, bandeja operativa, APIs, asignacion y formularios tipados.
- Se versiono formalmente el editor visual, documentando la shell operativa, la configuracion visual de `config.formulario` y la validacion frontend alineada al backend.
- Se actualizo el indice de funcionalidades y el changelog con las dos entregas nuevas del modulo.
- Se actualizaron contexto funcional, arquitectura, decisiones y sprint con reglas confirmadas y consecuencias tecnicas del nuevo estado de `flujos`.

**Decisiones o supuestos:**
- Se separa la documentacion del backend/runtime y la del editor en dos documentos versionados porque evolucionaron como superficies distintas del mismo modulo.
- Los pendientes tecnicos menores quedan documentados como deuda o limitacion, no mezclados con la descripcion de lo ya cerrado.

**Pendientes:**
- Ejecutar y automatizar un smoke test de round-trip completo del editor contra guardado/publicacion.

## 2026-05-01 - Empezar a reemplazar JSON libre por formulario tipado en tareas de flujo

**Tarea:** Implementar el primer formulario operativo tipado para resolucion de `TareaFlujo` en el caso comun de aprobacion/rechazo con observacion.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/infrastructure/selectors.py`
- `flujos/interfaces/templates/flujos/backoffice/tarea_detalle.html`
- `flujos/interfaces/web/forms.py`
- `flujos/interfaces/web/views.py`
- `flujos/tests/test_backoffice_tasks.py`

**Cambios realizados:**
- Se agrego deteccion de schema de resolucion para el patron de dos transiciones booleanas sobre el mismo campo.
- El detalle web ahora muestra un formulario tipado de decision + observacion para ese caso, manteniendo fallback a JSON libre para el resto.
- El detalle API ahora expone ese schema en `task.resolution_form` para futuras UIs externas.
- Se mejoro la UI del detalle de tarea con contexto acumulado de la instancia, historial visible y una presentacion mas guiada de la decision binaria.
- La bandeja se rehizo como lista de tarjetas operativas mas escaneable, manteniendo asignacion inline y preservando filtros activos en los retornos.
- El editor visual sumo una cabecera operativa con estado de versiones, guia de uso y contenedor mas claro para el canvas.
- Se agrego contrato explicito `config.formulario` para nodos `accion_humana`, con validacion en definicion/publicacion y prioridad sobre la heuristica de formularios tipados.
- Se extendio `config.formulario` con el tipo `text_input`, incluyendo soporte web, exposicion por API y bloqueo del resolver directo en bandeja cuando la tarea requiere input tipado.
- Se agrego un tercer tipo explicito, `choice_select`, para listas cerradas de opciones con validacion de opciones unicas y soporte operativo completo en detalle/API.
- El editor React ahora permite configurar visualmente `config.formulario` en nodos `accion_humana`, incluyendo decision booleana, texto y seleccion cerrada, con persistencia en la definicion y validaciones frontend alineadas al backend.
- Se agregaron tests para resolucion web con formulario tipado y para verificar el schema en la API de detalle.

**Decisiones o supuestos:**
- El primer formulario tipado se limita al caso inferible sin contrato v2 explicito: un campo booleano con salidas `True/False`.
- Se usa `observacion` como campo auxiliar opcional porque ya forma parte del ejemplo operativo que venimos usando.

**Pendientes:**
- Definir el contrato v2 de metadata por nodo para no depender de heuristicas sobre transiciones.
- Sumar otros formularios tipados una vez definido ese contrato (por ejemplo select, texto obligatorio, numerico).

## 2026-05-01 - Exponer detalle de tarea de flujo por API JSON

**Tarea:** Completar la capa API del backoffice operativo agregando detalle de `TareaFlujo` con metadata del nodo, acciones disponibles e historial de eventos.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/infrastructure/selectors.py`
- `flujos/interfaces/api/urls.py`
- `flujos/interfaces/web/views.py`
- `flujos/tests/test_backoffice_tasks.py`
- `flujos/tests/test_module_guards.py`

**Cambios realizados:**
- Se agrego `GET /api/flujos/tareas/<id>/` para devolver detalle de tarea con nodo completo, acciones, links operativos y timeline de `InstanciaLog`.
- Se extrajeron serializadores livianos de tarea y log en el selector para no duplicar armado de payloads JSON.
- Se agregaron tests de detalle API y guard del modulo inactivo para la nueva ruta.

**Decisiones o supuestos:**
- El timeline se devuelve en orden descendente por timestamp, priorizando el ultimo evento operativo.
- La API devuelve usuarios asignables y links de accion para facilitar que otra UI pueda operar la tarea sin hardcodear rutas.

**Pendientes:**
- Si hace falta una UI mas rica, exponer tambien el historial de version del flujo o un endpoint de instancia completa.

## 2026-05-01 - Exponer resolucion de tareas de flujo por API JSON

**Tarea:** Completar la operatoria API del modulo permitiendo resolver `TareaFlujo` desde otra UI sin depender del formulario HTML.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/api/urls.py`
- `flujos/interfaces/web/views.py`
- `flujos/tests/test_backoffice_tasks.py`

**Cambios realizados:**
- Se agrego `POST /api/flujos/tareas/<id>/resolver/` reutilizando `TareaResolverForm` y `resolver_tarea_flujo`.
- La API devuelve la tarea ya actualizada y el estado actual de la instancia para evitar una consulta extra del consumidor.
- Se agregaron tests para resolucion exitosa con payload JSON y para rechazo de JSON invalido.

**Decisiones o supuestos:**
- La API usa el mismo permiso operativo que la bandeja y la asignacion (`programaOperar` o `programaConfigurar`).
- El payload esperado sigue siendo `{"datos": {...}}` para no abrir un contrato distinto al del detalle web.

**Pendientes:**
- Si la UI externa necesita previsualizar el formulario completo, exponer un endpoint de detalle de tarea con metadata operativa y timeline.

## 2026-05-01 - Exponer asignacion de tareas de flujo por API JSON

**Tarea:** Permitir que otras UIs consuman la misma operatoria de asignacion/reasignacion de `TareaFlujo` sin depender del POST HTML del backoffice.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/api/urls.py`
- `flujos/interfaces/web/views.py`
- `flujos/tests/test_backoffice_tasks.py`

**Cambios realizados:**
- Se agrego `POST /api/flujos/tareas/<id>/asignar/` reutilizando el servicio de asignacion del backoffice.
- La API devuelve la tarea serializada ya actualizada para que otra UI no tenga que volver a consultar la bandeja completa.
- Se agregaron tests para asignacion via API y para rechazo de JSON invalido.

**Decisiones o supuestos:**
- La API reutiliza el mismo permiso operativo que la bandeja web (`programaOperar` o `programaConfigurar`).
- Ante error de payload o de negocio, responde `400` con mensaje simple en JSON para mantener el contrato liviano del modulo.

**Pendientes:**
- Si otra UI lo necesita, exponer tambien la resolucion de tareas por API con el mismo contrato de payload JSON.

## 2026-05-01 - Auditar asignacion y reasignacion de tareas de flujo

**Tarea:** Dejar trazabilidad operativa de los cambios de responsable sobre `TareaFlujo`.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/services.py`
- `flujos/tests/test_backoffice_tasks.py`

**Cambios realizados:**
- La asignacion, desasignacion y reasignacion de tareas pendientes ahora genera un `InstanciaLog` asociado a la instancia del flujo.
- El log reutiliza el nodo actual como origen/destino y guarda metadata del responsable anterior y nuevo en `datos_transicion`.
- Se agregaron asserts en los tests web para verificar que la auditoria se crea al asignar y reasignar.

**Decisiones o supuestos:**
- No se registra log cuando el responsable no cambia, para evitar ruido operativo.
- Se reutiliza `InstanciaLog` como bitacora del modulo en lugar de crear una tabla especifica de historial de asignaciones.

**Pendientes:**
- Si hace falta una UI de auditoria, exponer estos eventos en una timeline del detalle de instancia o de tarea.

## 2026-05-01 - Agregar asignacion y reasignacion de tareas de flujo

**Tarea:** Completar la primera operatoria de backoffice permitiendo asignar y reasignar `TareaFlujo` desde la bandeja y desde el detalle.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/services.py`
- `flujos/infrastructure/selectors.py`
- `flujos/interfaces/templates/flujos/backoffice/bandeja_tareas.html`
- `flujos/interfaces/templates/flujos/backoffice/tarea_detalle.html`
- `flujos/interfaces/web/forms.py`
- `flujos/interfaces/web/urls.py`
- `flujos/interfaces/web/views.py`
- `flujos/tests/test_backoffice_tasks.py`

**Cambios realizados:**
- Se agregó un caso de uso específico para asignar o desasignar tareas pendientes del runtime.
- La bandeja ahora permite asignar o reasignar inline cada tarea pendiente.
- El detalle de tarea ahora también permite cambiar responsable sin salir de la vista.
- Se incorporó un queryset reutilizable de usuarios asignables basado en los grupos `programaOperar` y `programaConfigurar`.
- Se agregaron tests para asignación desde la bandeja y reasignación desde el detalle.

**Decisiones o supuestos:**
- La asignación se restringe a tareas pendientes, porque una tarea resuelta o cancelada ya no forma parte de la operatoria activa.
- No se agregó todavía historial específico de asignaciones; por ahora el cambio impacta solo en `asignado_a`.

**Pendientes:**
- Registrar historial de asignación/reasignación si la operatoria requiere auditoría de responsables.
- Incorporar asignación por reglas o roles a nivel de nodo cuando el contrato v2 lo defina.

## 2026-05-01 - Completar la primera bandeja operativa con filtros, detalle y API JSON

**Tarea:** Hacer utilizable la bandeja de `TareaFlujo` para operatoria real: filtrar resultados, resolver pasos que requieren payload y exponer la consulta a otras UIs.

**Archivos creados:**
- `flujos/interfaces/templates/flujos/backoffice/tarea_detalle.html`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/services.py`
- `flujos/infrastructure/selectors.py`
- `flujos/interfaces/api/urls.py`
- `flujos/interfaces/templates/flujos/backoffice/bandeja_tareas.html`
- `flujos/interfaces/web/forms.py`
- `flujos/interfaces/web/urls.py`
- `flujos/interfaces/web/views.py`
- `flujos/runtime.py`
- `flujos/tests/test_backoffice_tasks.py`
- `flujos/tests/test_runtime_action_tasks.py`

**Cambios realizados:**
- La bandeja ahora acepta filtros por programa, asignado y estado reutilizando un selector central.
- Se agregó una vista de detalle de tarea con formulario JSON para resolver nodos que dependen de condiciones y datos de entrada.
- Se expuso la misma consulta operativa por API JSON bajo `/api/flujos/tareas/`.
- El runtime ahora acumula los datos usados para avanzar en `InstanciaFlujo.datos`, no solo en el log puntual.
- Se agregaron tests para filtros de bandeja, detalle con payload, API JSON y persistencia de datos del runtime.

**Decisiones o supuestos:**
- El formulario inicial de resolución sigue siendo genérico y usa JSON libre para no bloquear el avance del slice mientras no exista un contrato de formularios por tipo de nodo.
- La API JSON devuelve el mismo estado operativo que ve la bandeja web, incluyendo si la tarea puede resolverse directo o requiere payload.
- El filtro por asignado usa `sin_asignar` o el id del usuario asignado; no se agregó todavía una operatoria de asignación manual.

**Pendientes:**
- Reemplazar el JSON libre por formularios tipados cuando el contrato v2 defina metadata por nodo.
- Agregar asignación/reasignación de `TareaFlujo` desde la bandeja.
- Exponer detalle de tarea por API si otra UI necesita abrir el formulario completo.

## 2026-05-01 - Exponer TareaFlujo en una primera bandeja operativa

**Tarea:** Llevar `TareaFlujo` a una primera superficie de backoffice para listar pendientes y resolver pasos humanos simples desde UI.

**Archivos creados:**
- `flujos/infrastructure/selectors.py`
- `flujos/interfaces/templates/flujos/backoffice/bandeja_tareas.html`
- `flujos/tests/test_backoffice_tasks.py`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/services.py`
- `flujos/interfaces/web/urls.py`
- `flujos/interfaces/web/views.py`
- `flujos/module.py`
- `flujos/tests/test_module_guards.py`

**Cambios realizados:**
- Se agregó un selector ORM para construir la bandeja operativa de tareas pendientes.
- Se creó un caso de uso mínimo para resolver una `TareaFlujo` y avanzar la instancia cuando el nodo tiene salida libre.
- Se expusieron rutas web de backoffice para listar tareas pendientes y resolverlas desde POST.
- Se agregó la primera pantalla de bandeja con métricas básicas y acciones inline.
- Se cubrió el slice con tests de UI/backoffice y un guard adicional del módulo inactivo.

**Decisiones o supuestos:**
- En esta primera iteración solo se marcan como resolubles desde bandeja las tareas cuyo nodo puede avanzar sin datos adicionales.
- Las tareas que dependen de condiciones o payload quedan visibles pero bloqueadas hasta tener pantalla/formulario específico.
- Se habilitó acceso tanto para `programaConfigurar` como para `programaOperar` porque la pantalla ya entra en operatoria de backoffice.

**Pendientes:**
- Agregar filtros por programa, usuario asignado y estado en la bandeja.
- Diseñar formulario/detalle para tareas que requieren datos antes de avanzar.
- Exponer la misma información por API si el editor o futuras UIs la necesitan.

## 2026-05-01 - Materializar tareas de accion humana en el runtime de flujos

**Tarea:** Incorporar una pieza operativa mínima al runtime para que los nodos `accion_humana` generen trabajo pendiente real y no solo logging.

**Archivos creados:**
- `flujos/migrations/0003_tareaflujo.py`
- `flujos/tests/__init__.py`
- `flujos/tests/test_runtime_action_tasks.py`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/interfaces/module_api.py`
- `flujos/models.py`
- `flujos/runtime.py`

**Cambios realizados:**
- Se agregó el modelo `TareaFlujo` como unidad operativa mínima para pasos humanos del runtime.
- `FlowRuntime` ahora crea una tarea pendiente al entrar a un nodo `accion_humana`.
- Al salir de un nodo `accion_humana`, la tarea pendiente se resuelve automáticamente.
- Al cancelar una instancia de flujo desde el contrato público del módulo, las tareas pendientes asociadas se cancelan.
- Se agregaron tests de runtime para creación de tarea, resolución al avanzar y cancelación por baja de la instancia.

**Decisiones o supuestos:**
- Este slice no introduce todavía bandeja, vistas ni asignación avanzada; solo materializa la pieza operativa mínima necesaria.
- La tarea guarda un snapshot liviano del nodo y metadata operativa en `datos`.
- La resolución/cancelación automática usa `resuelto_por` cuando existe usuario disparador.

**Pendientes:**
- Exponer estas tareas en una API o selector de bandeja operativa.
- Diseñar asignación por rol/paso dentro del contrato v2.
- Conectar la UI del backoffice para operar las tareas materializadas.

## 2026-05-01 - Alinear validacion de publicacion entre backend y frontend

**Tarea:** Evitar que el editor permita publicar grafos que el backend ya rechaza por estar rotos o desconectados.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `frontend/flow-editor/src/utils/validators.js`
- `flujos/application/dto.py`
- `flujos/tests/test_flow_definition_form.py`
- `flujos/tests/test_publish_validation.py`

**Cambios realizados:**
- Se agregaron validaciones de publicacion en backend para nodos sin entrada, nodos sin salida y nodos no alcanzables desde el inicio.
- Se cubrieron esos casos con tests de formulario y de API.
- Se alineo el validador del editor React para bloquear publicacion de grafos con esas mismas fallas antes del request al backend.

**Decisiones o supuestos:**
- Los errores de publicacion del grafo pasan a ser bloqueantes tanto en backend como en frontend.
- La validacion de nombres vacios de nodo se mantiene como warning de UX por ahora y no como error bloqueante.

**Pendientes:**
- Decidir si el nombre de nodo debe pasar a ser requisito de publicacion.
- Avanzar al siguiente slice del contrato v2 o empezar la pieza operativa del runtime.

## 2026-05-01 - Separar validacion de borrador y publicacion en flujos

**Tarea:** Alinear el backend de `flujos` con la UX del editor para permitir guardar borradores incompletos y exigir requisitos minimos recien al publicar.

**Archivos creados:**
- `flujos/tests/test_publish_validation.py`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/dto.py`
- `flujos/interfaces/web/forms.py`
- `flujos/interfaces/web/views.py`
- `flujos/tests/test_flow_definition_form.py`

**Cambios realizados:**
- Se agrego `validation_mode` al validador del contrato JSON para distinguir `draft` de `publish`.
- Se relajo la validacion de borrador: ahora permite guardar definiciones sin nodo de inicio/fin y con nombres vacios, manteniendo la validacion estructural del grafo.
- Se endurecio la publicacion: `api_publicar` revalida la ultima version borrador en modo `publish` antes de archivarla/publicarla.
- Se agregaron tests para borradores incompletos validos y para rechazo de publicacion de un borrador incompleto via API.

**Decisiones o supuestos:**
- El backend mantiene como bloqueantes solo las reglas de estructura y de publicacion minima; los warnings de UX siguen viviendo en frontend.
- No se expandieron aun los tipos de nodo soportados por el runtime.

**Pendientes:**
- Definir validaciones de publicacion mas ricas para el contrato v2 (por ejemplo roles obligatorios o metadata por tipo de nodo).
- Diseñar el modelo operativo del runtime para pasos humanos materializados.

## 2026-05-01 - Implementar slice inicial de Fase 1 para flujos de programas

**Tarea:** Endurecer el contrato JSON del módulo `flujos` en backend con validación estructural y tests unitarios dedicados.

**Archivos creados:**
- `flujos/tests/test_flow_definition_form.py`

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`
- `flujos/application/dto.py`
- `flujos/interfaces/web/forms.py`

**Cambios realizados:**
- Se incorporó una utilidad central de normalización/validación del contrato JSON en `flujos/application/dto.py`.
- Se agregó `schema_version` por defecto al guardar definiciones y se normalizó `config` en nodos existentes.
- Se validan ids duplicados, tipos de nodo soportados, referencias válidas en transiciones y operadores soportados en condiciones.
- Se conectó `DefinicionFlujoForm` a la nueva validación central.
- Se agregaron tests unitarios para contrato válido, ids duplicados, transiciones rotas, tipo de nodo no soportado y operador inválido.

**Decisiones o supuestos:**
- En este slice se preservan únicamente los tipos de nodo que el runtime actual sabe ejecutar.
- La compatibilidad hacia atrás se mantiene aceptando definiciones actuales sin `schema_version` y normalizándolas a versión 2.
- Las validaciones de publicación más ricas (conectividad completa, roles obligatorios por paso, etc.) quedan para slices siguientes.

**Pendientes:**
- Separar validaciones de borrador vs publicación.
- Diseñar el contrato v2 extendido de nodos sin romper el runtime actual.
- Introducir la pieza operativa del runtime para pasos humanos materializados.

## 2026-05-01 - Planificar implementación completa de flujos de programas

**Tarea:** Analizar el módulo `flujos` actual y definir un orden de implementación completo para llevarlo de MVP técnico a operador funcional de programas.

**Archivos creados:**
- Ninguno

**Archivos modificados:**
- `docs/tmp/WORKLOG.md`

**Cambios realizados:**
- Se revisó la documentación funcional y técnica del motor de flujos y del editor visual.
- Se contrastó el contrato actual (`nodos` + `transiciones`) con la visión funcional de programas.
- Se definió un orden recomendado por fases: contrato JSON v2, runtime operable, pantallas de ejecución, evolución del editor, integraciones y automatismos.

**Decisiones o supuestos:**
- No conviene reescribir `flujos` desde cero; conviene extender el enfoque actual de JSON versionado.
- La principal deuda no está en el canvas React sino en la falta de operatoria materializada para pasos humanos.
- El primer slice de implementación debe cerrar el contrato funcional/técnico antes de ampliar nodos o UI.

**Pendientes:**
- Bajar el plan a backlog ejecutable con entregables concretos por fase.
- Definir el contrato JSON v2 y las tareas operativas materializadas del runtime.

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
- Se resolvieron conflictos manteniendo la estructura modular canónica de la rama del PR.
- Se agregaron `portal_ciudadano` y `reclamos` como apps legacy no modularizadas para no duplicar apps ya declaradas en `config.modules`.
- Se conservaron rutas opcionales por registry modular y se agregaron solo rutas directas para apps nuevas no modularizadas.
- Se movió la API nueva de `tramites` a `tramites/interfaces/api` y los services a `tramites/application`.
- Se actualizaron imports legacy de `portal_ciudadano` y `conversaciones`.
- Se aceptó la eliminación del selector legacy `portal/selectors/ciudadano.py`.

**Decisiones o supuestos:**
- `tramites`, `chatbot`, `conversaciones` y `flujos` siguen publicando rutas mediante `module.py`.
- `portal_ciudadano` y `reclamos` se mantienen como apps directas porque llegaron desde `Dev` sin layout modular.

**Pendientes:**
- Ejecutar tests/checks solo si se pide explícitamente.
