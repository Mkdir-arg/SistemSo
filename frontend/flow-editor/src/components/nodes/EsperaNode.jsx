import FlowNodeCard from './FlowNodeCard.jsx';

export default function EsperaNode({ data, selected }) {
  return (
    <FlowNodeCard
      data={data}
      selected={selected}
      type="espera"
      icon="⏳"
      title="Espera"
      defaultLabel="Espera"
    />
  );
}
