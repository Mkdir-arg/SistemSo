import FlowNodeCard from './FlowNodeCard.jsx';

export default function AccionHumanaNode({ data, selected }) {
  const formulario = data.config?.formulario;
  const formTypeLabel = formulario
    ? {
        boolean_decision: 'Decision',
        text_input: 'Texto',
        choice_select: 'Seleccion',
      }[formulario.type] || 'Formulario'
    : null;

  return (
    <FlowNodeCard
      data={data}
      selected={selected}
      type="accion_humana"
      icon="👤"
      title="Acción humana"
      defaultLabel="Acción"
      badge={formulario ? (
        <div className="flow-node__badge">
          <span>{formTypeLabel}</span>
          {formulario.field_label && <span>{formulario.field_label}</span>}
        </div>
      ) : null}
    />
  );
}
