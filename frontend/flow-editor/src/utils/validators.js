/**
 * Validaciones del grafo de flujo.
 * Retornan arrays de mensajes de error/advertencia.
 */

/**
 * Valida que el flujo tenga la estructura mínima para poder publicarse.
 * @param {Array} nodes - Nodos de React Flow
 * @param {Array} edges - Aristas de React Flow
 * @returns {{errores: string[], advertencias: string[]}}
 */
export function validarFlujo(nodes, edges) {
  const errores = [];
  const advertencias = [];

  const supportedUiFieldKinds = new Set(['text', 'textarea', 'number', 'date', 'radio', 'select', 'checkbox']);
  const supportedHttpMethods = new Set(['GET', 'POST', 'PUT', 'PATCH', 'DELETE']);

  const nodeIds = new Set(nodes.map((node) => node.id));
  const startNodes = nodes.filter((n) => n.data?.tipo === 'inicio');

  const tieneInicio = startNodes.length > 0;
  const tieneFin = nodes.some((n) => n.data?.tipo === 'fin');

  if (!tieneInicio) {
    errores.push('El flujo debe tener un nodo de inicio.');
  }
  if (startNodes.length > 1) {
    errores.push('El flujo no puede tener más de un nodo de inicio.');
  }
  if (!tieneFin) {
    errores.push('El flujo debe tener al menos un nodo de fin.');
  }

  const incomingByNode = new Map();
  const outgoingByNode = new Map();
  nodes.forEach((node) => {
    incomingByNode.set(node.id, []);
    outgoingByNode.set(node.id, []);
  });

  edges.forEach((edge) => {
    if (nodeIds.has(edge.source) && nodeIds.has(edge.target)) {
      outgoingByNode.get(edge.source)?.push(edge.target);
      incomingByNode.get(edge.target)?.push(edge.source);
    }
  });

  nodes.forEach((node) => {
    const tieneSalida = (outgoingByNode.get(node.id) || []).length > 0;
    const tieneEntrada = (incomingByNode.get(node.id) || []).length > 0;
    const esTipoInicio = node.data?.tipo === 'inicio';
    const esTipoFin = node.data?.tipo === 'fin';

    if (!esTipoFin && !tieneSalida) {
      errores.push(
        `El nodo "${node.data?.label || node.id}" no tiene conexión de salida.`
      );
    }
    if (!esTipoInicio && !tieneEntrada) {
      errores.push(
        `El nodo "${node.data?.label || node.id}" no tiene conexión de entrada.`
      );
    }
  });

  if (startNodes.length === 1) {
    const reachable = new Set();
    const pending = [startNodes[0].id];

    while (pending.length > 0) {
      const current = pending.pop();
      if (reachable.has(current)) {
        continue;
      }
      reachable.add(current);
      for (const target of outgoingByNode.get(current) || []) {
        if (!reachable.has(target)) {
          pending.push(target);
        }
      }
    }

    const disconnectedNodes = nodes.filter((node) => !reachable.has(node.id));
    if (disconnectedNodes.length > 0) {
      errores.push(
        `Hay nodos desconectados del inicio: ${disconnectedNodes
          .map((node) => `"${node.data?.label || node.id}"`)
          .join(', ')}.`
      );
    }
  }

  // Nodos sin nombre
  nodes.forEach((node) => {
    if (!node.data?.label?.trim()) {
      advertencias.push(`Un nodo (${node.data?.tipo || node.id}) no tiene nombre configurado.`);
    }
  });

  nodes.forEach((node) => {
    const formulario = node.data?.config?.formulario;
    const uiConfig = node.data?.config?.ui;
    const emailConfig = node.data?.config?.email;
    const httpConfig = node.data?.config?.http;
    if (node.data?.tipo !== 'accion_humana' || !formulario) {
      if (node.data?.tipo !== 'accion_humana' || !uiConfig) {
        if (node.data?.tipo !== 'accion_email' && node.data?.tipo !== 'accion_http') {
          return;
        }
      }
    }

    const nodeLabel = node.data?.label || node.id;

    if (uiConfig) {
      const actor = node.data?.actor;
      const surface = Array.isArray(node.data?.surface) ? node.data.surface : [];
      if (actor?.mode !== 'group' || !actor?.value?.trim()) {
        errores.push(`El nodo "${nodeLabel}" debe definir un grupo responsable para la pantalla declarativa.`);
      }
      if (surface.length !== 1 || surface[0] !== 'backoffice') {
        errores.push(`El nodo "${nodeLabel}" solo puede usar la superficie backoffice en esta versión.`);
      }
      if (uiConfig.type !== 'form') {
        errores.push(`El nodo "${nodeLabel}" usa un tipo de pantalla no soportado: "${uiConfig.type || ''}".`);
      }
      if (!uiConfig.title?.trim()) {
        errores.push(`El nodo "${nodeLabel}" debe definir un título visible para la pantalla.`);
      }
      const sections = Array.isArray(uiConfig.sections) ? uiConfig.sections : [];
      if (sections.length === 0) {
        errores.push(`El nodo "${nodeLabel}" debe tener al menos una sección en la pantalla.`);
        return;
      }

      const seenFieldIds = new Set();
      sections.forEach((section) => {
        const fields = Array.isArray(section.fields) ? section.fields : [];
        if (fields.length === 0) {
          errores.push(`El nodo "${nodeLabel}" tiene una sección sin campos configurados.`);
          return;
        }
        fields.forEach((field) => {
          const fieldId = field.id?.trim();
          if (!fieldId) {
            errores.push(`El nodo "${nodeLabel}" tiene un campo de pantalla sin id.`);
            return;
          }
          if (seenFieldIds.has(fieldId)) {
            errores.push(`El nodo "${nodeLabel}" repite ids de campo en la pantalla declarativa.`);
          }
          seenFieldIds.add(fieldId);
          if (!field.label?.trim()) {
            errores.push(`El nodo "${nodeLabel}" tiene un campo de pantalla sin etiqueta visible.`);
          }
          if (!supportedUiFieldKinds.has(field.kind)) {
            errores.push(`El nodo "${nodeLabel}" usa un tipo de campo no soportado: "${field.kind || ''}".`);
          }
          if (field.kind === 'textarea' && field.rows && (!Number.isInteger(Number(field.rows)) || Number(field.rows) <= 0)) {
            errores.push(`El nodo "${nodeLabel}" debe definir filas válidas en el campo "${fieldId}".`);
          }
          if (['radio', 'select'].includes(field.kind)) {
            const options = Array.isArray(field.options) ? field.options : [];
            if (options.length === 0) {
              errores.push(`El nodo "${nodeLabel}" debe tener opciones en el campo "${fieldId}".`);
              return;
            }
            const seenValues = new Set();
            options.forEach((option) => {
              if (!option.value?.trim() || !option.label?.trim()) {
                errores.push(`El nodo "${nodeLabel}" tiene opciones incompletas en el campo "${fieldId}".`);
                return;
              }
              if (seenValues.has(option.value.trim())) {
                errores.push(`El nodo "${nodeLabel}" repite valores en las opciones del campo "${fieldId}".`);
              }
              seenValues.add(option.value.trim());
            });
          }
        });
      });
    }

    if (node.data?.tipo === 'accion_email') {
      const recipients = Array.isArray(emailConfig?.to) ? emailConfig.to : [];
      if (recipients.length === 0 || recipients.some((recipient) => !recipient?.trim())) {
        errores.push(`El nodo "${nodeLabel}" debe tener al menos un destinatario de email válido.`);
      }
      if (!emailConfig?.subject?.trim()) {
        errores.push(`El nodo "${nodeLabel}" debe definir un asunto de email.`);
      }
      if (!emailConfig?.body?.trim()) {
        errores.push(`El nodo "${nodeLabel}" debe definir un cuerpo de email.`);
      }
      return;
    }

    if (node.data?.tipo === 'accion_http') {
      if (!supportedHttpMethods.has(httpConfig?.method || '')) {
        errores.push(`El nodo "${nodeLabel}" usa un método HTTP no soportado.`);
      }
      if (!httpConfig?.url?.trim()) {
        errores.push(`El nodo "${nodeLabel}" debe definir una URL HTTP.`);
      }
      if (!Number.isInteger(Number(httpConfig?.timeout_seconds)) || Number(httpConfig?.timeout_seconds) <= 0) {
        errores.push(`El nodo "${nodeLabel}" debe definir un timeout HTTP válido.`);
      }
      const headers = Array.isArray(httpConfig?.headers) ? httpConfig.headers : [];
      const seenHeaderKeys = new Set();
      headers.forEach((header) => {
        const key = header?.key?.trim();
        if (!key) {
          errores.push(`El nodo "${nodeLabel}" tiene headers HTTP sin clave.`);
          return;
        }
        const keyLower = key.toLowerCase();
        if (seenHeaderKeys.has(keyLower)) {
          errores.push(`El nodo "${nodeLabel}" repite headers HTTP.`);
        }
        seenHeaderKeys.add(keyLower);
      });
      return;
    }

    if (!formulario) {
      return;
    }

    const fieldName = formulario.field_name?.trim();
    if (!fieldName) {
      errores.push(`El nodo "${nodeLabel}" tiene un formulario sin campo runtime configurado.`);
      return;
    }

    if (formulario.type === 'boolean_decision') {
      const salidas = edges.filter((edge) => edge.source === node.id);
      if (salidas.length !== 2) {
        errores.push(`El nodo "${nodeLabel}" con decisión booleana debe tener exactamente dos salidas.`);
        return;
      }
      const condiciones = salidas.map((edge) => edge.data?.condicion).filter(Boolean);
      if (condiciones.length !== 2) {
        errores.push(`El nodo "${nodeLabel}" con decisión booleana requiere dos salidas condicionales.`);
        return;
      }
      const campos = new Set(condiciones.map((condicion) => condicion.campo));
      const operadores = new Set(condiciones.map((condicion) => condicion.operador));
      const valores = new Set(condiciones.map((condicion) => condicion.valor));
      if (campos.size !== 1 || !campos.has(fieldName) || operadores.size !== 1 || !operadores.has('==') || !valores.has(true) || !valores.has(false)) {
        errores.push(`El nodo "${nodeLabel}" debe mapear salidas true/false sobre el campo "${fieldName}".`);
      }
    }

    if (formulario.type === 'text_input') {
      if (formulario.multiline && (!Number.isInteger(Number(formulario.rows)) || Number(formulario.rows) <= 0)) {
        errores.push(`El nodo "${nodeLabel}" debe definir una cantidad de filas válida para el campo multilínea.`);
      }
    }

    if (formulario.type === 'choice_select') {
      const options = Array.isArray(formulario.options) ? formulario.options : [];
      if (options.length === 0) {
        errores.push(`El nodo "${nodeLabel}" debe tener al menos una opción configurada.`);
      }
      const seenValues = new Set();
      options.forEach((option) => {
        if (!option.value?.trim() || !option.label?.trim()) {
          errores.push(`El nodo "${nodeLabel}" tiene opciones incompletas en su selección cerrada.`);
          return;
        }
        if (seenValues.has(option.value.trim())) {
          errores.push(`El nodo "${nodeLabel}" repite valores en la lista de opciones.`);
        }
        seenValues.add(option.value.trim());
      });
    }
  });

  return { errores, advertencias };
}

/**
 * Verifica si el flujo puede publicarse (sin errores bloqueantes).
 */
export function puedePublicar(nodes, edges) {
  const { errores } = validarFlujo(nodes, edges);
  return errores.length === 0;
}
