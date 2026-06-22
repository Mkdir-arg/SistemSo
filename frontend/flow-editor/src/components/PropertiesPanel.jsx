import { useEffect, useState } from 'react';

import ScreenPreview from './ScreenPreview.jsx';

/**
 * Panel derecho — propiedades del nodo o transición seleccionada.
 */

const OPERADORES = ['==', '!=', '>', '>=', '<', '<=', 'in'];

const FORM_TYPE_OPTIONS = [
  { value: '', label: 'Sin formulario tipado' },
  { value: 'boolean_decision', label: 'Decision booleana' },
  { value: 'text_input', label: 'Campo de texto' },
  { value: 'choice_select', label: 'Seleccion cerrada' },
];

const ACTION_EXPERIENCE_OPTIONS = [
  { value: '', label: 'Sin contrato de captura' },
  { value: 'legacy_form', label: 'Formulario tipado v2' },
  { value: 'ui_form', label: 'Interfaz declarativa v3' },
];

const UI_FIELD_KIND_OPTIONS = [
  { value: 'text', label: 'Texto' },
  { value: 'textarea', label: 'Texto largo' },
  { value: 'number', label: 'Numero' },
  { value: 'date', label: 'Fecha' },
  { value: 'radio', label: 'Opcion unica' },
  { value: 'select', label: 'Lista' },
  { value: 'checkbox', label: 'Confirmacion' },
  { value: 'info', label: 'Info' },
  { value: 'summary', label: 'Resumen' },
  { value: 'table', label: 'Tabla' },
];

const UI_BLOCK_TYPE_OPTIONS = [
  { value: 'text', label: 'Texto' },
  { value: 'textarea', label: 'Texto largo' },
  { value: 'number', label: 'Numero' },
  { value: 'date', label: 'Fecha' },
  { value: 'radio', label: 'Opcion unica' },
  { value: 'select', label: 'Lista' },
  { value: 'checkbox', label: 'Confirmacion' },
  { value: 'info', label: 'Info' },
  { value: 'summary', label: 'Resumen' },
  { value: 'table', label: 'Tabla' },
];

const INFO_TONE_OPTIONS = [
  { value: 'info', label: 'Info' },
  { value: 'success', label: 'Exito' },
  { value: 'warning', label: 'Advertencia' },
  { value: 'danger', label: 'Alerta' },
  { value: 'neutral', label: 'Neutral' },
];

const UI_LAYOUT_OPTIONS = [
  { value: 'single_column', label: 'Una columna' },
  { value: 'two_column', label: 'Dos columnas' },
];

const SIMPLE_TABLE_COLUMNS = [
  { key: 'campo', label: 'Campo' },
  { key: 'valor', label: 'Valor' },
];

const SIMPLE_TABLE_TEMPLATES = [
  {
    id: 'ciudadano',
    label: 'Datos del ciudadano',
    rows: [
      { campo: 'DNI', valor: '{{ ciudadano.dni }}' },
      { campo: 'Nombre y apellido', valor: '{{ ciudadano.nombre_completo }}' },
      { campo: 'Email', valor: '{{ ciudadano.email }}' },
    ],
  },
  {
    id: 'programa',
    label: 'Datos del programa',
    rows: [
      { campo: 'Código', valor: '{{ programa.codigo }}' },
      { campo: 'Nombre', valor: '{{ programa.nombre }}' },
    ],
  },
  {
    id: 'estado',
    label: 'Estado del paso',
    rows: [
      { campo: 'Estado', valor: 'En revisión' },
      { campo: 'Responsable', valor: '{{ usuario.nombre_completo }}' },
    ],
  },
];

const DISPLAY_ONLY_UI_FIELD_KINDS = new Set(['info', 'summary', 'table']);

const ACTOR_GROUP_OPTIONS = [
  { value: 'programaOperar', label: 'programaOperar' },
  { value: 'programaConfigurar', label: 'programaConfigurar' },
];

const HTTP_METHOD_OPTIONS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];

function createConditionSuggestion(path, label, valueType = 'string', extra = {}) {
  return {
    path,
    label,
    valueType,
    ...extra,
  };
}

function inferUiFieldConditionSuggestion(field, section) {
  if (!field?.id) {
    return null;
  }

  if (DISPLAY_ONLY_UI_FIELD_KINDS.has(field.kind)) {
    return null;
  }

  const baseLabel = section?.title ? `${section.title} · ${field.label || field.id}` : (field.label || field.id);
  if (field.kind === 'checkbox') {
    return createConditionSuggestion(field.id, baseLabel, 'boolean', { defaultValue: true });
  }
  if (field.kind === 'number') {
    return createConditionSuggestion(field.id, baseLabel, 'number', { defaultValue: 0 });
  }
  if (field.kind === 'radio' || field.kind === 'select') {
    const options = Array.isArray(field.options) ? field.options.filter((option) => option?.value) : [];
    return createConditionSuggestion(field.id, baseLabel, 'string', {
      options,
      defaultValue: options[0]?.value ?? '',
    });
  }

  return createConditionSuggestion(field.id, baseLabel, 'string', { defaultValue: '' });
}

function buildConditionSuggestions(sourceNode) {
  if (!sourceNode?.data) {
    return [];
  }

  const suggestions = [];
  const nodeLabel = sourceNode.data.label || sourceNode.id;
  const formulario = sourceNode.data.config?.formulario;
  const uiConfig = sourceNode.data.config?.ui;

  if (formulario?.field_name) {
    if (formulario.type === 'boolean_decision') {
      suggestions.push(createConditionSuggestion(formulario.field_name, `${nodeLabel} · resultado`, 'boolean', { defaultValue: true }));
    } else if (formulario.type === 'choice_select') {
      const options = Array.isArray(formulario.options) ? formulario.options.filter((option) => option?.value) : [];
      suggestions.push(createConditionSuggestion(formulario.field_name, `${nodeLabel} · ${formulario.field_label || formulario.field_name}`, 'string', {
        options,
        defaultValue: options[0]?.value ?? '',
      }));
    } else {
      suggestions.push(createConditionSuggestion(formulario.field_name, `${nodeLabel} · ${formulario.field_label || formulario.field_name}`, 'string', { defaultValue: '' }));
    }
  }

  (uiConfig?.sections || []).forEach((section) => {
    (section.fields || []).forEach((field) => {
      const suggestion = inferUiFieldConditionSuggestion(field, section);
      if (suggestion) {
        suggestions.push(suggestion);
      }
    });
  });

  if (sourceNode.data.tipo === 'accion_email') {
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.ok`, `${nodeLabel} · email enviado`, 'boolean', { defaultValue: true }));
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.subject`, `${nodeLabel} · asunto`, 'string', { defaultValue: '' }));
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.sent_at`, `${nodeLabel} · fecha de envío`, 'string', { defaultValue: '' }));
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.error`, `${nodeLabel} · error`, 'string', { defaultValue: '' }));
  }

  if (sourceNode.data.tipo === 'accion_http') {
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.ok`, `${nodeLabel} · HTTP ok`, 'boolean', { defaultValue: true }));
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.status_code`, `${nodeLabel} · status code`, 'number', { defaultValue: 200 }));
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.reason`, `${nodeLabel} · motivo`, 'string', { defaultValue: '' }));
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.body`, `${nodeLabel} · body`, 'string', { defaultValue: '' }));
    suggestions.push(createConditionSuggestion(`acciones.${sourceNode.id}.error`, `${nodeLabel} · error`, 'string', { defaultValue: '' }));
  }

  return Array.from(
    suggestions.reduce((accumulator, suggestion) => {
      if (!accumulator.has(suggestion.path)) {
        accumulator.set(suggestion.path, suggestion);
      }
      return accumulator;
    }, new Map()).values(),
  );
}

function coerceConditionForSuggestion(condition, suggestion) {
  const nextCondition = {
    ...(condition || {}),
    operador: condition?.operador || '==',
  };

  if (!suggestion) {
    return {
      ...nextCondition,
      valor: nextCondition.valor ?? '',
    };
  }

  nextCondition.campo = suggestion.path;

  if (suggestion.valueType === 'boolean') {
    return {
      ...nextCondition,
      operador: '==',
      valor: typeof nextCondition.valor === 'boolean' ? nextCondition.valor : (suggestion.defaultValue ?? true),
    };
  }

  if (suggestion.valueType === 'number') {
    const numericValue = typeof nextCondition.valor === 'number' ? nextCondition.valor : Number(nextCondition.valor);
    return {
      ...nextCondition,
      valor: Number.isFinite(numericValue) ? numericValue : (suggestion.defaultValue ?? 0),
    };
  }

  if (Array.isArray(suggestion.options) && suggestion.options.length > 0) {
    const optionValues = new Set(suggestion.options.map((option) => option.value));
    return {
      ...nextCondition,
      valor: optionValues.has(nextCondition.valor) ? nextCondition.valor : (suggestion.defaultValue ?? suggestion.options[0].value),
    };
  }

  return {
    ...nextCondition,
    valor: typeof nextCondition.valor === 'string' ? nextCondition.valor : (nextCondition.valor == null ? (suggestion.defaultValue ?? '') : String(nextCondition.valor)),
  };
}

function buildDefaultCondition(sourceNode, suggestions) {
  const formulario = sourceNode?.data?.config?.formulario;
  if (sourceNode?.data?.tipo === 'accion_humana' && formulario?.type === 'boolean_decision') {
    return {
      campo: formulario.field_name || 'aprobado',
      operador: '==',
      valor: true,
    };
  }

  if (suggestions.length > 0) {
    return coerceConditionForSuggestion({ campo: suggestions[0].path, operador: '==', valor: suggestions[0].defaultValue }, suggestions[0]);
  }

  return {
    campo: '',
    operador: '==',
    valor: '',
  };
}

function buildDefaultUiField(kind = 'text', index = 1) {
  if (kind === 'info') {
    return {
      id: `info_${index}`,
      kind,
      label: `Bloque informativo ${index}`,
      required: false,
      tone: 'info',
      content: 'Usá este bloque para mostrar contexto, instrucciones o advertencias dentro de la pantalla.',
    };
  }

  if (kind === 'summary') {
    return {
      id: `resumen_${index}`,
      kind,
      label: `Resumen ${index}`,
      required: false,
      items: [
        { label: 'DNI', value: '{{ ciudadano.dni }}' },
        { label: 'Programa', value: '{{ programa.codigo }}' },
        { label: 'Estado', value: 'En revision' },
      ],
      empty_message: 'Sin indicadores para mostrar.',
    };
  }

  if (kind === 'table') {
    return {
      id: `tabla_${index}`,
      kind,
      label: index === 1 ? 'Datos principales' : `Datos principales ${index}`,
      required: false,
      table_mode: 'simple',
      columns: cloneUiValue(SIMPLE_TABLE_COLUMNS),
      rows: [
        { campo: 'DNI', valor: '{{ ciudadano.dni }}' },
        { campo: 'Programa', valor: '{{ programa.codigo }}' },
      ],
      empty_message: 'Sin datos para mostrar.',
    };
  }

  const field = {
    id: `campo_${index}`,
    kind,
    label: `Campo ${index}`,
    required: false,
  };

  if (kind === 'textarea') {
    field.rows = 4;
  }

  if (kind === 'radio' || kind === 'select') {
    field.options = [
      { value: 'opcion_1', label: 'Opcion 1' },
      { value: 'opcion_2', label: 'Opcion 2' },
    ];
  }

  return field;
}

function buildDefaultUiConfig(type = 'form') {
  if (type !== 'form') {
    return null;
  }

  return {
    type,
    title: 'Vista operativa',
    description: 'Completá la información necesaria para continuar el flujo.',
    layout: 'single_column',
    sections: [
      {
        id: 'principal',
        title: 'Datos principales',
        fields: [buildDefaultUiField('text', 1)],
      },
    ],
    submit: {
      label: 'Guardar y continuar',
    },
  };
}

function getUiTableMode(field) {
  if (field?.table_mode === 'advanced' || field?.table_mode === 'simple') {
    return field.table_mode;
  }

  return Array.isArray(field?.columns) && field.columns.length > 2 ? 'advanced' : 'simple';
}

function buildSimpleTableRows(field) {
  const defaultTable = buildDefaultUiField('table', 1);
  const currentColumns = Array.isArray(field?.columns) && field.columns.length > 0
    ? field.columns
    : defaultTable.columns;
  const primaryKey = currentColumns[0]?.key || defaultTable.columns[0].key;
  const valueKey = currentColumns[1]?.key || defaultTable.columns[1].key;
  const rows = Array.isArray(field?.rows) ? field.rows : [];

  if (rows.length === 0) {
    return [];
  }

  return rows.map((row) => ({
    campo: row?.campo ?? row?.[primaryKey] ?? '',
    valor: row?.valor ?? row?.[valueKey] ?? '',
  }));
}

function coerceUiTableToSimple(field, index = 1) {
  const defaultTable = buildDefaultUiField('table', index);
  const nextRows = Array.isArray(field?.rows) && field.rows.length > 0
    ? buildSimpleTableRows(field)
    : cloneUiValue(defaultTable.rows);

  return {
    ...field,
    kind: 'table',
    required: false,
    table_mode: 'simple',
    columns: cloneUiValue(SIMPLE_TABLE_COLUMNS),
    rows: nextRows,
    empty_message: field?.empty_message || defaultTable.empty_message,
  };
}

function cloneUiValue(value) {
  return JSON.parse(JSON.stringify(value));
}

function normalizeUiIdentifier(value, fallback = 'item') {
  const normalized = String(value || fallback)
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, '_')
    .replace(/^_+|_+$/g, '');

  return normalized || fallback;
}

function buildUniqueUiIdentifier(baseValue, existingIds, fallback = 'item') {
  const baseId = normalizeUiIdentifier(baseValue, fallback);
  if (!existingIds.has(baseId)) {
    return baseId;
  }

  let suffix = 2;
  while (existingIds.has(`${baseId}_${suffix}`)) {
    suffix += 1;
  }
  return `${baseId}_${suffix}`;
}

function moveArrayItem(items, fromIndex, toIndex) {
  const nextItems = [...items];
  const [item] = nextItems.splice(fromIndex, 1);
  nextItems.splice(toIndex, 0, item);
  return nextItems;
}

function buildUiSectionCollapseKey(nodeId, section, sectionIndex) {
  return `${nodeId}::section::${section?.id || sectionIndex}`;
}

function buildUiFieldCollapseKey(nodeId, section, sectionIndex, field, fieldIndex) {
  return `${nodeId}::field::${section?.id || sectionIndex}::${field?.id || fieldIndex}`;
}

function getUiFieldKindLabel(kind) {
  return UI_FIELD_KIND_OPTIONS.find((option) => option.value === kind)?.label || kind || 'Campo';
}

function getUiBlockTypeValue(field) {
  return field?.kind || 'text';
}

function getUiBlockTypeLabel(field) {
  return UI_BLOCK_TYPE_OPTIONS.find((option) => option.value === getUiBlockTypeValue(field))?.label
    || getUiFieldKindLabel(field?.kind);
}

const INFO_TONE_LABEL = {
  info: 'info',
  success: 'éxito',
  warning: 'advertencia',
  danger: 'alerta',
  neutral: 'neutral',
};

function pluralize(count, singular, plural) {
  return `${count} ${count === 1 ? singular : plural}`;
}

function getUiBlockSummary(field) {
  const baseLabel = getUiBlockTypeLabel(field);

  if (field?.kind === 'table') {
    const mode = getUiTableMode(field);
    const rowCount = Array.isArray(field?.rows) ? field.rows.length : 0;
    if (mode === 'simple') {
      return `Tabla simple · ${pluralize(rowCount, 'fila', 'filas')}`;
    }
    const colCount = Array.isArray(field?.columns) ? field.columns.length : 0;
    return `Tabla avanzada · ${pluralize(colCount, 'columna', 'columnas')} × ${pluralize(rowCount, 'fila', 'filas')}`;
  }

  if (field?.kind === 'info') {
    return `Info · ${INFO_TONE_LABEL[field.tone] || field.tone || 'info'}`;
  }

  if (field?.kind === 'summary') {
    const itemCount = Array.isArray(field?.items) ? field.items.length : 0;
    return `Resumen · ${pluralize(itemCount, 'ítem', 'ítems')}`;
  }

  if (field?.kind === 'radio' || field?.kind === 'select') {
    const opts = Array.isArray(field?.options) ? field.options.length : 0;
    const required = field?.required ? ' · obligatorio' : '';
    return `${baseLabel} · ${pluralize(opts, 'opción', 'opciones')}${required}`;
  }

  if (field?.kind === 'checkbox') {
    return `${baseLabel}${field?.required ? ' · obligatorio' : ''}`;
  }

  return `${baseLabel}${field?.required ? ' · obligatorio' : ''}`;
}

function getUiSectionSummary(section) {
  const count = (section?.fields || []).length;
  if (count === 0) return 'Sin bloques';
  return pluralize(count, 'bloque', 'bloques');
}

function buildDefaultActor() {
  return {
    mode: 'group',
    value: 'programaOperar',
  };
}

function buildDefaultFormConfig(type) {
  if (type === 'boolean_decision') {
    return {
      type,
      field_name: 'aprobado',
      field_label: 'Resultado',
      true_label: 'Aprobar',
      false_label: 'Rechazar',
      include_observacion: true,
      observacion_label: 'Observacion',
      observacion_required: false,
    };
  }

  if (type === 'text_input') {
    return {
      type,
      field_name: 'detalle',
      field_label: 'Detalle',
      placeholder: 'Escribi el detalle',
      help_text: '',
      required: true,
      multiline: true,
      rows: 4,
    };
  }

  if (type === 'choice_select') {
    return {
      type,
      field_name: 'resultado',
      field_label: 'Resultado',
      placeholder: 'Seleccionar una opcion',
      help_text: '',
      required: true,
      options: [
        { value: 'opcion_1', label: 'Opcion 1' },
        { value: 'opcion_2', label: 'Opcion 2' },
      ],
    };
  }

  return null;
}

function buildDefaultEmailActionConfig() {
  return {
    to: ['{{ ciudadano.email }}'],
    subject: 'Actualización de {{ programa.nombre }}',
    body: 'Hola {{ ciudadano.nombre_completo }},\n\nTu caso en {{ programa.nombre }} fue actualizado.',
  };
}

function buildDefaultHttpActionConfig() {
  return {
    method: 'POST',
    url: 'https://example.com/api/flujo',
    headers: [
      { key: 'Content-Type', value: 'application/json' },
    ],
    body: '{"programa": "{{ programa.codigo }}", "ciudadano": "{{ ciudadano.dni }}"}',
    timeout_seconds: 10,
  };
}

function buildNodeConfigTabs(nodeType, hasDeclarativeUi) {
  const tabs = [{ id: 'general', label: 'General' }];

  if (nodeType === 'accion_humana') {
    tabs.push({ id: 'operativa', label: 'Operativa' });
    if (hasDeclarativeUi) {
      tabs.push({ id: 'pantalla', label: 'Interfaz' });
    }
  }

  if (nodeType === 'accion_email' || nodeType === 'accion_http') {
    tabs.push({ id: 'automatizacion', label: 'Automatización' });
  }

  return tabs;
}

export default function PropertiesPanel({ selectedNode, selectedEdge, nodes, onUpdateNode, onUpdateEdge, presentation = 'sidebar', roles = [] }) {
  const [expandedSectionKey, setExpandedSectionKey] = useState(null);
  const [expandedFieldKey, setExpandedFieldKey] = useState(null);
  const [activeNodeConfigTab, setActiveNodeConfigTab] = useState('general');
  const isModalPresentation = presentation === 'modal';
  const panelClassName = isModalPresentation ? 'flow-panel flow-modal-panel' : 'flow-panel flow-side-panel';
  const propertiesClassName = isModalPresentation ? 'flow-properties flow-properties--modal' : 'flow-properties';

  const selectedNodeType = selectedNode?.data?.tipo || '';
  const hasDeclarativeUi = Boolean(selectedNode?.data?.config?.ui);
  const selectedNodeId = selectedNode?.id;
  const firstSectionKey = selectedNodeId && selectedNode?.data?.config?.ui?.sections?.length
    ? buildUiSectionCollapseKey(selectedNodeId, selectedNode.data.config.ui.sections[0], 0)
    : null;

  useEffect(() => {
    if (presentation !== 'modal' || !selectedNode) {
      if (activeNodeConfigTab !== 'general') {
        setActiveNodeConfigTab('general');
      }
      return;
    }

    const availableTabs = buildNodeConfigTabs(selectedNodeType, hasDeclarativeUi).map((tab) => tab.id);
    if (!availableTabs.includes(activeNodeConfigTab)) {
      setActiveNodeConfigTab(availableTabs[0] || 'general');
    }
  }, [presentation, selectedNode, selectedNodeType, hasDeclarativeUi, activeNodeConfigTab]);

  useEffect(() => {
    setExpandedSectionKey(firstSectionKey);
    setExpandedFieldKey(null);
  }, [selectedNodeId, firstSectionKey]);

  if (!selectedNode && !selectedEdge) {
    return (
      <aside className={panelClassName}>
        <div className={propertiesClassName}>
          <div className="flow-panel-kicker">Inspector</div>
          <div className="flow-empty-panel">
            <strong>Seleccioná un elemento</strong>
            Elegí un nodo o una conexión para editar nombre, instrucciones, formularios y condiciones desde este panel.
          </div>
        </div>
      </aside>
    );
  }

  if (selectedNode) {
    const { data } = selectedNode;
    const nodeConfig = data.config || {};
    const formulario = nodeConfig.formulario || null;
    const uiConfig = nodeConfig.ui || null;
    const emailConfig = nodeConfig.email || null;
    const httpConfig = nodeConfig.http || null;
    const actor = data.actor || null;
    const surface = Array.isArray(data.surface) ? data.surface : [];
    const contractMode = uiConfig ? 'ui_form' : (formulario ? 'legacy_form' : '');
    const nodeTabs = presentation === 'modal'
      ? buildNodeConfigTabs(data.tipo, Boolean(uiConfig))
      : [];
    const showGeneralTab = presentation !== 'modal' || activeNodeConfigTab === 'general';
    const showOperativeTab = presentation !== 'modal' || activeNodeConfigTab === 'operativa';
    const showScreenTab = presentation !== 'modal' || activeNodeConfigTab === 'pantalla';
    const showAutomationTab = presentation !== 'modal' || activeNodeConfigTab === 'automatizacion';
    const getSectionCollapseKey = (section, sectionIndex) => buildUiSectionCollapseKey(selectedNode.id, section, sectionIndex);
    const getFieldCollapseKey = (section, sectionIndex, field, fieldIndex) => (
      buildUiFieldCollapseKey(selectedNode.id, section, sectionIndex, field, fieldIndex)
    );
    const uiPanelSectionStyle = isModalPresentation
      ? { ...sectionStyle, marginTop: 14, paddingTop: 10 }
      : sectionStyle;
    const uiPanelSectionTitleStyle = isModalPresentation
      ? { ...sectionTitleStyle, fontSize: 10, marginBottom: 8 }
      : sectionTitleStyle;
    const uiLabelStyle = isModalPresentation
      ? { ...labelStyle, fontSize: 10, marginTop: 10, marginBottom: 4 }
      : labelStyle;
    const uiInputStyle = isModalPresentation
      ? { ...inputStyle, padding: '8px 10px', fontSize: 12, borderRadius: 8 }
      : inputStyle;
    const uiCheckLabelStyle = isModalPresentation
      ? { ...checkLabelStyle, gap: 6, fontSize: 11, marginTop: 10 }
      : checkLabelStyle;
    const uiTwoColumnsStyle = isModalPresentation
      ? { ...twoColumnsStyle, gap: 8 }
      : twoColumnsStyle;
    const uiOptionCardStyle = isModalPresentation
      ? { ...optionCardStyle, padding: 10, marginTop: 8, borderRadius: 10 }
      : optionCardStyle;
    const uiSecondaryBtnStyle = isModalPresentation
      ? { ...secondaryBtnStyle, marginTop: 10, padding: '8px 10px', fontSize: 11, borderRadius: 8 }
      : secondaryBtnStyle;
    const uiCompactSecondaryBtnStyle = isModalPresentation
      ? { ...compactSecondaryBtnStyle, padding: '6px 9px', fontSize: 10, borderRadius: 8 }
      : compactSecondaryBtnStyle;
    const uiRemoveBtnStyle = isModalPresentation
      ? { ...removeBtnStyle, marginTop: 10, padding: '8px 10px', fontSize: 11, borderRadius: 8 }
      : removeBtnStyle;
    const uiHintStyle = isModalPresentation
      ? { ...hintStyle, marginTop: 10, padding: '8px 10px', fontSize: 10, borderRadius: 10 }
      : hintStyle;
    const uiInlineActionsStyle = isModalPresentation
      ? { ...inlineActionsStyle, gap: 6, marginBottom: 6 }
      : inlineActionsStyle;
    const uiCollapsibleHeaderStyle = isModalPresentation
      ? { ...collapsibleHeaderStyle, gap: 8, marginBottom: 6 }
      : collapsibleHeaderStyle;
    const uiCollapsibleTitleStyle = isModalPresentation
      ? { ...collapsibleTitleStyle, fontSize: 12 }
      : collapsibleTitleStyle;
    const uiCollapsibleMetaStyle = isModalPresentation
      ? { ...collapsibleMetaStyle, fontSize: 10 }
      : collapsibleMetaStyle;
    const uiCompactGhostBtnStyle = isModalPresentation
      ? { ...compactGhostBtnStyle, padding: '5px 9px', fontSize: 10 }
      : compactGhostBtnStyle;
    const uiTableHelpStyle = isModalPresentation
      ? {
          ...hintStyle,
          marginTop: 8,
          marginBottom: 10,
          padding: '8px 10px',
          fontSize: 10,
          borderRadius: 10,
          background: '#f8fafc',
          border: '1px solid #dbe4ef',
        }
      : {
          ...hintStyle,
          marginTop: 8,
          marginBottom: 10,
          background: '#f8fafc',
          border: '1px solid #dbe4ef',
        };
    const uiTableHelpTitleStyle = {
      display: 'block',
      marginBottom: 4,
      fontWeight: 700,
      color: '#0f172a',
    };
    const uiTableMicrocopyStyle = {
      marginTop: 6,
      fontSize: isModalPresentation ? 10 : 11,
      color: '#64748b',
      lineHeight: 1.5,
    };
    const uiTableEscapeHatchStyle = {
      marginTop: 12,
      paddingTop: 10,
      borderTop: '1px dashed #dbe4ef',
      fontSize: isModalPresentation ? 10 : 11,
      color: '#64748b',
      lineHeight: 1.5,
    };
    const uiInlineLinkBtnStyle = {
      background: 'transparent',
      border: 'none',
      padding: 0,
      color: '#1d4ed8',
      fontSize: 'inherit',
      fontWeight: 600,
      textDecoration: 'underline',
      cursor: 'pointer',
    };
    const uiAdvancedBannerStyle = {
      marginTop: 8,
      marginBottom: 4,
      padding: isModalPresentation ? '8px 10px' : '10px 12px',
      borderRadius: 10,
      background: '#eef2ff',
      border: '1px solid #c7d2fe',
      color: '#1e3a8a',
      fontSize: isModalPresentation ? 11 : 12,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: 10,
      flexWrap: 'wrap',
    };
    const uiTemplateChipsStyle = {
      display: 'flex',
      flexWrap: 'wrap',
      gap: 6,
      marginTop: 8,
      marginBottom: 4,
    };
    const uiTemplateChipStyle = {
      padding: isModalPresentation ? '6px 10px' : '7px 12px',
      borderRadius: 999,
      border: '1px solid #c7d2fe',
      background: '#eef2ff',
      color: '#1e3a8a',
      fontSize: isModalPresentation ? 10 : 11,
      fontWeight: 600,
      cursor: 'pointer',
      whiteSpace: 'nowrap',
      transition: 'background 0.15s',
    };
    const uiTemplateClearChipStyle = {
      ...uiTemplateChipStyle,
      background: '#fff',
      borderColor: '#dbe4ef',
      color: '#475569',
    };
    const updateNodeConfig = (patch) => {
      onUpdateNode(selectedNode.id, { config: { ...nodeConfig, ...patch } });
    };
    const updateNodeData = (patch) => {
      onUpdateNode(selectedNode.id, patch);
    };
    const updateFormulario = (patch) => {
      updateNodeConfig({ formulario: { ...(formulario || {}), ...patch } });
    };
    const updateOption = (optionIndex, patch) => {
      const options = (formulario?.options || []).map((opcion, index) => (
        index === optionIndex ? { ...opcion, ...patch } : opcion
      ));
      updateFormulario({ options });
    };
    const addOption = () => {
      const nextOptions = [
        ...(formulario?.options || []),
        { value: `opcion_${(formulario?.options || []).length + 1}`, label: `Opcion ${(formulario?.options || []).length + 1}` },
      ];
      updateFormulario({ options: nextOptions });
    };
    const removeOption = (optionIndex) => {
      const nextOptions = (formulario?.options || []).filter((_, index) => index !== optionIndex);
      updateFormulario({ options: nextOptions });
    };
    const updateUiConfig = (patch) => {
      updateNodeConfig({ ui: { ...(uiConfig || buildDefaultUiConfig('form')), ...patch } });
    };
    const updateEmailConfig = (patch) => {
      updateNodeConfig({ email: { ...(emailConfig || buildDefaultEmailActionConfig()), ...patch } });
    };
    const updateHttpConfig = (patch) => {
      updateNodeConfig({ http: { ...(httpConfig || buildDefaultHttpActionConfig()), ...patch } });
    };
    const updateEmailRecipient = (recipientIndex, value) => {
      const nextRecipients = (emailConfig?.to || []).map((recipient, index) => (
        index === recipientIndex ? value : recipient
      ));
      updateEmailConfig({ to: nextRecipients });
    };
    const addEmailRecipient = () => {
      updateEmailConfig({ to: [...(emailConfig?.to || []), ''] });
    };
    const removeEmailRecipient = (recipientIndex) => {
      const nextRecipients = (emailConfig?.to || []).filter((_, index) => index !== recipientIndex);
      updateEmailConfig({ to: nextRecipients.length > 0 ? nextRecipients : [''] });
    };
    const updateHttpHeader = (headerIndex, patch) => {
      const nextHeaders = (httpConfig?.headers || []).map((header, index) => (
        index === headerIndex ? { ...header, ...patch } : header
      ));
      updateHttpConfig({ headers: nextHeaders });
    };
    const addHttpHeader = () => {
      updateHttpConfig({ headers: [...(httpConfig?.headers || []), { key: '', value: '' }] });
    };
    const removeHttpHeader = (headerIndex) => {
      const nextHeaders = (httpConfig?.headers || []).filter((_, index) => index !== headerIndex);
      updateHttpConfig({ headers: nextHeaders });
    };
    const setContractMode = (mode) => {
      if (mode === 'legacy_form') {
        updateNodeData({
          actor: null,
          surface: [],
          config: {
            ...nodeConfig,
            ui: null,
            formulario: formulario || buildDefaultFormConfig('boolean_decision'),
          },
        });
        return;
      }

      if (mode === 'ui_form') {
        updateNodeData({
          actor: actor || buildDefaultActor(),
          surface: surface.length ? surface : ['backoffice'],
          config: {
            ...nodeConfig,
            formulario: null,
            ui: uiConfig || buildDefaultUiConfig('form'),
          },
        });
        return;
      }

      updateNodeData({
        actor: null,
        surface: [],
        config: {
          ...nodeConfig,
          formulario: null,
          ui: null,
        },
      });
    };
    const updateUiSection = (sectionIndex, patch) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => (
        index === sectionIndex ? { ...section, ...patch } : section
      ));
      updateUiConfig({ sections: nextSections });
    };
    const addUiSection = () => {
      const sections = uiConfig?.sections || [];
      const newIndex = sections.length;
      const newSection = {
        id: `seccion_${newIndex + 1}`,
        title: `Seccion ${newIndex + 1}`,
        fields: [buildDefaultUiField('text', 1)],
      };
      updateUiConfig({ sections: [...sections, newSection] });
      setExpandedSectionKey(buildUiSectionCollapseKey(selectedNode.id, newSection, newIndex));
      setExpandedFieldKey(null);
    };
    const removeUiSection = (sectionIndex) => {
      const nextSections = (uiConfig?.sections || []).filter((_, index) => index !== sectionIndex);
      updateUiConfig({ sections: nextSections.length > 0 ? nextSections : [
        {
          id: 'principal',
          title: 'Datos principales',
          fields: [buildDefaultUiField('text', 1)],
        },
      ] });
    };
    const selectUiSection = (section, sectionIndex) => {
      const key = getSectionCollapseKey(section, sectionIndex);
      setExpandedSectionKey((current) => (current === key ? null : key));
      setExpandedFieldKey(null);
    };
    const closeAllUi = () => {
      setExpandedSectionKey(null);
      setExpandedFieldKey(null);
    };
    const moveUiSection = (sectionIndex, direction) => {
      const sections = uiConfig?.sections || [];
      const targetIndex = sectionIndex + direction;
      if (targetIndex < 0 || targetIndex >= sections.length) {
        return;
      }
      updateUiConfig({ sections: moveArrayItem(sections, sectionIndex, targetIndex) });
    };
    const duplicateUiSection = (sectionIndex) => {
      const sections = uiConfig?.sections || [];
      const section = sections[sectionIndex];
      if (!section) {
        return;
      }

      const duplicatedSection = cloneUiValue(section);
      const sectionIds = new Set(sections.map((item) => item.id).filter(Boolean));
      const fieldIds = new Set(
        sections.flatMap((item) => (item.fields || []).map((field) => field.id).filter(Boolean)),
      );

      duplicatedSection.id = buildUniqueUiIdentifier(`${section.id || `seccion_${sectionIndex + 1}`}_copia`, sectionIds, 'seccion');
      duplicatedSection.title = section.title ? `${section.title} copia` : `Seccion ${sectionIndex + 2}`;
      duplicatedSection.fields = (duplicatedSection.fields || []).map((field, fieldIndex) => {
        const duplicatedField = cloneUiValue(field);
        duplicatedField.id = buildUniqueUiIdentifier(`${field.id || `campo_${fieldIndex + 1}`}_copia`, fieldIds, 'campo');
        fieldIds.add(duplicatedField.id);
        if (duplicatedField.label) {
          duplicatedField.label = `${duplicatedField.label} copia`;
        }
        return duplicatedField;
      });

      const nextSections = [...sections];
      nextSections.splice(sectionIndex + 1, 0, duplicatedSection);
      updateUiConfig({ sections: nextSections });
    };
    const updateUiField = (sectionIndex, fieldIndex, patch) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const nextField = { ...field, ...patch };
            if (nextField.kind === 'info') {
              nextField.required = false;
              nextField.tone = nextField.tone || 'info';
              nextField.content = typeof nextField.content === 'string'
                ? nextField.content
                : buildDefaultUiField('info', fieldIndex + 1).content;
              delete nextField.placeholder;
              delete nextField.help_text;
              delete nextField.items;
              delete nextField.columns;
              delete nextField.empty_message;
              if (Array.isArray(nextField.rows)) {
                delete nextField.rows;
              }
            }
            if (nextField.kind === 'summary') {
              const defaultSummary = buildDefaultUiField('summary', fieldIndex + 1);
              nextField.required = false;
              nextField.items = Array.isArray(nextField.items) && nextField.items.length > 0
                ? nextField.items
                : defaultSummary.items;
              nextField.empty_message = nextField.empty_message || defaultSummary.empty_message;
              delete nextField.placeholder;
              delete nextField.help_text;
              delete nextField.content;
              delete nextField.tone;
              delete nextField.columns;
              if (Array.isArray(nextField.rows)) {
                delete nextField.rows;
              }
            }
            if (nextField.kind === 'table') {
              const defaultTable = buildDefaultUiField('table', fieldIndex + 1);
              nextField.required = false;
              nextField.table_mode = getUiTableMode(nextField);
              nextField.columns = Array.isArray(nextField.columns) && nextField.columns.length > 0
                ? nextField.columns
                : defaultTable.columns;
              nextField.rows = Array.isArray(nextField.rows)
                ? nextField.rows
                : defaultTable.rows;
              nextField.empty_message = nextField.empty_message || defaultTable.empty_message;
              delete nextField.placeholder;
              delete nextField.help_text;
              delete nextField.content;
              delete nextField.tone;
              delete nextField.items;
              if (nextField.table_mode !== 'advanced') {
                Object.assign(nextField, coerceUiTableToSimple(nextField, fieldIndex + 1));
              }
            }
            if (nextField.kind !== 'textarea' && nextField.kind !== 'table') {
              delete nextField.rows;
            }
            if (!['radio', 'select'].includes(nextField.kind)) {
              delete nextField.options;
            } else if (!Array.isArray(nextField.options) || nextField.options.length === 0) {
              nextField.options = buildDefaultUiField(nextField.kind, fieldIndex + 1).options;
            }
            if (!DISPLAY_ONLY_UI_FIELD_KINDS.has(nextField.kind)) {
              delete nextField.content;
              delete nextField.tone;
              delete nextField.columns;
              delete nextField.empty_message;
              delete nextField.items;
            }
            if (nextField.kind !== 'table') {
              delete nextField.table_mode;
            }
            return nextField;
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const addUiField = (sectionIndex, kind = 'text') => {
      const sections = uiConfig?.sections || [];
      const targetSection = sections[sectionIndex];
      const fields = targetSection?.fields || [];
      const newField = buildDefaultUiField(kind, fields.length + 1);
      const newFieldIndex = fields.length;

      const nextSections = sections.map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: [...(section.fields || []), newField],
        };
      });
      updateUiConfig({ sections: nextSections });

      if (targetSection) {
        setExpandedSectionKey(buildUiSectionCollapseKey(selectedNode.id, targetSection, sectionIndex));
        setExpandedFieldKey(buildUiFieldCollapseKey(selectedNode.id, targetSection, sectionIndex, newField, newFieldIndex));
      }
    };
    const removeUiField = (sectionIndex, fieldIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        const remainingFields = (section.fields || []).filter((_, innerIndex) => innerIndex !== fieldIndex);
        return {
          ...section,
          fields: remainingFields.length > 0 ? remainingFields : [buildDefaultUiField('text', 1)],
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const selectUiField = (section, sectionIndex, field, fieldIndex) => {
      const key = getFieldCollapseKey(section, sectionIndex, field, fieldIndex);
      setExpandedFieldKey((current) => (current === key ? null : key));
    };
    const moveUiField = (sectionIndex, fieldIndex, direction) => {
      const sections = uiConfig?.sections || [];
      const section = sections[sectionIndex];
      const fields = section?.fields || [];
      const targetIndex = fieldIndex + direction;
      if (targetIndex < 0 || targetIndex >= fields.length) {
        return;
      }

      const nextSections = sections.map((currentSection, index) => {
        if (index !== sectionIndex) {
          return currentSection;
        }
        return {
          ...currentSection,
          fields: moveArrayItem(fields, fieldIndex, targetIndex),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const duplicateUiField = (sectionIndex, fieldIndex) => {
      const sections = uiConfig?.sections || [];
      const section = sections[sectionIndex];
      const field = section?.fields?.[fieldIndex];
      if (!field) {
        return;
      }

      const fieldIds = new Set(
        sections.flatMap((item) => (item.fields || []).map((currentField) => currentField.id).filter(Boolean)),
      );

      const duplicatedField = cloneUiValue(field);
      duplicatedField.id = buildUniqueUiIdentifier(`${field.id || `campo_${fieldIndex + 1}`}_copia`, fieldIds, 'campo');
      if (duplicatedField.label) {
        duplicatedField.label = `${duplicatedField.label} copia`;
      }

      const nextSections = sections.map((currentSection, index) => {
        if (index !== sectionIndex) {
          return currentSection;
        }
        const nextFields = [...(currentSection.fields || [])];
        nextFields.splice(fieldIndex + 1, 0, duplicatedField);
        return {
          ...currentSection,
          fields: nextFields,
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const updateUiOption = (sectionIndex, fieldIndex, optionIndex, patch) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            return {
              ...field,
              options: (field.options || []).map((option, optionInnerIndex) => (
                optionInnerIndex === optionIndex ? { ...option, ...patch } : option
              )),
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const addUiOption = (sectionIndex, fieldIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            return {
              ...field,
              options: [
                ...(field.options || []),
                { value: `opcion_${(field.options || []).length + 1}`, label: `Opcion ${(field.options || []).length + 1}` },
              ],
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const removeUiOption = (sectionIndex, fieldIndex, optionIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const remainingOptions = (field.options || []).filter((_, optionInnerIndex) => optionInnerIndex !== optionIndex);
            return {
              ...field,
              options: remainingOptions.length > 0 ? remainingOptions : [
                { value: 'opcion_1', label: 'Opcion 1' },
                { value: 'opcion_2', label: 'Opcion 2' },
              ],
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const updateUiSummaryItem = (sectionIndex, fieldIndex, itemIndex, patch) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            return {
              ...field,
              items: (field.items || []).map((item, innerItemIndex) => (
                innerItemIndex === itemIndex ? { ...item, ...patch } : item
              )),
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const addUiSummaryItem = (sectionIndex, fieldIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            return {
              ...field,
              items: [
                ...(field.items || []),
                { label: `Dato ${(field.items || []).length + 1}`, value: '' },
              ],
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const removeUiSummaryItem = (sectionIndex, fieldIndex, itemIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const remainingItems = (field.items || []).filter((_, innerItemIndex) => innerItemIndex !== itemIndex);
            return {
              ...field,
              items: remainingItems.length > 0 ? remainingItems : buildDefaultUiField('summary', fieldIndex + 1).items,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const updateUiTableColumn = (sectionIndex, fieldIndex, columnIndex, patch) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const previousColumn = field.columns?.[columnIndex] || { key: '', label: '' };
            const nextColumn = { ...previousColumn, ...patch };
            const nextColumns = (field.columns || []).map((column, innerColumnIndex) => (
              innerColumnIndex === columnIndex ? nextColumn : column
            ));
            const nextRows = (field.rows || []).map((row) => {
              if (!patch.key || patch.key === previousColumn.key) {
                return row;
              }
              const nextRow = { ...row };
              nextRow[patch.key] = row[previousColumn.key] ?? '';
              delete nextRow[previousColumn.key];
              return nextRow;
            });
            return {
              ...field,
              columns: nextColumns,
              rows: nextRows,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const addUiTableColumn = (sectionIndex, fieldIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const nextKey = `columna_${(field.columns || []).length + 1}`;
            const nextColumns = [
              ...(field.columns || []),
              { key: nextKey, label: `Columna ${(field.columns || []).length + 1}` },
            ];
            const nextRows = (field.rows || []).map((row) => ({
              ...row,
              [nextKey]: '',
            }));
            return {
              ...field,
              columns: nextColumns,
              rows: nextRows,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const removeUiTableColumn = (sectionIndex, fieldIndex, columnIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const currentColumns = field.columns || [];
            const nextColumns = currentColumns.filter((_, innerColumnIndex) => innerColumnIndex !== columnIndex);
            if (nextColumns.length === 0) {
              const fallbackField = buildDefaultUiField('table', fieldIndex + 1);
              return {
                ...field,
                columns: fallbackField.columns,
                rows: fallbackField.rows,
              };
            }
            const removedKey = currentColumns[columnIndex]?.key;
            const nextRows = (field.rows || []).map((row) => {
              const nextRow = { ...row };
              delete nextRow[removedKey];
              return nextRow;
            });
            return {
              ...field,
              columns: nextColumns,
              rows: nextRows,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const updateUiTableCell = (sectionIndex, fieldIndex, rowIndex, columnKey, value) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const nextRows = (field.rows || []).map((row, innerRowIndex) => (
              innerRowIndex === rowIndex ? { ...row, [columnKey]: value } : row
            ));
            return {
              ...field,
              rows: nextRows,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const addUiTableRow = (sectionIndex, fieldIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const nextRow = Object.fromEntries((field.columns || []).map((column) => [column.key, '']));
            return {
              ...field,
              rows: [
                ...(field.rows || []),
                nextRow,
              ],
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const removeUiTableRow = (sectionIndex, fieldIndex, rowIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const nextRows = (field.rows || []).filter((_, innerRowIndex) => innerRowIndex !== rowIndex);
            return {
              ...field,
              rows: nextRows,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const setUiTableMode = (sectionIndex, fieldIndex, mode) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const defaultTable = buildDefaultUiField('table', fieldIndex + 1);
            if (mode === 'simple') {
              return coerceUiTableToSimple({ ...field, table_mode: 'simple' }, fieldIndex + 1);
            }
            return {
              ...field,
              kind: 'table',
              required: false,
              table_mode: 'advanced',
              columns: Array.isArray(field.columns) && field.columns.length > 0
                ? field.columns
                : defaultTable.columns,
              rows: Array.isArray(field.rows)
                ? field.rows
                : defaultTable.rows,
              empty_message: field.empty_message || defaultTable.empty_message,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const updateUiSimpleTableRow = (sectionIndex, fieldIndex, rowIndex, patch) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const normalizedField = coerceUiTableToSimple(field, fieldIndex + 1);
            return {
              ...normalizedField,
              rows: normalizedField.rows.map((row, innerRowIndex) => (
                innerRowIndex === rowIndex ? { ...row, ...patch } : row
              )),
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const addUiSimpleTableRow = (sectionIndex, fieldIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const normalizedField = coerceUiTableToSimple(field, fieldIndex + 1);
            return {
              ...normalizedField,
              rows: [...normalizedField.rows, { campo: '', valor: '' }],
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const appendUiSimpleTableRows = (sectionIndex, fieldIndex, rowsToAppend) => {
      if (!Array.isArray(rowsToAppend) || rowsToAppend.length === 0) {
        return;
      }
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const normalizedField = coerceUiTableToSimple(field, fieldIndex + 1);
            const incoming = rowsToAppend.map((row) => ({
              campo: row?.campo || '',
              valor: row?.valor || '',
            }));
            return {
              ...normalizedField,
              rows: [...normalizedField.rows, ...incoming],
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const replaceUiSimpleTableRows = (sectionIndex, fieldIndex, rowsToSet) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const normalizedField = coerceUiTableToSimple(field, fieldIndex + 1);
            const nextRows = (Array.isArray(rowsToSet) ? rowsToSet : []).map((row) => ({
              campo: row?.campo || '',
              valor: row?.valor || '',
            }));
            return {
              ...normalizedField,
              rows: nextRows,
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const removeUiSimpleTableRow = (sectionIndex, fieldIndex, rowIndex) => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: (section.fields || []).map((field, innerIndex) => {
            if (innerIndex !== fieldIndex) {
              return field;
            }
            const normalizedField = coerceUiTableToSimple(field, fieldIndex + 1);
            return {
              ...normalizedField,
              rows: normalizedField.rows.filter((_, innerRowIndex) => innerRowIndex !== rowIndex),
            };
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const updateUiBlockType = (sectionIndex, fieldIndex, nextType) => {
      updateUiField(sectionIndex, fieldIndex, { kind: nextType });
    };

    return (
      <aside className={panelClassName}>
        <div className={propertiesClassName}>
        <div className="flow-panel-kicker">Nodo</div>
        <h4 style={panelTitleStyle}>{data.tipo}</h4>
        <div style={panelIntroStyle}>Configurá el nombre visible, las instrucciones y el contrato operativo de este paso.</div>
        {presentation === 'modal' && nodeTabs.length > 1 && (
          <>
            <div style={tabListStyle}>
              {nodeTabs.map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  style={{
                    ...tabButtonStyle,
                    ...(activeNodeConfigTab === tab.id ? activeTabButtonStyle : {}),
                  }}
                  onClick={() => setActiveNodeConfigTab(tab.id)}
                >
                  {tab.label}
                </button>
              ))}
            </div>
            <div style={tabHintCardStyle}>
              {activeNodeConfigTab === 'general' && 'Datos base del paso: nombre, instrucciones e identificación interna.'}
              {activeNodeConfigTab === 'operativa' && 'Contrato operativo del paso: tipo de captura, grupo responsable y comportamiento de resolución.'}
              {activeNodeConfigTab === 'pantalla' && 'Composición de la interfaz: layout, vista previa, secciones y bloques visibles.'}
              {activeNodeConfigTab === 'automatizacion' && 'Configuración técnica de la acción automática y sus parámetros de ejecución.'}
            </div>
          </>
        )}
        {showGeneralTab && (
          <>
        <label style={labelStyle}>Nombre del paso</label>
        <input
          style={inputStyle}
          value={data.label || ''}
          onChange={(e) => onUpdateNode(selectedNode.id, { label: e.target.value })}
          placeholder="Ej: Evaluación inicial"
        />
        <label style={labelStyle}>Descripción / instrucciones</label>
        <textarea
          style={{ ...inputStyle, minHeight: 72, resize: 'vertical' }}
          value={data.descripcion || ''}
          onChange={(e) => onUpdateNode(selectedNode.id, { descripcion: e.target.value })}
          placeholder="Instrucciones para el operador..."
        />
        <div style={{ marginTop: 8, fontSize: 10, color: '#94a3b8' }}>
          ID interno: <code>{selectedNode.id}</code>
        </div>
          </>
        )}

        {data.tipo === 'accion_email' && showAutomationTab && (
          <div style={sectionStyle}>
            <div style={sectionTitleStyle}>Acción automática</div>
            <label style={labelStyle}>Destinatarios</label>
            {(emailConfig?.to || ['']).map((recipient, index) => (
              <div key={`recipient-${index}`} style={optionCardStyle}>
                <input
                  style={inputStyle}
                  value={recipient}
                  onChange={(e) => updateEmailRecipient(index, e.target.value)}
                  placeholder="{{ ciudadano.email }} o mail@dominio.com"
                />
                <button type="button" style={removeBtnStyle} onClick={() => removeEmailRecipient(index)}>
                  Quitar destinatario
                </button>
              </div>
            ))}
            <button type="button" style={secondaryBtnStyle} onClick={addEmailRecipient}>
              Agregar destinatario
            </button>

            <label style={labelStyle}>Asunto</label>
            <input
              style={inputStyle}
              value={emailConfig?.subject || ''}
              onChange={(e) => updateEmailConfig({ subject: e.target.value })}
              placeholder="Actualización de {{ programa.nombre }}"
            />

            <label style={labelStyle}>Cuerpo</label>
            <textarea
              style={{ ...inputStyle, minHeight: 120, resize: 'vertical' }}
              value={emailConfig?.body || ''}
              onChange={(e) => updateEmailConfig({ body: e.target.value })}
            />

            <div style={hintStyle}>
              Podés interpolar valores del flujo con <code>{'{{ campo }}'}</code>, <code>{'{{ ciudadano.email }}'}</code> o <code>{'{{ programa.nombre }}'}</code>. El resultado queda disponible en <code>acciones.{selectedNode.id}.ok</code>.
            </div>
          </div>
        )}

        {data.tipo === 'accion_http' && showAutomationTab && (
          <div style={sectionStyle}>
            <div style={sectionTitleStyle}>Acción automática</div>
            <label style={labelStyle}>Método</label>
            <select
              style={inputStyle}
              value={httpConfig?.method || 'POST'}
              onChange={(e) => updateHttpConfig({ method: e.target.value })}
            >
              {HTTP_METHOD_OPTIONS.map((method) => (
                <option key={method} value={method}>{method}</option>
              ))}
            </select>

            <label style={labelStyle}>URL</label>
            <input
              style={inputStyle}
              value={httpConfig?.url || ''}
              onChange={(e) => updateHttpConfig({ url: e.target.value })}
              placeholder="https://example.com/api/flujo"
            />

            <label style={labelStyle}>Timeout (segundos)</label>
            <input
              type="number"
              min="1"
              style={inputStyle}
              value={httpConfig?.timeout_seconds || 10}
              onChange={(e) => updateHttpConfig({ timeout_seconds: Number(e.target.value || 1) })}
            />

            <div style={{ ...sectionTitleStyle, marginTop: 14 }}>Headers</div>
            {(httpConfig?.headers || []).map((header, index) => (
              <div key={`header-${index}`} style={optionCardStyle}>
                <div style={twoColumnsStyle}>
                  <div>
                    <label style={labelStyle}>Clave</label>
                    <input
                      style={inputStyle}
                      value={header.key || ''}
                      onChange={(e) => updateHttpHeader(index, { key: e.target.value })}
                    />
                  </div>
                  <div>
                    <label style={labelStyle}>Valor</label>
                    <input
                      style={inputStyle}
                      value={header.value || ''}
                      onChange={(e) => updateHttpHeader(index, { value: e.target.value })}
                    />
                  </div>
                </div>
                <button type="button" style={removeBtnStyle} onClick={() => removeHttpHeader(index)}>
                  Quitar header
                </button>
              </div>
            ))}
            <button type="button" style={secondaryBtnStyle} onClick={addHttpHeader}>
              Agregar header
            </button>

            <label style={labelStyle}>Body</label>
            <textarea
              style={{ ...inputStyle, minHeight: 120, resize: 'vertical' }}
              value={httpConfig?.body || ''}
              onChange={(e) => updateHttpConfig({ body: e.target.value })}
            />

            <div style={hintStyle}>
              La acción deja su resultado en <code>acciones.{selectedNode.id}.status_code</code>, <code>acciones.{selectedNode.id}.ok</code> y <code>acciones.{selectedNode.id}.json</code> o <code>body</code>.
            </div>
          </div>
        )}

        {data.tipo === 'accion_humana' && showOperativeTab && (
          <div style={sectionStyle}>
            <div style={sectionTitleStyle}>Experiencia del paso</div>
            <select
              style={inputStyle}
              value={contractMode}
              onChange={(e) => {
                setContractMode(e.target.value);
              }}
            >
              {ACTION_EXPERIENCE_OPTIONS.map((option) => (
                <option key={option.value || 'empty'} value={option.value}>{option.label}</option>
              ))}
            </select>

            {!formulario && !uiConfig && (
              <div style={hintStyle}>
                Si dejás este paso sin contrato de captura, la resolución seguirá dependiendo de la salida libre o del JSON/manual según la configuración del flujo.
              </div>
            )}

            <label style={labelStyle}>Rol requerido (opcional)</label>
            <select
              style={inputStyle}
              value={nodeConfig?.rol_programa_id ?? ''}
              onChange={(e) => {
                const value = e.target.value;
                updateNodeConfig({ rol_programa_id: value ? Number(value) : null });
              }}
            >
              <option value="">Ninguno — cualquier operador con permiso de programa</option>
              {roles.map((rol) => (
                <option key={rol.id} value={rol.id}>{rol.nombre}</option>
              ))}
            </select>
            {roles.length === 0 && (
              <div style={hintStyle}>
                Este programa no tiene roles definidos todavía. Gestionalos desde "Roles del programa" en el editor.
              </div>
            )}

            {uiConfig && (
              <>
                <div style={{ ...sectionTitleStyle, marginTop: 14 }}>Contrato declarativo</div>
                <label style={labelStyle}>Grupo responsable</label>
                <select
                  style={inputStyle}
                  value={actor?.value || 'programaOperar'}
                  onChange={(e) => updateNodeData({ actor: { mode: 'group', value: e.target.value } })}
                >
                  {ACTOR_GROUP_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>{option.label}</option>
                  ))}
                </select>
                <label style={labelStyle}>Superficie</label>
                <input style={inputStyle} value={(surface[0] || 'backoffice')} disabled />
                <div style={hintStyle}>
                  En este corte el renderer declarativo solo soporta `backoffice` y asignación por grupo.
                </div>
              </>
            )}

            {formulario && (
              <>
                <div style={{ ...sectionTitleStyle, marginTop: 14 }}>Formulario operativo legacy</div>
                <label style={labelStyle}>Tipo de captura</label>
                <select
                  style={inputStyle}
                  value={formulario?.type || ''}
                  onChange={(e) => {
                    const nextType = e.target.value;
                    updateNodeConfig({ formulario: buildDefaultFormConfig(nextType) });
                  }}
                >
                  {FORM_TYPE_OPTIONS.map((option) => (
                    <option key={option.value || 'empty'} value={option.value}>{option.label}</option>
                  ))}
                </select>
              </>
            )}

            {formulario?.type === 'boolean_decision' && (
              <>
                <label style={labelStyle}>Campo runtime</label>
                <input
                  style={inputStyle}
                  value={formulario.field_name || ''}
                  onChange={(e) => updateFormulario({ field_name: e.target.value })}
                  placeholder="aprobado"
                />
                <label style={labelStyle}>Etiqueta visible</label>
                <input
                  style={inputStyle}
                  value={formulario.field_label || ''}
                  onChange={(e) => updateFormulario({ field_label: e.target.value })}
                  placeholder="Resultado"
                />
                <div style={twoColumnsStyle}>
                  <div>
                    <label style={labelStyle}>Opción positiva</label>
                    <input
                      style={inputStyle}
                      value={formulario.true_label || ''}
                      onChange={(e) => updateFormulario({ true_label: e.target.value })}
                    />
                  </div>
                  <div>
                    <label style={labelStyle}>Opción negativa</label>
                    <input
                      style={inputStyle}
                      value={formulario.false_label || ''}
                      onChange={(e) => updateFormulario({ false_label: e.target.value })}
                    />
                  </div>
                </div>
                <label style={checkLabelStyle}>
                  <input
                    type="checkbox"
                    checked={formulario.include_observacion !== false}
                    onChange={(e) => updateFormulario({ include_observacion: e.target.checked, observacion_required: e.target.checked ? formulario.observacion_required : false })}
                  />
                  <span>Permitir observación adicional</span>
                </label>
                {formulario.include_observacion !== false && (
                  <>
                    <label style={labelStyle}>Etiqueta de observación</label>
                    <input
                      style={inputStyle}
                      value={formulario.observacion_label || ''}
                      onChange={(e) => updateFormulario({ observacion_label: e.target.value })}
                    />
                    <label style={checkLabelStyle}>
                      <input
                        type="checkbox"
                        checked={Boolean(formulario.observacion_required)}
                        onChange={(e) => updateFormulario({ observacion_required: e.target.checked })}
                      />
                      <span>Hacer obligatoria la observación</span>
                    </label>
                  </>
                )}
                <div style={hintStyle}>
                  Este tipo necesita dos salidas condicionales en el mismo nodo, usando el campo configurado con valores <code>true</code> y <code>false</code>.
                </div>
              </>
            )}

            {formulario?.type === 'text_input' && (
              <>
                <label style={labelStyle}>Campo runtime</label>
                <input
                  style={inputStyle}
                  value={formulario.field_name || ''}
                  onChange={(e) => updateFormulario({ field_name: e.target.value })}
                  placeholder="detalle"
                />
                <label style={labelStyle}>Etiqueta visible</label>
                <input
                  style={inputStyle}
                  value={formulario.field_label || ''}
                  onChange={(e) => updateFormulario({ field_label: e.target.value })}
                />
                <label style={labelStyle}>Placeholder</label>
                <input
                  style={inputStyle}
                  value={formulario.placeholder || ''}
                  onChange={(e) => updateFormulario({ placeholder: e.target.value })}
                />
                <label style={labelStyle}>Ayuda</label>
                <textarea
                  style={{ ...inputStyle, minHeight: 56, resize: 'vertical' }}
                  value={formulario.help_text || ''}
                  onChange={(e) => updateFormulario({ help_text: e.target.value })}
                />
                <label style={checkLabelStyle}>
                  <input
                    type="checkbox"
                    checked={formulario.required !== false}
                    onChange={(e) => updateFormulario({ required: e.target.checked })}
                  />
                  <span>Campo obligatorio</span>
                </label>
                <label style={checkLabelStyle}>
                  <input
                    type="checkbox"
                    checked={Boolean(formulario.multiline)}
                    onChange={(e) => updateFormulario({ multiline: e.target.checked })}
                  />
                  <span>Usar caja multilínea</span>
                </label>
                {formulario.multiline && (
                  <>
                    <label style={labelStyle}>Cantidad de filas</label>
                    <input
                      type="number"
                      min="1"
                      style={inputStyle}
                      value={formulario.rows || 4}
                      onChange={(e) => updateFormulario({ rows: Number(e.target.value || 1) })}
                    />
                  </>
                )}
              </>
            )}

            {formulario?.type === 'choice_select' && (
              <>
                <label style={labelStyle}>Campo runtime</label>
                <input
                  style={inputStyle}
                  value={formulario.field_name || ''}
                  onChange={(e) => updateFormulario({ field_name: e.target.value })}
                  placeholder="resultado"
                />
                <label style={labelStyle}>Etiqueta visible</label>
                <input
                  style={inputStyle}
                  value={formulario.field_label || ''}
                  onChange={(e) => updateFormulario({ field_label: e.target.value })}
                />
                <label style={labelStyle}>Texto inicial</label>
                <input
                  style={inputStyle}
                  value={formulario.placeholder || ''}
                  onChange={(e) => updateFormulario({ placeholder: e.target.value })}
                />
                <label style={labelStyle}>Ayuda</label>
                <textarea
                  style={{ ...inputStyle, minHeight: 56, resize: 'vertical' }}
                  value={formulario.help_text || ''}
                  onChange={(e) => updateFormulario({ help_text: e.target.value })}
                />
                <label style={checkLabelStyle}>
                  <input
                    type="checkbox"
                    checked={formulario.required !== false}
                    onChange={(e) => updateFormulario({ required: e.target.checked })}
                  />
                  <span>Selección obligatoria</span>
                </label>
                <div style={{ ...sectionTitleStyle, marginTop: 14 }}>Opciones</div>
                {(formulario.options || []).map((option, index) => (
                  <div key={`${option.value}-${index}`} style={optionCardStyle}>
                    <div style={twoColumnsStyle}>
                      <div>
                        <label style={labelStyle}>Valor</label>
                        <input
                          style={inputStyle}
                          value={option.value || ''}
                          onChange={(e) => updateOption(index, { value: e.target.value })}
                        />
                      </div>
                      <div>
                        <label style={labelStyle}>Etiqueta</label>
                        <input
                          style={inputStyle}
                          value={option.label || ''}
                          onChange={(e) => updateOption(index, { label: e.target.value })}
                        />
                      </div>
                    </div>
                    <button type="button" style={removeBtnStyle} onClick={() => removeOption(index)}>
                      Quitar opción
                    </button>
                  </div>
                ))}
                <button type="button" style={secondaryBtnStyle} onClick={addOption}>
                  Agregar opción
                </button>
              </>
            )}
          </div>
        )}

        {data.tipo === 'accion_humana' && uiConfig && showScreenTab && (
          <div style={uiPanelSectionStyle}>
            <div style={uiPanelSectionTitleStyle}>Interfaz declarativa v3</div>
            <label style={uiLabelStyle}>Título de la vista</label>
            <input
              style={uiInputStyle}
              value={uiConfig.title || ''}
              onChange={(e) => updateUiConfig({ title: e.target.value })}
              placeholder="Vista operativa"
            />
            <label style={uiLabelStyle}>Descripción</label>
            <textarea
              style={{ ...uiInputStyle, minHeight: isModalPresentation ? 48 : 56, resize: 'vertical' }}
              value={uiConfig.description || ''}
              onChange={(e) => updateUiConfig({ description: e.target.value })}
            />
            <label style={uiLabelStyle}>Layout</label>
            <select
              style={uiInputStyle}
              value={uiConfig.layout || 'single_column'}
              onChange={(e) => updateUiConfig({ layout: e.target.value })}
            >
              {UI_LAYOUT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
              ))}
            </select>
            <label style={uiLabelStyle}>Botón principal</label>
            <input
              style={uiInputStyle}
              value={uiConfig.submit?.label || ''}
              onChange={(e) => updateUiConfig({ submit: { ...(uiConfig.submit || {}), label: e.target.value } })}
              placeholder="Guardar y continuar"
            />

            <ScreenPreview
              schema={uiConfig}
              nodeLabel={data.label || 'Interfaz'}
              compact={isModalPresentation}
            />
            <div style={uiHintStyle}>
              La vista previa muestra la estructura final de la interfaz mientras la editás. Los placeholders como <code>{'{{ ciudadano.nombre_completo }}'}</code> se verán resueltos recién en la tarea real.
            </div>

            <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 14 : 18, display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
              <span>Secciones</span>
              {(expandedSectionKey || expandedFieldKey) && (
                <button type="button" style={uiCompactGhostBtnStyle} onClick={closeAllUi}>
                  Cerrar todo
                </button>
              )}
            </div>
            {(uiConfig.sections || []).map((section, sectionIndex) => {
              const sectionKey = getSectionCollapseKey(section, sectionIndex);
              const isSectionExpanded = expandedSectionKey === sectionKey;
              return (
              <div key={`${section.id || 'section'}-${sectionIndex}`} style={uiOptionCardStyle}>
                <div
                  style={{ ...uiCollapsibleHeaderStyle, cursor: 'pointer' }}
                  onClick={() => selectUiSection(section, sectionIndex)}
                >
                  <div>
                    <div style={uiCollapsibleTitleStyle}>{section.title || `Sección ${sectionIndex + 1}`}</div>
                    <div style={uiCollapsibleMetaStyle}>{getUiSectionSummary(section)}</div>
                  </div>
                  <button
                    type="button"
                    style={uiCompactGhostBtnStyle}
                    onClick={(e) => { e.stopPropagation(); selectUiSection(section, sectionIndex); }}
                  >
                    {isSectionExpanded ? 'Cerrar' : 'Editar'}
                  </button>
                </div>
                {isSectionExpanded && (
                  <>
                <div style={uiInlineActionsStyle}>
                  <button type="button" style={uiCompactSecondaryBtnStyle} onClick={() => moveUiSection(sectionIndex, -1)} disabled={sectionIndex === 0}>
                    Subir sección
                  </button>
                  <button type="button" style={uiCompactSecondaryBtnStyle} onClick={() => moveUiSection(sectionIndex, 1)} disabled={sectionIndex === (uiConfig.sections || []).length - 1}>
                    Bajar sección
                  </button>
                  <button type="button" style={uiCompactSecondaryBtnStyle} onClick={() => duplicateUiSection(sectionIndex)}>
                    Duplicar sección
                  </button>
                </div>
                <label style={uiLabelStyle}>ID de sección</label>
                <input
                  style={uiInputStyle}
                  value={section.id || ''}
                  onChange={(e) => updateUiSection(sectionIndex, { id: e.target.value })}
                />
                <label style={uiLabelStyle}>Título visible</label>
                <input
                  style={uiInputStyle}
                  value={section.title || ''}
                  onChange={(e) => updateUiSection(sectionIndex, { title: e.target.value })}
                />
                <label style={uiLabelStyle}>Descripción breve</label>
                <textarea
                  style={{ ...uiInputStyle, minHeight: isModalPresentation ? 48 : 56, resize: 'vertical' }}
                  value={section.description || ''}
                  onChange={(e) => updateUiSection(sectionIndex, { description: e.target.value })}
                  placeholder="Contexto, instrucciones o foco de esta sección"
                />

                <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 10 : 14 }}>Bloques</div>
                {(section.fields || []).map((field, fieldIndex) => {
                  const isTableField = field.kind === 'table';
                  const isDisplayOnlyField = !isTableField && DISPLAY_ONLY_UI_FIELD_KINDS.has(field.kind);
                  const tableMode = isTableField ? getUiTableMode(field) : null;
                  const simpleTableRows = isTableField ? buildSimpleTableRows(field) : [];
                  const fieldKey = getFieldCollapseKey(section, sectionIndex, field, fieldIndex);
                  const isFieldExpanded = expandedFieldKey === fieldKey;

                  return (
                  <div key={`${field.id || 'field'}-${fieldIndex}`} style={uiOptionCardStyle}>
                    <div
                      style={{ ...uiCollapsibleHeaderStyle, cursor: 'pointer' }}
                      onClick={() => selectUiField(section, sectionIndex, field, fieldIndex)}
                    >
                      <div>
                        <div style={uiCollapsibleTitleStyle}>{field.label || (isTableField ? `Tabla ${fieldIndex + 1}` : `Campo ${fieldIndex + 1}`)}</div>
                        <div style={uiCollapsibleMetaStyle}>
                          {getUiBlockSummary(field)}
                        </div>
                      </div>
                      <button
                        type="button"
                        style={uiCompactGhostBtnStyle}
                        onClick={(e) => { e.stopPropagation(); selectUiField(section, sectionIndex, field, fieldIndex); }}
                      >
                        {isFieldExpanded ? 'Cerrar' : 'Editar'}
                      </button>
                    </div>
                    {isFieldExpanded && (
                      <>
                    <div style={uiInlineActionsStyle}>
                      <button
                        type="button"
                        style={uiCompactSecondaryBtnStyle}
                        onClick={() => moveUiField(sectionIndex, fieldIndex, -1)}
                        disabled={fieldIndex === 0}
                      >
                        Subir bloque
                      </button>
                      <button
                        type="button"
                        style={uiCompactSecondaryBtnStyle}
                        onClick={() => moveUiField(sectionIndex, fieldIndex, 1)}
                        disabled={fieldIndex === (section.fields || []).length - 1}
                      >
                        Bajar bloque
                      </button>
                      <button
                        type="button"
                        style={uiCompactSecondaryBtnStyle}
                        onClick={() => duplicateUiField(sectionIndex, fieldIndex)}
                      >
                        Duplicar bloque
                      </button>
                    </div>
                    {isTableField ? (
                      <>
                        <label style={uiLabelStyle}>Tipo de bloque</label>
                        <select
                          style={uiInputStyle}
                          value={getUiBlockTypeValue(field)}
                          onChange={(e) => updateUiBlockType(sectionIndex, fieldIndex, e.target.value)}
                        >
                          {UI_BLOCK_TYPE_OPTIONS.map((option) => (
                            <option key={option.value} value={option.value}>{option.label}</option>
                          ))}
                        </select>
                        <label style={uiLabelStyle}>Título del bloque</label>
                        <input
                          style={uiInputStyle}
                          value={field.label || ''}
                          onChange={(e) => updateUiField(sectionIndex, fieldIndex, { label: e.target.value })}
                          placeholder="Ej: Datos principales"
                        />
                        <label style={uiLabelStyle}>Texto si no hay datos</label>
                        <input
                          style={uiInputStyle}
                          value={field.empty_message || ''}
                          onChange={(e) => updateUiField(sectionIndex, fieldIndex, { empty_message: e.target.value })}
                          placeholder="Ej: Sin datos para mostrar."
                        />

                        {tableMode === 'simple' ? (
                          <>
                            <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 10 : 14 }}>Plantillas rápidas</div>
                            <div style={uiTableMicrocopyStyle}>
                              Agregá un grupo de filas pre-armadas y editá lo que necesites. Las variables se resuelven en runtime.
                            </div>
                            <div style={uiTemplateChipsStyle}>
                              {SIMPLE_TABLE_TEMPLATES.map((template) => (
                                <button
                                  key={template.id}
                                  type="button"
                                  style={uiTemplateChipStyle}
                                  onClick={() => appendUiSimpleTableRows(sectionIndex, fieldIndex, template.rows)}
                                  title={template.rows.map((row) => `${row.campo} → ${row.valor}`).join('\n')}
                                >
                                  + {template.label}
                                </button>
                              ))}
                              {simpleTableRows.length > 0 && (
                                <button
                                  type="button"
                                  style={uiTemplateClearChipStyle}
                                  onClick={() => replaceUiSimpleTableRows(sectionIndex, fieldIndex, [])}
                                  title="Quitar todas las filas y empezar desde cero"
                                >
                                  Vaciar filas
                                </button>
                              )}
                            </div>
                            <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 10 : 14 }}>Filas a mostrar</div>
                            <div style={uiTableMicrocopyStyle}>
                              Cada fila se ve como un par <strong>Etiqueta / Valor</strong>. Podés interpolar datos con <code>{'{{ ciudadano.dni }}'}</code>.
                            </div>
                            {simpleTableRows.length === 0 && (
                              <div style={uiTableHelpStyle}>
                                Todavía no agregaste filas. Usá una plantilla rápida arriba o sumá una fila vacía abajo.
                              </div>
                            )}
                            {simpleTableRows.map((row, rowIndex) => (
                              <div key={`simple-row-${rowIndex}`} style={uiOptionCardStyle}>
                                <div style={uiCollapsibleHeaderStyle}>
                                  <div style={uiCollapsibleTitleStyle}>{`Fila ${rowIndex + 1}`}</div>
                                  <button
                                    type="button"
                                    style={uiCompactGhostBtnStyle}
                                    onClick={() => removeUiSimpleTableRow(sectionIndex, fieldIndex, rowIndex)}
                                  >
                                    Quitar
                                  </button>
                                </div>
                                <div style={uiTwoColumnsStyle}>
                                  <div>
                                    <label style={uiLabelStyle}>Etiqueta</label>
                                    <input
                                      style={uiInputStyle}
                                      value={row.campo || ''}
                                      onChange={(e) => updateUiSimpleTableRow(sectionIndex, fieldIndex, rowIndex, { campo: e.target.value })}
                                      placeholder="Ej: DNI"
                                    />
                                  </div>
                                  <div>
                                    <label style={uiLabelStyle}>Valor</label>
                                    <input
                                      style={uiInputStyle}
                                      value={row.valor || ''}
                                      onChange={(e) => updateUiSimpleTableRow(sectionIndex, fieldIndex, rowIndex, { valor: e.target.value })}
                                      placeholder="Ej: {{ ciudadano.dni }}"
                                    />
                                  </div>
                                </div>
                              </div>
                            ))}
                            <button type="button" style={uiSecondaryBtnStyle} onClick={() => addUiSimpleTableRow(sectionIndex, fieldIndex)}>
                              Agregar fila
                            </button>
                            <div style={uiTableEscapeHatchStyle}>
                              ¿Necesitás más de dos columnas?{' '}
                              <button
                                type="button"
                                style={uiInlineLinkBtnStyle}
                                onClick={() => setUiTableMode(sectionIndex, fieldIndex, 'advanced')}
                              >
                                Activar modo avanzado
                              </button>
                            </div>
                          </>
                        ) : (
                          <>
                            <div style={uiAdvancedBannerStyle}>
                              <div>
                                <strong>Modo avanzado</strong>
                                <div style={uiCollapsibleMetaStyle}>Definí columnas y filas a medida.</div>
                              </div>
                              <button
                                type="button"
                                style={uiInlineLinkBtnStyle}
                                onClick={() => setUiTableMode(sectionIndex, fieldIndex, 'simple')}
                              >
                                ← Volver a tabla simple
                              </button>
                            </div>
                            <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 10 : 14 }}>Columnas</div>
                            <div style={uiTableMicrocopyStyle}>
                              Definí cada columna visible y después cargá filas de ejemplo usando esas mismas claves.
                            </div>
                            {(field.columns || []).map((column, columnIndex) => (
                              <div key={`${column.key || 'column'}-${columnIndex}`} style={uiOptionCardStyle}>
                                <div style={uiCollapsibleHeaderStyle}>
                                  <div>
                                    <div style={uiCollapsibleTitleStyle}>{column.label || `Columna ${columnIndex + 1}`}</div>
                                    <div style={uiCollapsibleMetaStyle}>ID interno: {column.key || `columna_${columnIndex + 1}`}</div>
                                  </div>
                                </div>
                                <div style={uiTwoColumnsStyle}>
                                  <div>
                                    <label style={uiLabelStyle}>ID interno</label>
                                    <input
                                      style={uiInputStyle}
                                      value={column.key || ''}
                                      onChange={(e) => updateUiTableColumn(sectionIndex, fieldIndex, columnIndex, { key: e.target.value })}
                                      placeholder="Ej: dni"
                                    />
                                  </div>
                                  <div>
                                    <label style={uiLabelStyle}>Título visible</label>
                                    <input
                                      style={uiInputStyle}
                                      value={column.label || ''}
                                      onChange={(e) => updateUiTableColumn(sectionIndex, fieldIndex, columnIndex, { label: e.target.value })}
                                      placeholder="Ej: DNI"
                                    />
                                  </div>
                                </div>
                                <button type="button" style={uiRemoveBtnStyle} onClick={() => removeUiTableColumn(sectionIndex, fieldIndex, columnIndex)}>
                                  Quitar columna
                                </button>
                              </div>
                            ))}
                            <button type="button" style={uiSecondaryBtnStyle} onClick={() => addUiTableColumn(sectionIndex, fieldIndex)}>
                              Agregar columna
                            </button>

                            <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 10 : 14 }}>Filas</div>
                            <div style={uiTableMicrocopyStyle}>
                              Cada fila completa una línea de la tabla usando una celda por cada columna definida arriba.
                            </div>
                            {(field.rows || []).length === 0 && (
                              <div style={uiTableHelpStyle}>
                                Todavía no hay filas cargadas. Agregá una para ver cómo se compone la tabla en la vista previa.
                              </div>
                            )}
                            {(field.rows || []).map((row, rowIndex) => (
                              <div key={`row-${rowIndex}`} style={uiOptionCardStyle}>
                                <div style={uiCollapsibleHeaderStyle}>
                                  <div>
                                    <div style={uiCollapsibleTitleStyle}>{`Fila ${rowIndex + 1}`}</div>
                                    <div style={uiCollapsibleMetaStyle}>Una celda por columna</div>
                                  </div>
                                </div>
                                {(field.columns || []).map((column) => (
                                  <div key={`row-${rowIndex}-${column.key}`}>
                                    <label style={uiLabelStyle}>{column.label}</label>
                                    <input
                                      style={uiInputStyle}
                                      value={row[column.key] || ''}
                                      onChange={(e) => updateUiTableCell(sectionIndex, fieldIndex, rowIndex, column.key, e.target.value)}
                                      placeholder={column.key ? `Ej: {{ registro.${column.key} }}` : 'Escribi un valor'}
                                    />
                                  </div>
                                ))}
                                <button type="button" style={uiRemoveBtnStyle} onClick={() => removeUiTableRow(sectionIndex, fieldIndex, rowIndex)}>
                                  Quitar fila
                                </button>
                              </div>
                            ))}
                            <button type="button" style={uiSecondaryBtnStyle} onClick={() => addUiTableRow(sectionIndex, fieldIndex)}>
                              Agregar fila
                            </button>
                          </>
                        )}
                      </>
                    ) : (
                      <>
                        {isDisplayOnlyField ? (
                          <>
                            <label style={uiLabelStyle}>Tipo de bloque</label>
                            <select
                              style={uiInputStyle}
                              value={getUiBlockTypeValue(field)}
                              onChange={(e) => updateUiBlockType(sectionIndex, fieldIndex, e.target.value)}
                            >
                              {UI_BLOCK_TYPE_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>{option.label}</option>
                              ))}
                            </select>
                          </>
                        ) : (
                          <div style={uiTwoColumnsStyle}>
                            <div>
                              <label style={uiLabelStyle}>ID interno</label>
                              <input
                                style={uiInputStyle}
                                value={field.id || ''}
                                onChange={(e) => updateUiField(sectionIndex, fieldIndex, { id: e.target.value })}
                              />
                            </div>
                            <div>
                              <label style={uiLabelStyle}>Tipo de bloque</label>
                              <select
                                style={uiInputStyle}
                                value={getUiBlockTypeValue(field)}
                                onChange={(e) => updateUiBlockType(sectionIndex, fieldIndex, e.target.value)}
                              >
                                {UI_BLOCK_TYPE_OPTIONS.map((option) => (
                                  <option key={option.value} value={option.value}>{option.label}</option>
                                ))}
                              </select>
                            </div>
                          </div>
                        )}
                        <label style={uiLabelStyle}>{isDisplayOnlyField ? 'Título del bloque' : 'Etiqueta visible'}</label>
                        <input
                          style={uiInputStyle}
                          value={field.label || ''}
                          onChange={(e) => updateUiField(sectionIndex, fieldIndex, { label: e.target.value })}
                        />
                        {!['checkbox', 'info', 'summary'].includes(field.kind) && (
                          <>
                            <label style={uiLabelStyle}>Placeholder</label>
                            <input
                              style={uiInputStyle}
                              value={field.placeholder || ''}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { placeholder: e.target.value })}
                            />
                          </>
                        )}
                        {!['info', 'summary'].includes(field.kind) && (
                          <>
                            <label style={uiLabelStyle}>Ayuda</label>
                            <textarea
                              style={{ ...uiInputStyle, minHeight: isModalPresentation ? 42 : 48, resize: 'vertical' }}
                              value={field.help_text || ''}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { help_text: e.target.value })}
                            />
                            <label style={uiCheckLabelStyle}>
                              <input
                                type="checkbox"
                                checked={Boolean(field.required)}
                                onChange={(e) => updateUiField(sectionIndex, fieldIndex, { required: e.target.checked })}
                              />
                              <span>Campo obligatorio</span>
                            </label>
                          </>
                        )}
                        {field.kind === 'textarea' && (
                          <>
                            <label style={uiLabelStyle}>Cantidad de filas</label>
                            <input
                              type="number"
                              min="1"
                              style={uiInputStyle}
                              value={field.rows || 4}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { rows: Number(e.target.value || 1) })}
                            />
                          </>
                        )}
                        {['radio', 'select'].includes(field.kind) && (
                          <>
                            <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 10 : 14 }}>Opciones</div>
                            {(field.options || []).map((option, optionIndex) => (
                              <div key={`${option.value || 'option'}-${optionIndex}`} style={uiOptionCardStyle}>
                                <div style={uiTwoColumnsStyle}>
                                  <div>
                                    <label style={uiLabelStyle}>Valor</label>
                                    <input
                                      style={uiInputStyle}
                                      value={option.value || ''}
                                      onChange={(e) => updateUiOption(sectionIndex, fieldIndex, optionIndex, { value: e.target.value })}
                                    />
                                  </div>
                                  <div>
                                    <label style={uiLabelStyle}>Etiqueta</label>
                                    <input
                                      style={uiInputStyle}
                                      value={option.label || ''}
                                      onChange={(e) => updateUiOption(sectionIndex, fieldIndex, optionIndex, { label: e.target.value })}
                                    />
                                  </div>
                                </div>
                                <button type="button" style={uiRemoveBtnStyle} onClick={() => removeUiOption(sectionIndex, fieldIndex, optionIndex)}>
                                  Quitar opción
                                </button>
                              </div>
                            ))}
                            <button type="button" style={uiSecondaryBtnStyle} onClick={() => addUiOption(sectionIndex, fieldIndex)}>
                              Agregar opción
                            </button>
                          </>
                        )}
                        {field.kind === 'info' && (
                          <>
                            <label style={uiLabelStyle}>Contenido</label>
                            <textarea
                              style={{ ...uiInputStyle, minHeight: isModalPresentation ? 72 : 88, resize: 'vertical' }}
                              value={field.content || ''}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { content: e.target.value })}
                            />
                            <label style={uiLabelStyle}>Tono visual</label>
                            <select
                              style={uiInputStyle}
                              value={field.tone || 'info'}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { tone: e.target.value })}
                            >
                              {INFO_TONE_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>{option.label}</option>
                              ))}
                            </select>
                          </>
                        )}
                        {field.kind === 'summary' && (
                          <>
                            <label style={uiLabelStyle}>Mensaje sin items</label>
                            <input
                              style={uiInputStyle}
                              value={field.empty_message || ''}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { empty_message: e.target.value })}
                            />
                            <div style={{ ...uiPanelSectionTitleStyle, marginTop: isModalPresentation ? 10 : 14 }}>Items</div>
                            {(field.items || []).map((item, itemIndex) => (
                              <div key={`${item.label || 'summary-item'}-${itemIndex}`} style={uiOptionCardStyle}>
                                <div>
                                  <label style={uiLabelStyle}>Etiqueta</label>
                                  <input
                                    style={uiInputStyle}
                                    value={item.label || ''}
                                    onChange={(e) => updateUiSummaryItem(sectionIndex, fieldIndex, itemIndex, { label: e.target.value })}
                                  />
                                </div>
                                <div>
                                  <label style={uiLabelStyle}>Valor</label>
                                  <input
                                    style={uiInputStyle}
                                    value={item.value ?? ''}
                                    onChange={(e) => updateUiSummaryItem(sectionIndex, fieldIndex, itemIndex, { value: e.target.value })}
                                  />
                                </div>
                                <button type="button" style={uiRemoveBtnStyle} onClick={() => removeUiSummaryItem(sectionIndex, fieldIndex, itemIndex)}>
                                  Quitar item
                                </button>
                              </div>
                            ))}
                            <button type="button" style={uiSecondaryBtnStyle} onClick={() => addUiSummaryItem(sectionIndex, fieldIndex)}>
                              Agregar item
                            </button>
                          </>
                        )}
                      </>
                    )}
                    <button type="button" style={uiRemoveBtnStyle} onClick={() => removeUiField(sectionIndex, fieldIndex)}>
                      Quitar bloque
                    </button>
                      </>
                    )}
                  </div>
                  );
                })}

                <div style={uiInlineActionsStyle}>
                  <button type="button" style={uiCompactSecondaryBtnStyle} onClick={() => addUiField(sectionIndex, 'text')}>
                    Agregar bloque de texto
                  </button>
                  <button type="button" style={uiCompactSecondaryBtnStyle} onClick={() => addUiField(sectionIndex, 'info')}>
                    Agregar bloque info
                  </button>
                  <button type="button" style={uiCompactSecondaryBtnStyle} onClick={() => addUiField(sectionIndex, 'summary')}>
                    Agregar resumen
                  </button>
                  <button type="button" style={uiCompactSecondaryBtnStyle} onClick={() => addUiField(sectionIndex, 'table')}>
                    Agregar tabla de datos
                  </button>
                </div>
                <button type="button" style={uiRemoveBtnStyle} onClick={() => removeUiSection(sectionIndex)}>
                  Quitar sección
                </button>
                  </>
                )}
              </div>
              );
            })}

            <button type="button" style={uiSecondaryBtnStyle} onClick={addUiSection}>
              Agregar sección
            </button>
          </div>
        )}
        </div>
      </aside>
    );
  }

  // Arista seleccionada — solo mostrar editor de condición si el nodo origen es "decision"
  if (selectedEdge) {
    const sourceNode = nodes.find((n) => n.id === selectedEdge.source);
    const sourceForm = sourceNode?.data?.config?.formulario;
    const esAccionBooleana = sourceNode?.data?.tipo === 'accion_humana' && sourceForm?.type === 'boolean_decision';
    const conditionSuggestions = buildConditionSuggestions(sourceNode);
    const conditionSuggestionsMap = new Map(conditionSuggestions.map((suggestion) => [suggestion.path, suggestion]));
    const permiteCondicion = Boolean(sourceNode);
    const condicion = selectedEdge.data?.condicion ?? null;
    const condicionEditable = esAccionBooleana
      ? (condicion || buildDefaultCondition(sourceNode, conditionSuggestions))
      : condicion;
    const condicionActiva = condicionEditable || buildDefaultCondition(sourceNode, conditionSuggestions);
    const conditionSuggestion = conditionSuggestionsMap.get(condicionActiva?.campo || '') || null;
    const conditionDatalistId = `edge-condition-fields-${selectedEdge.id}`;
    const applyConditionPatch = (patch) => {
      onUpdateEdge(selectedEdge.id, { condicion: { ...condicionActiva, ...patch } });
    };
    const selectSuggestedConditionField = (campo) => {
      const suggestion = conditionSuggestionsMap.get(campo) || null;
      const nextCondition = coerceConditionForSuggestion({ ...condicionActiva, campo }, suggestion);
      onUpdateEdge(selectedEdge.id, { condicion: nextCondition });
    };

    return (
      <aside className={panelClassName}>
        <div className={propertiesClassName}>
        <div className="flow-panel-kicker">Transición</div>
        <h4 style={panelTitleStyle}>Regla de conexión</h4>
        <div style={panelIntroStyle}>Definí si esta salida es libre o si depende de una condición evaluable en runtime.</div>
        {!permiteCondicion ? (
          <div style={{ fontSize: 11, color: '#64748b' }}>
            No se pudo resolver el nodo origen de esta transición. Volvé a seleccionar la conexión después de actualizar el diagrama.
          </div>
        ) : (
          <>
            {!esAccionBooleana && (
              <>
                <label style={labelStyle}>Tipo de transición</label>
                <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                  <button
                    style={{ ...btnStyle, background: condicion === null ? '#e0e7ff' : '#fff', fontWeight: condicion === null ? 700 : 400 }}
                    onClick={() => onUpdateEdge(selectedEdge.id, { condicion: null })}
                  >
                    Libre
                  </button>
                  <button
                    style={{ ...btnStyle, background: condicion !== null ? '#e0e7ff' : '#fff', fontWeight: condicion !== null ? 700 : 400 }}
                    onClick={() => onUpdateEdge(selectedEdge.id, { condicion: condicion ?? buildDefaultCondition(sourceNode, conditionSuggestions) })}
                  >
                    Condicional
                  </button>
                </div>
              </>
            )}

            {esAccionBooleana && (
              <div style={hintStyle}>
                Este paso usa decisión booleana. Cada salida debe quedar condicionada por <code>{sourceForm.field_name}</code> con valor <code>true</code> o <code>false</code>.
              </div>
            )}

            {(esAccionBooleana || condicion !== null) && (
              <>
                <label style={labelStyle}>Campo a evaluar</label>
                <input
                  style={inputStyle}
                  value={condicionActiva?.campo || ''}
                  onChange={(e) => {
                    const nextField = e.target.value;
                    const suggestion = conditionSuggestionsMap.get(nextField) || null;
                    if (suggestion) {
                      selectSuggestedConditionField(nextField);
                      return;
                    }
                    applyConditionPatch({ campo: nextField });
                  }}
                  placeholder="Ej: aprobado o acciones.mi_nodo.ok"
                  disabled={esAccionBooleana}
                  list={conditionSuggestions.length > 0 ? conditionDatalistId : undefined}
                />
                {conditionSuggestions.length > 0 && (
                  <datalist id={conditionDatalistId}>
                    {conditionSuggestions.map((suggestion) => (
                      <option key={suggestion.path} value={suggestion.path}>{suggestion.label}</option>
                    ))}
                  </datalist>
                )}
                {conditionSuggestions.length > 0 && !esAccionBooleana && (
                  <div style={conditionSuggestionWrapStyle}>
                    {conditionSuggestions.map((suggestion) => (
                      <button
                        key={suggestion.path}
                        type="button"
                        style={{
                          ...conditionSuggestionButtonStyle,
                          ...(condicionActiva?.campo === suggestion.path ? activeConditionSuggestionButtonStyle : {}),
                        }}
                        onClick={() => selectSuggestedConditionField(suggestion.path)}
                        title={suggestion.label}
                      >
                        {suggestion.path}
                      </button>
                    ))}
                  </div>
                )}
                <label style={labelStyle}>Operador</label>
                {(esAccionBooleana || conditionSuggestion?.valueType === 'boolean') ? (
                  <input style={inputStyle} value="==" disabled />
                ) : (
                  <select
                    style={inputStyle}
                    value={condicionActiva?.operador || '==' }
                    onChange={(e) => applyConditionPatch({ operador: e.target.value })}
                  >
                    {OPERADORES.map((op) => <option key={op} value={op}>{op}</option>)}
                  </select>
                )}
                <label style={labelStyle}>Valor</label>
                {(esAccionBooleana || conditionSuggestion?.valueType === 'boolean') ? (
                  <select
                    style={inputStyle}
                    value={String(condicionActiva?.valor ?? true)}
                    onChange={(e) => applyConditionPatch({ valor: e.target.value === 'true' })}
                  >
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : Array.isArray(conditionSuggestion?.options) && conditionSuggestion.options.length > 0 ? (
                  <select
                    style={inputStyle}
                    value={condicionActiva?.valor ?? conditionSuggestion.defaultValue ?? ''}
                    onChange={(e) => applyConditionPatch({ valor: e.target.value })}
                  >
                    {conditionSuggestion.options.map((option) => (
                      <option key={option.value} value={option.value}>{option.label || option.value}</option>
                    ))}
                  </select>
                ) : conditionSuggestion?.valueType === 'number' ? (
                  <input
                    type="number"
                    style={inputStyle}
                    value={condicionActiva?.valor ?? conditionSuggestion.defaultValue ?? 0}
                    onChange={(e) => applyConditionPatch({ valor: Number(e.target.value) })}
                    placeholder="Ej: 200"
                  />
                ) : (
                  <input
                    style={inputStyle}
                    value={condicionActiva?.valor ?? ''}
                    onChange={(e) => applyConditionPatch({ valor: e.target.value })}
                    placeholder="Ej: true"
                  />
                )}
                <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>
                  La transición se toma cuando <code>{condicionActiva?.campo || 'campo'}</code> {condicionActiva?.operador} <code>{String(condicionActiva?.valor ?? '')}</code>
                </div>
                {conditionSuggestion && !esAccionBooleana && (
                  <div style={hintStyle}>
                    Campo sugerido desde <code>{sourceNode?.data?.label || sourceNode?.id}</code>: <strong>{conditionSuggestion.label}</strong>.
                    {conditionSuggestion.valueType === 'boolean' && ' Este valor se guarda como boolean real.'}
                    {conditionSuggestion.valueType === 'number' && ' Este valor se guarda como número real.'}
                  </div>
                )}
              </>
            )}
          </>
        )}
        </div>
      </aside>
    );
  }

  return null;
}

const labelStyle = {
  display: 'block',
  fontSize: 11,
  fontWeight: 700,
  color: '#475569',
  textTransform: 'uppercase',
  letterSpacing: '0.04em',
  marginBottom: 6,
  marginTop: 14,
};

const inputStyle = {
  width: '100%',
  padding: '10px 12px',
  border: '1px solid #cbd5e1',
  borderRadius: 10,
  fontSize: 13,
  boxSizing: 'border-box',
  background: '#fff',
  color: '#0f172a',
  boxShadow: 'inset 0 1px 2px rgba(15, 23, 42, 0.04)',
};

const btnStyle = {
  flex: 1,
  padding: '8px 10px',
  border: '1px solid #cbd5e1',
  borderRadius: 10,
  fontSize: 12,
  color: '#334155',
  background: '#fff',
  cursor: 'pointer',
};

const sectionStyle = {
  marginTop: 18,
  paddingTop: 14,
  borderTop: '1px solid #dbe4ef',
};

const sectionTitleStyle = {
  fontSize: 11,
  fontWeight: 700,
  color: '#334155',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  marginBottom: 10,
};

const hintStyle = {
  marginTop: 12,
  padding: '10px 12px',
  fontSize: 11,
  color: '#334155',
  background: '#eef2ff',
  border: '1px solid #c7d2fe',
  borderRadius: 12,
  lineHeight: 1.5,
};

const checkLabelStyle = {
  display: 'flex',
  gap: 8,
  alignItems: 'center',
  fontSize: 12,
  color: '#334155',
  marginTop: 12,
};

const twoColumnsStyle = {
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 10,
};

const optionCardStyle = {
  padding: 12,
  marginTop: 10,
  background: '#fff',
  border: '1px solid #dbe4ef',
  borderRadius: 12,
  boxShadow: '0 12px 24px -24px rgba(15, 23, 42, 0.45)',
};

const secondaryBtnStyle = {
  marginTop: 12,
  padding: '9px 12px',
  border: '1px solid #cbd5e1',
  borderRadius: 10,
  background: '#fff',
  color: '#1d4ed8',
  fontSize: 12,
  fontWeight: 600,
  cursor: 'pointer',
};

const compactSecondaryBtnStyle = {
  ...secondaryBtnStyle,
  marginTop: 0,
  padding: '7px 10px',
  fontSize: 11,
};

const removeBtnStyle = {
  ...secondaryBtnStyle,
  marginTop: 12,
  color: '#b91c1c',
  borderColor: '#fecaca',
  background: '#fef2f2',
};

const panelTitleStyle = {
  margin: '4px 0 0',
  fontSize: 18,
  fontWeight: 700,
  color: '#0f172a',
  textTransform: 'capitalize',
};

const tabListStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 8,
  marginTop: 14,
  marginBottom: 10,
  padding: 8,
  borderRadius: 14,
  background: '#f8fafc',
  border: '1px solid #e2e8f0',
};

const tabButtonStyle = {
  border: '1px solid transparent',
  borderRadius: 999,
  background: 'transparent',
  color: '#475569',
  padding: '8px 12px',
  fontSize: 12,
  fontWeight: 700,
  cursor: 'pointer',
};

const activeTabButtonStyle = {
  background: '#dbeafe',
  borderColor: '#93c5fd',
  color: '#1d4ed8',
  boxShadow: '0 10px 24px -20px rgba(29, 78, 216, 0.55)',
};

const tabHintCardStyle = {
  marginBottom: 14,
  padding: '10px 12px',
  borderRadius: 12,
  background: 'linear-gradient(180deg, #ffffff 0%, #f8fbff 100%)',
  border: '1px solid #dbe4ef',
  fontSize: 12,
  lineHeight: 1.5,
  color: '#475569',
};

const inlineActionsStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 8,
  marginBottom: 8,
};

const collapsibleHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: 12,
  marginBottom: 8,
};

const collapsibleTitleStyle = {
  fontSize: 13,
  fontWeight: 700,
  color: '#0f172a',
};

const collapsibleMetaStyle = {
  marginTop: 2,
  fontSize: 11,
  color: '#64748b',
};

const compactGhostBtnStyle = {
  border: '1px solid #dbe4ef',
  background: '#f8fafc',
  color: '#334155',
  borderRadius: 999,
  padding: '6px 10px',
  fontSize: 11,
  fontWeight: 600,
  cursor: 'pointer',
  whiteSpace: 'nowrap',
};

const panelIntroStyle = {
  marginTop: 6,
  color: '#64748b',
  fontSize: 12,
  lineHeight: 1.6,
};

const conditionSuggestionWrapStyle = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: 8,
  marginTop: 10,
};

const conditionSuggestionButtonStyle = {
  padding: '6px 10px',
  borderRadius: 999,
  border: '1px solid #cbd5e1',
  background: '#fff',
  color: '#334155',
  fontSize: 11,
  cursor: 'pointer',
};

const activeConditionSuggestionButtonStyle = {
  borderColor: '#93c5fd',
  background: '#dbeafe',
  color: '#1d4ed8',
  fontWeight: 700,
};
