import FlowNodeCard from './FlowNodeCard.jsx';

export default function AccionEmailNode({ data, selected }) {
  const recipients = Array.isArray(data.config?.email?.to) ? data.config.email.to : [];

  return (
    <FlowNodeCard
      data={data}
      selected={selected}
      type="accion_email"
      icon="✉"
      title="Acción email"
      defaultLabel="Email"
      badge={(
        <div className="flow-node__badge">
          <span>{recipients.length || 0} destinatario{recipients.length === 1 ? '' : 's'}</span>
        </div>
      )}
    />
  );
}