/**
 * Panel izquierdo — tipos de nodo disponibles para arrastrar al canvas.
 */

const LIBRARY_SECTIONS = [
  {
    title: 'Base',
    items: [
      { tipo: 'inicio', label: 'Inicio', icon: '▶', color: '#10b981', desc: 'Punto de entrada del flujo' },
      { tipo: 'fin', label: 'Fin', icon: '⏹', color: '#ef4444', desc: 'Cierre del caso' },
      { tipo: 'decision', label: 'Decisión', icon: '🔀', color: '#a855f7', desc: 'Ramificación condicional' },
      { tipo: 'espera', label: 'Espera', icon: '⏳', color: '#eab308', desc: 'Pausa temporal (bajo demanda)' },
      { tipo: 'accion_humana', label: 'Acción Humana', icon: '👤', color: '#3b82f6', desc: 'Paso manual genérico para el operador' },
      { tipo: 'accion_email', label: 'Acción Email', icon: '✉', color: '#ec4899', desc: 'Envía un email automáticamente' },
      { tipo: 'accion_http', label: 'Acción HTTP', icon: '⇄', color: '#0f766e', desc: 'Llama un endpoint automáticamente' },
    ],
  },
  {
    title: 'Plantillas',
    items: [
      {
        tipo: 'accion_humana',
        label: 'Aprobación',
        icon: '✅',
        color: '#2563eb',
        desc: 'Aprobación / rechazo con observación opcional',
        template: {
          label: 'Aprobación',
          descripcion: 'Definí una aprobación o rechazo guiado para este paso.',
          config: {
            formulario: {
              type: 'boolean_decision',
              field_name: 'aprobado',
              field_label: 'Resultado',
              true_label: 'Aprobar',
              false_label: 'Rechazar',
              include_observacion: true,
              observacion_label: 'Observación',
              observacion_required: false,
            },
          },
        },
      },
      {
        tipo: 'accion_humana',
        label: 'Formulario',
        icon: '📝',
        color: '#0f766e',
        desc: 'Captura texto libre, dictamen o comentario operativo',
        template: {
          label: 'Formulario',
          descripcion: 'Solicitá una carga manual de texto en este paso.',
          config: {
            formulario: {
              type: 'text_input',
              field_name: 'detalle',
              field_label: 'Detalle',
              placeholder: 'Escribí el detalle',
              help_text: '',
              required: true,
              multiline: true,
              rows: 4,
            },
          },
        },
      },
      {
        tipo: 'accion_humana',
        label: 'Selección',
        icon: '📋',
        color: '#7c3aed',
        desc: 'Lista cerrada de opciones operativas',
        template: {
          label: 'Selección',
          descripcion: 'Pedí al operador una selección cerrada entre opciones.',
          config: {
            formulario: {
              type: 'choice_select',
              field_name: 'resultado',
              field_label: 'Resultado',
              placeholder: 'Seleccioná una opción',
              help_text: '',
              required: true,
              options: [
                { value: 'opcion_1', label: 'Opción 1' },
                { value: 'opcion_2', label: 'Opción 2' },
              ],
            },
          },
        },
      },
      {
        tipo: 'accion_humana',
        label: 'Pantalla',
        icon: '🗂',
        color: '#0f4c81',
        desc: 'Pantalla declarativa v3 para backoffice',
        template: {
          label: 'Pantalla',
          descripcion: 'Definí una pantalla operativa declarativa para este paso.',
          actor: {
            mode: 'group',
            value: 'programaOperar',
          },
          surface: ['backoffice'],
          config: {
            ui: {
              type: 'form',
              title: 'Pantalla operativa',
              description: 'Completá la información necesaria para continuar el flujo.',
              layout: 'single_column',
              sections: [
                {
                  id: 'principal',
                  title: 'Datos principales',
                  fields: [
                    {
                      id: 'observacion',
                      kind: 'textarea',
                      label: 'Observacion',
                      required: false,
                      rows: 4,
                    },
                  ],
                },
              ],
              submit: {
                label: 'Guardar y continuar',
              },
            },
          },
        },
      },
      {
        tipo: 'accion_humana',
        label: 'Pantalla + resumen',
        icon: '📊',
        color: '#1d4ed8',
        desc: 'Pantalla declarativa con info, resumen visual y tabla de contexto',
        template: {
          label: 'Pantalla con resumen',
          descripcion: 'Mostrá contexto del caso y capturá una decisión del operador en la misma pantalla.',
          actor: {
            mode: 'group',
            value: 'programaOperar',
          },
          surface: ['backoffice'],
          config: {
            ui: {
              type: 'form',
              title: 'Revisión operativa',
              description: 'Verificá el contexto del caso y completá la resolución del paso.',
              layout: 'two_column',
              sections: [
                {
                  id: 'contexto',
                  title: 'Contexto del caso',
                  description: 'Resumen automático del caso antes de tomar la decisión.',
                  fields: [
                    {
                      id: 'recordatorio',
                      kind: 'info',
                      label: 'Antes de continuar',
                      tone: 'info',
                      content: 'Ciudadano {{ ciudadano.nombre_completo }} · Programa {{ programa.nombre }}',
                    },
                    {
                      id: 'indicadores',
                      kind: 'summary',
                      label: 'Indicadores del caso',
                      items: [
                        { label: 'DNI', value: '{{ ciudadano.dni }}' },
                        { label: 'Programa', value: '{{ programa.codigo }}' },
                        { label: 'Estado', value: 'En revision' },
                      ],
                      empty_message: 'Sin indicadores para mostrar.',
                    },
                    {
                      id: 'resumen',
                      kind: 'table',
                      label: 'Resumen',
                      columns: [
                        { key: 'campo', label: 'Campo' },
                        { key: 'valor', label: 'Valor' },
                      ],
                      rows: [
                        { campo: 'DNI', valor: '{{ ciudadano.dni }}' },
                        { campo: 'Programa', valor: '{{ programa.codigo }}' },
                      ],
                      empty_message: 'Sin datos para mostrar.',
                    },
                  ],
                },
                {
                  id: 'resolucion',
                  title: 'Resolución',
                  description: 'Captura operativa del paso actual.',
                  fields: [
                    {
                      id: 'resultado',
                      kind: 'radio',
                      label: 'Resultado',
                      required: true,
                      options: [
                        { value: 'aprobado', label: 'Aprobado' },
                        { value: 'observado', label: 'Observado' },
                      ],
                    },
                    {
                      id: 'observacion',
                      kind: 'textarea',
                      label: 'Observación',
                      required: false,
                      rows: 4,
                    },
                  ],
                },
              ],
              submit: {
                label: 'Guardar y continuar',
              },
            },
          },
        },
      },
      {
        tipo: 'accion_email',
        label: 'Notificar por email',
        icon: '📨',
        color: '#ec4899',
        desc: 'Envía un email usando datos del contexto del flujo',
        template: {
          label: 'Notificar por email',
          descripcion: 'Envía una notificación automática y continúa el flujo.',
          config: {
            email: {
              to: ['{{ ciudadano.email }}'],
              subject: 'Actualización de {{ programa.nombre }}',
              body: 'Hola {{ ciudadano.nombre_completo }},\n\nTu caso en {{ programa.nombre }} fue actualizado.',
            },
          },
        },
      },
      {
        tipo: 'accion_http',
        label: 'Llamada HTTP',
        icon: '🌐',
        color: '#0f766e',
        desc: 'Invoca una integración HTTP y deja el resultado en el contexto',
        template: {
          label: 'Llamada HTTP',
          descripcion: 'Invoca un endpoint y continúa según el resultado.',
          config: {
            http: {
              method: 'POST',
              url: 'https://example.com/api/flujo',
              headers: [
                { key: 'Content-Type', value: 'application/json' },
              ],
              body: '{"programa": "{{ programa.codigo }}", "ciudadano": "{{ ciudadano.dni }}"}',
              timeout_seconds: 10,
            },
          },
        },
      },
    ],
  },
];

export default function NodePanel({ tieneInicio }) {
  const onDragStart = (event, item) => {
    event.dataTransfer.setData('application/reactflow-tipo', item.tipo);
    event.dataTransfer.setData(
      'application/reactflow-template',
      JSON.stringify({
        tipo: item.tipo,
        label: item.template?.label || item.label,
        descripcion: item.template?.descripcion || '',
        actor: item.template?.actor || null,
        surface: item.template?.surface || [],
        config: item.template?.config || {},
      })
    );
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside className="flow-panel flow-node-panel">
      <div className="flow-panel-kicker">Biblioteca</div>
      <h4 className="flow-node-panel__title">Nodos y plantillas</h4>
      <p className="flow-node-panel__subtitle">
        Arrastrá piezas base o plantillas ya armadas para construir el recorrido operativo del programa.
      </p>

      {LIBRARY_SECTIONS.map((section) => (
        <div key={section.title} className="flow-node-panel__section">
          <div className="flow-node-panel__section-title">{section.title}</div>
          {section.items.map((item) => {
            const deshabilitado = item.tipo === 'inicio' && tieneInicio;
            return (
              <div
                key={`${section.title}-${item.label}`}
                draggable={!deshabilitado}
                onDragStart={deshabilitado ? undefined : (e) => onDragStart(e, item)}
                title={deshabilitado ? 'Ya existe un nodo de inicio' : item.desc}
                className={`flow-node-tile ${deshabilitado ? 'is-disabled' : ''}`}
                style={{ '--node-color': item.color }}
              >
                <span className="flow-node-tile__icon">{item.icon}</span>
                <div>
                  <div className="flow-node-tile__title">{item.label}</div>
                  <div className="flow-node-tile__desc">{item.desc}</div>
                </div>
              </div>
            );
          })}
        </div>
      ))}

      <div className="flow-node-panel__hint">
        Tip: las plantillas crean nodos `accion_humana` ya preconfigurados; podés usar formularios tipados legacy o una pantalla declarativa v3 desde el inspector derecho.
      </div>
    </aside>
  );
}
