import FlowNodeCard from './FlowNodeCard.jsx';

export default function FinNode({ data, selected }) {
  return (
    <FlowNodeCard
      data={data}
      selected={selected}
      type="fin"
      icon="⏹"
      title="Fin"
      defaultLabel="Fin"
      source={false}
    />
  );
}
