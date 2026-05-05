const INFO_TONE_STYLES = {
  info: {
    background: '#eff6ff',
    borderColor: '#bfdbfe',
    color: '#1d4ed8',
  },
  success: {
    background: '#ecfdf5',
    borderColor: '#a7f3d0',
    color: '#047857',
  },
  warning: {
    background: '#fffbeb',
    borderColor: '#fde68a',
    color: '#b45309',
  },
  danger: {
    background: '#fef2f2',
    borderColor: '#fecaca',
    color: '#b91c1c',
  },
  neutral: {
    background: '#f8fafc',
    borderColor: '#cbd5e1',
    color: '#334155',
  },
};

function previewInputStyle(compact) {
  return {
    width: '100%',
    padding: compact ? '8px 10px' : '9px 11px',
    borderRadius: 10,
    border: '1px solid #dbe4ef',
    background: '#f8fafc',
    color: '#475569',
    fontSize: compact ? 11 : 12,
    boxSizing: 'border-box',
  };
}

function fieldContainerStyle({ compact, fullWidth }) {
  return {
    gridColumn: fullWidth ? '1 / -1' : 'auto',
    minWidth: 0,
  };
}

function fieldLabelStyle(compact) {
  return {
    display: 'block',
    marginBottom: 5,
    fontSize: compact ? 10 : 11,
    fontWeight: 700,
    color: '#334155',
  };
}

function renderFieldPreview(field, compact) {
  const label = field?.label || field?.id || 'Campo';
  const inputStyle = previewInputStyle(compact);
  const fullWidthKinds = new Set(['textarea', 'info', 'summary', 'table']);
  const fullWidth = fullWidthKinds.has(field?.kind);

  if (field?.kind === 'info') {
    const toneStyle = INFO_TONE_STYLES[field.tone] || INFO_TONE_STYLES.info;
    return (
      <div style={fieldContainerStyle({ compact, fullWidth })}>
        <div
          style={{
            padding: compact ? '10px 11px' : '11px 12px',
            borderRadius: 12,
            border: `1px solid ${toneStyle.borderColor}`,
            background: toneStyle.background,
            color: toneStyle.color,
            fontSize: compact ? 11 : 12,
            lineHeight: 1.5,
          }}
        >
          {field.content || 'Bloque informativo'}
        </div>
      </div>
    );
  }

  if (field?.kind === 'summary') {
    const items = Array.isArray(field.items) ? field.items : [];
    return (
      <div style={fieldContainerStyle({ compact, fullWidth })}>
        <label style={fieldLabelStyle(compact)}>{label}</label>
        <div style={{ border: '1px solid #dbe4ef', borderRadius: 12, overflow: 'hidden', background: '#fff' }}>
          {items.length === 0 ? (
            <div style={{ padding: compact ? '10px 11px' : '12px 13px', color: '#64748b', fontSize: compact ? 11 : 12 }}>
              {field.empty_message || 'Sin datos para mostrar.'}
            </div>
          ) : (
            items.map((item, index) => (
              <div
                key={`${item.label || 'item'}-${index}`}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  gap: 10,
                  padding: compact ? '9px 11px' : '10px 12px',
                  borderTop: index === 0 ? 'none' : '1px solid #eef2f7',
                  fontSize: compact ? 11 : 12,
                }}
              >
                <span style={{ color: '#334155', fontWeight: 600 }}>{item.label || `Dato ${index + 1}`}</span>
                <span style={{ color: '#64748b' }}>{item.value || 'Sin valor'}</span>
              </div>
            ))
          )}
        </div>
      </div>
    );
  }

  if (field?.kind === 'table') {
    const columns = Array.isArray(field.columns) ? field.columns : [];
    const rows = Array.isArray(field.rows) ? field.rows : [];
    return (
      <div style={fieldContainerStyle({ compact, fullWidth })}>
        <label style={fieldLabelStyle(compact)}>{label}</label>
        <div style={{ border: '1px solid #dbe4ef', borderRadius: 12, overflow: 'hidden', background: '#fff' }}>
          {rows.length === 0 ? (
            <div style={{ padding: compact ? '10px 11px' : '12px 13px', color: '#64748b', fontSize: compact ? 11 : 12 }}>
              {field.empty_message || 'Sin registros para mostrar.'}
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: columns.length > 2 ? 420 : 0 }}>
                <thead>
                  <tr>
                    {columns.map((column, index) => (
                      <th
                        key={`${column.key || 'column'}-${index}`}
                        style={{
                          textAlign: 'left',
                          padding: compact ? '8px 10px' : '10px 12px',
                          background: '#f8fafc',
                          color: '#334155',
                          fontSize: compact ? 10 : 11,
                          borderBottom: '1px solid #e2e8f0',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {column.label || column.key || `Columna ${index + 1}`}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.map((row, rowIndex) => (
                    <tr key={`row-${rowIndex}`}>
                      {columns.map((column, columnIndex) => (
                        <td
                          key={`row-${rowIndex}-${column.key || columnIndex}`}
                          style={{
                            padding: compact ? '8px 10px' : '10px 12px',
                            fontSize: compact ? 11 : 12,
                            color: '#475569',
                            borderTop: rowIndex === 0 ? 'none' : '1px solid #eef2f7',
                          }}
                        >
                          {row?.[column.key] || '—'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (field?.kind === 'checkbox') {
    return (
      <div style={fieldContainerStyle({ compact, fullWidth })}>
        <label style={{ display: 'flex', gap: 8, alignItems: 'center', color: '#334155', fontSize: compact ? 11 : 12 }}>
          <input type="checkbox" disabled checked={Boolean(field.required)} />
          <span>{label}</span>
        </label>
      </div>
    );
  }

  if (field?.kind === 'radio') {
    const options = Array.isArray(field.options) ? field.options : [];
    return (
      <div style={fieldContainerStyle({ compact, fullWidth })}>
        <label style={fieldLabelStyle(compact)}>{label}</label>
        <div style={{ display: 'grid', gap: 6 }}>
          {options.map((option, index) => (
            <label key={`${option.value || 'option'}-${index}`} style={{ display: 'flex', gap: 8, alignItems: 'center', color: '#334155', fontSize: compact ? 11 : 12 }}>
              <input type="radio" disabled name={field.id || label} />
              <span>{option.label || option.value || `Opcion ${index + 1}`}</span>
            </label>
          ))}
        </div>
      </div>
    );
  }

  if (field?.kind === 'select') {
    return (
      <div style={fieldContainerStyle({ compact, fullWidth })}>
        <label style={fieldLabelStyle(compact)}>{label}</label>
        <select disabled style={inputStyle}>
          <option>{field.placeholder || 'Selecciona una opcion'}</option>
        </select>
      </div>
    );
  }

  if (field?.kind === 'textarea') {
    return (
      <div style={fieldContainerStyle({ compact, fullWidth })}>
        <label style={fieldLabelStyle(compact)}>{label}</label>
        <textarea
          disabled
          rows={field.rows || 4}
          style={{ ...inputStyle, resize: 'none', minHeight: compact ? 68 : 84 }}
          placeholder={field.placeholder || field.help_text || 'Escribi aca'}
        />
      </div>
    );
  }

  return (
    <div style={fieldContainerStyle({ compact, fullWidth: false })}>
      <label style={fieldLabelStyle(compact)}>{label}</label>
      <input
        disabled
        type={field?.kind === 'number' ? 'number' : field?.kind === 'date' ? 'date' : 'text'}
        style={inputStyle}
        placeholder={field?.placeholder || field?.help_text || 'Valor'}
      />
    </div>
  );
}

export default function ScreenPreview({ schema, nodeLabel = 'Pantalla', compact = false }) {
  const sections = Array.isArray(schema?.sections) ? schema.sections : [];
  const isTwoColumn = schema?.layout === 'two_column';

  return (
    <div style={{ marginTop: compact ? 12 : 14 }}>
      <div style={{ marginBottom: 8, fontSize: compact ? 11 : 12, fontWeight: 700, color: '#334155' }}>Vista previa en vivo</div>
      <div
        style={{
          border: '1px solid #dbe4ef',
          borderRadius: 16,
          overflow: 'hidden',
          background: 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
          boxShadow: '0 18px 40px -34px rgba(15, 23, 42, 0.5)',
        }}
      >
        <div style={{ padding: compact ? '12px 13px' : '14px 16px', borderBottom: '1px solid #e2e8f0', background: '#ffffffd9' }}>
          <div style={{ fontSize: compact ? 10 : 11, fontWeight: 700, letterSpacing: '0.04em', textTransform: 'uppercase', color: '#64748b' }}>
            {nodeLabel}
          </div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap', marginTop: 4 }}>
            <div>
              <div style={{ fontSize: compact ? 16 : 18, fontWeight: 700, color: '#0f172a' }}>{schema?.title || nodeLabel}</div>
              {schema?.description ? (
                <div style={{ marginTop: 4, fontSize: compact ? 11 : 12, color: '#64748b', lineHeight: 1.5 }}>{schema.description}</div>
              ) : null}
            </div>
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                padding: compact ? '6px 9px' : '7px 10px',
                borderRadius: 999,
                border: '1px solid #dbe4ef',
                background: '#f8fafc',
                color: '#334155',
                fontSize: compact ? 10 : 11,
                fontWeight: 700,
              }}
            >
              {isTwoColumn ? 'Layout 2 columnas' : 'Layout 1 columna'}
            </div>
          </div>
        </div>

        <div style={{ padding: compact ? 12 : 16, display: 'grid', gap: compact ? 10 : 12 }}>
          {sections.map((section, sectionIndex) => (
            <div key={`${section.id || 'section'}-${sectionIndex}`} style={{ border: '1px solid #e2e8f0', borderRadius: 14, background: '#fff', padding: compact ? 11 : 13 }}>
              <div style={{ fontSize: compact ? 13 : 14, fontWeight: 700, color: '#0f172a' }}>{section.title || `Seccion ${sectionIndex + 1}`}</div>
              {section.description ? (
                <div style={{ marginTop: 4, fontSize: compact ? 11 : 12, color: '#64748b', lineHeight: 1.5 }}>{section.description}</div>
              ) : null}
              <div
                style={{
                  marginTop: 10,
                  display: 'grid',
                  gridTemplateColumns: isTwoColumn ? 'repeat(2, minmax(0, 1fr))' : '1fr',
                  gap: compact ? 10 : 12,
                }}
              >
                {(section.fields || []).map((field, fieldIndex) => (
                  <div key={`${field.id || field.kind || 'field'}-${fieldIndex}`}>{renderFieldPreview(field, compact)}</div>
                ))}
              </div>
            </div>
          ))}

          {sections.length === 0 ? (
            <div style={{ padding: compact ? '10px 12px' : '12px 14px', borderRadius: 12, border: '1px dashed #cbd5e1', background: '#f8fafc', color: '#64748b', fontSize: compact ? 11 : 12 }}>
              Todavia no hay secciones cargadas para esta pantalla.
            </div>
          ) : null}

          <button
            type="button"
            disabled
            style={{
              border: 'none',
              borderRadius: 12,
              padding: compact ? '10px 12px' : '11px 14px',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              color: '#fff',
              fontSize: compact ? 11 : 12,
              fontWeight: 700,
              opacity: 0.92,
            }}
          >
            {schema?.submit?.label || 'Guardar y continuar'}
          </button>
        </div>
      </div>
    </div>
  );
}