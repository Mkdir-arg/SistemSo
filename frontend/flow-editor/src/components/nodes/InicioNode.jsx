import FlowNodeCard from './FlowNodeCard.jsx';

export default function InicioNode({ data, selected }) {
  return (
    <FlowNodeCard
      data={data}
      selected={selected}
      type="inicio"
      icon="▶"
      title="Inicio"
      defaultLabel="Inicio"
      target={false}
    />
  );
}
