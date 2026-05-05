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
  { value: 'ui_form', label: 'Pantalla declarativa v3' },
];

const UI_FIELD_KIND_OPTIONS = [
  { value: 'text', label: 'Texto corto' },
  { value: 'textarea', label: 'Texto largo' },
  { value: 'number', label: 'Numero' },
  { value: 'date', label: 'Fecha' },
  { value: 'radio', label: 'Opcion unica' },
  { value: 'select', label: 'Lista desplegable' },
  { value: 'checkbox', label: 'Check' },
];

const ACTOR_GROUP_OPTIONS = [
  { value: 'programaOperar', label: 'programaOperar' },
  { value: 'programaConfigurar', label: 'programaConfigurar' },
];

const HTTP_METHOD_OPTIONS = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'];

function buildDefaultUiField(kind = 'text', index = 1) {
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
    title: 'Pantalla operativa',
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

export default function PropertiesPanel({ selectedNode, selectedEdge, nodes, onUpdateNode, onUpdateEdge }) {
  if (!selectedNode && !selectedEdge) {
    return (
      <aside className="flow-panel flow-side-panel">
        <div className="flow-properties">
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
      const nextSections = [
        ...(uiConfig?.sections || []),
        {
          id: `seccion_${(uiConfig?.sections || []).length + 1}`,
          title: `Seccion ${(uiConfig?.sections || []).length + 1}`,
          fields: [buildDefaultUiField('text', 1)],
        },
      ];
      updateUiConfig({ sections: nextSections });
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
            if (nextField.kind !== 'textarea') {
              delete nextField.rows;
            }
            if (!['radio', 'select'].includes(nextField.kind)) {
              delete nextField.options;
            } else if (!Array.isArray(nextField.options) || nextField.options.length === 0) {
              nextField.options = buildDefaultUiField(nextField.kind, fieldIndex + 1).options;
            }
            return nextField;
          }),
        };
      });
      updateUiConfig({ sections: nextSections });
    };
    const addUiField = (sectionIndex, kind = 'text') => {
      const nextSections = (uiConfig?.sections || []).map((section, index) => {
        if (index !== sectionIndex) {
          return section;
        }
        return {
          ...section,
          fields: [
            ...(section.fields || []),
            buildDefaultUiField(kind, (section.fields || []).length + 1),
          ],
        };
      });
      updateUiConfig({ sections: nextSections });
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

    return (
      <aside className="flow-panel flow-side-panel">
        <div className="flow-properties">
        <div className="flow-panel-kicker">Nodo</div>
        <h4 style={panelTitleStyle}>{data.tipo}</h4>
        <div style={panelIntroStyle}>Configurá el nombre visible, las instrucciones y el contrato operativo de este paso.</div>
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

        {data.tipo === 'accion_email' && (
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

        {data.tipo === 'accion_http' && (
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

        {data.tipo === 'accion_humana' && (
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

            {uiConfig && (
              <>
                <div style={{ ...sectionTitleStyle, marginTop: 14 }}>Pantalla declarativa v3</div>
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

                <label style={labelStyle}>Título de la pantalla</label>
                <input
                  style={inputStyle}
                  value={uiConfig.title || ''}
                  onChange={(e) => updateUiConfig({ title: e.target.value })}
                  placeholder="Pantalla operativa"
                />
                <label style={labelStyle}>Descripción</label>
                <textarea
                  style={{ ...inputStyle, minHeight: 56, resize: 'vertical' }}
                  value={uiConfig.description || ''}
                  onChange={(e) => updateUiConfig({ description: e.target.value })}
                />
                <label style={labelStyle}>Botón principal</label>
                <input
                  style={inputStyle}
                  value={uiConfig.submit?.label || ''}
                  onChange={(e) => updateUiConfig({ submit: { ...(uiConfig.submit || {}), label: e.target.value } })}
                  placeholder="Guardar y continuar"
                />

                <div style={{ ...sectionTitleStyle, marginTop: 18 }}>Secciones</div>
                {(uiConfig.sections || []).map((section, sectionIndex) => (
                  <div key={`${section.id || 'section'}-${sectionIndex}`} style={optionCardStyle}>
                    <label style={labelStyle}>ID de sección</label>
                    <input
                      style={inputStyle}
                      value={section.id || ''}
                      onChange={(e) => updateUiSection(sectionIndex, { id: e.target.value })}
                    />
                    <label style={labelStyle}>Título visible</label>
                    <input
                      style={inputStyle}
                      value={section.title || ''}
                      onChange={(e) => updateUiSection(sectionIndex, { title: e.target.value })}
                    />

                    <div style={{ ...sectionTitleStyle, marginTop: 14 }}>Campos</div>
                    {(section.fields || []).map((field, fieldIndex) => (
                      <div key={`${field.id || 'field'}-${fieldIndex}`} style={optionCardStyle}>
                        <div style={twoColumnsStyle}>
                          <div>
                            <label style={labelStyle}>ID</label>
                            <input
                              style={inputStyle}
                              value={field.id || ''}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { id: e.target.value })}
                            />
                          </div>
                          <div>
                            <label style={labelStyle}>Tipo</label>
                            <select
                              style={inputStyle}
                              value={field.kind || 'text'}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { kind: e.target.value })}
                            >
                              {UI_FIELD_KIND_OPTIONS.map((option) => (
                                <option key={option.value} value={option.value}>{option.label}</option>
                              ))}
                            </select>
                          </div>
                        </div>
                        <label style={labelStyle}>Etiqueta</label>
                        <input
                          style={inputStyle}
                          value={field.label || ''}
                          onChange={(e) => updateUiField(sectionIndex, fieldIndex, { label: e.target.value })}
                        />
                        {field.kind !== 'checkbox' && (
                          <>
                            <label style={labelStyle}>Placeholder</label>
                            <input
                              style={inputStyle}
                              value={field.placeholder || ''}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { placeholder: e.target.value })}
                            />
                          </>
                        )}
                        <label style={labelStyle}>Ayuda</label>
                        <textarea
                          style={{ ...inputStyle, minHeight: 48, resize: 'vertical' }}
                          value={field.help_text || ''}
                          onChange={(e) => updateUiField(sectionIndex, fieldIndex, { help_text: e.target.value })}
                        />
                        <label style={checkLabelStyle}>
                          <input
                            type="checkbox"
                            checked={Boolean(field.required)}
                            onChange={(e) => updateUiField(sectionIndex, fieldIndex, { required: e.target.checked })}
                          />
                          <span>Campo obligatorio</span>
                        </label>
                        {field.kind === 'textarea' && (
                          <>
                            <label style={labelStyle}>Cantidad de filas</label>
                            <input
                              type="number"
                              min="1"
                              style={inputStyle}
                              value={field.rows || 4}
                              onChange={(e) => updateUiField(sectionIndex, fieldIndex, { rows: Number(e.target.value || 1) })}
                            />
                          </>
                        )}
                        {['radio', 'select'].includes(field.kind) && (
                          <>
                            <div style={{ ...sectionTitleStyle, marginTop: 14 }}>Opciones</div>
                            {(field.options || []).map((option, optionIndex) => (
                              <div key={`${option.value || 'option'}-${optionIndex}`} style={optionCardStyle}>
                                <div style={twoColumnsStyle}>
                                  <div>
                                    <label style={labelStyle}>Valor</label>
                                    <input
                                      style={inputStyle}
                                      value={option.value || ''}
                                      onChange={(e) => updateUiOption(sectionIndex, fieldIndex, optionIndex, { value: e.target.value })}
                                    />
                                  </div>
                                  <div>
                                    <label style={labelStyle}>Etiqueta</label>
                                    <input
                                      style={inputStyle}
                                      value={option.label || ''}
                                      onChange={(e) => updateUiOption(sectionIndex, fieldIndex, optionIndex, { label: e.target.value })}
                                    />
                                  </div>
                                </div>
                                <button type="button" style={removeBtnStyle} onClick={() => removeUiOption(sectionIndex, fieldIndex, optionIndex)}>
                                  Quitar opción
                                </button>
                              </div>
                            ))}
                            <button type="button" style={secondaryBtnStyle} onClick={() => addUiOption(sectionIndex, fieldIndex)}>
                              Agregar opción
                            </button>
                          </>
                        )}
                        <button type="button" style={removeBtnStyle} onClick={() => removeUiField(sectionIndex, fieldIndex)}>
                          Quitar campo
                        </button>
                      </div>
                    ))}

                    <button type="button" style={secondaryBtnStyle} onClick={() => addUiField(sectionIndex)}>
                      Agregar campo
                    </button>
                    <button type="button" style={removeBtnStyle} onClick={() => removeUiSection(sectionIndex)}>
                      Quitar sección
                    </button>
                  </div>
                ))}

                <button type="button" style={secondaryBtnStyle} onClick={addUiSection}>
                  Agregar sección
                </button>
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
        </div>
      </aside>
    );
  }

  // Arista seleccionada — solo mostrar editor de condición si el nodo origen es "decision"
  if (selectedEdge) {
    const sourceNode = nodes.find((n) => n.id === selectedEdge.source);
    const sourceForm = sourceNode?.data?.config?.formulario;
    const esDecision = sourceNode?.data?.tipo === 'decision';
    const esAccionBooleana = sourceNode?.data?.tipo === 'accion_humana' && sourceForm?.type === 'boolean_decision';
    const permiteCondicion = esDecision || esAccionBooleana;
    const condicion = selectedEdge.data?.condicion ?? null;
    const condicionInicialBooleana = esAccionBooleana
      ? (condicion || { campo: sourceForm.field_name || 'aprobado', operador: '==', valor: true })
      : condicion;

    return (
      <aside className="flow-panel flow-side-panel">
        <div className="flow-properties">
        <div className="flow-panel-kicker">Transición</div>
        <h4 style={panelTitleStyle}>Regla de conexión</h4>
        <div style={panelIntroStyle}>Definí si esta salida es libre o si depende de una condición evaluable en runtime.</div>
        {!permiteCondicion ? (
          <div style={{ fontSize: 11, color: '#64748b' }}>
            Esta transición es libre (sin condición). Solo los nodos de decisión o una acción humana con formulario booleano pueden configurar condiciones.
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
                    onClick={() => onUpdateEdge(selectedEdge.id, { condicion: condicion ?? { campo: '', operador: '==', valor: '' } })}
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
                  value={condicionInicialBooleana?.campo || ''}
                  onChange={(e) => onUpdateEdge(selectedEdge.id, { condicion: { ...condicionInicialBooleana, campo: e.target.value } })}
                  placeholder="Ej: aprobado"
                  disabled={esAccionBooleana}
                />
                <label style={labelStyle}>Operador</label>
                {esAccionBooleana ? (
                  <input style={inputStyle} value="==" disabled />
                ) : (
                  <select
                    style={inputStyle}
                    value={condicionInicialBooleana?.operador || '=='}
                    onChange={(e) => onUpdateEdge(selectedEdge.id, { condicion: { ...condicionInicialBooleana, operador: e.target.value } })}
                  >
                    {OPERADORES.map((op) => <option key={op} value={op}>{op}</option>)}
                  </select>
                )}
                <label style={labelStyle}>Valor</label>
                {esAccionBooleana ? (
                  <select
                    style={inputStyle}
                    value={String(condicionInicialBooleana?.valor ?? true)}
                    onChange={(e) => onUpdateEdge(selectedEdge.id, { condicion: { ...condicionInicialBooleana, valor: e.target.value === 'true' } })}
                  >
                    <option value="true">true</option>
                    <option value="false">false</option>
                  </select>
                ) : (
                  <input
                    style={inputStyle}
                    value={condicionInicialBooleana?.valor ?? ''}
                    onChange={(e) => onUpdateEdge(selectedEdge.id, { condicion: { ...condicionInicialBooleana, valor: e.target.value } })}
                    placeholder="Ej: true"
                  />
                )}
                <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>
                  La transición se toma cuando <code>{condicionInicialBooleana?.campo || 'campo'}</code> {condicionInicialBooleana?.operador} <code>{String(condicionInicialBooleana?.valor ?? '')}</code>
                </div>
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

const panelIntroStyle = {
  marginTop: 6,
  color: '#64748b',
  fontSize: 12,
  lineHeight: 1.6,
};
