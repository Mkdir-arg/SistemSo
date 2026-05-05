import FlowNodeCard from './FlowNodeCard.jsx';

export default function AccionHttpNode({ data, selected }) {
  const method = data.config?.http?.method || 'POST';

  return (
    <FlowNodeCard
      data={data}
      selected={selected}
      type="accion_http"
      icon="⇄"
      title="Acción HTTP"
      defaultLabel="HTTP"
      badge={(
        <div className="flow-node__badge">
          <span>{method}</span>
        </div>
      )}
    />
  );
}