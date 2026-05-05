import FlowNodeCard from './FlowNodeCard.jsx';

export default function DecisionNode({ data, selected }) {
  return (
    <FlowNodeCard
      data={data}
      selected={selected}
      type="decision"
      icon="◆"
      title="Decisión"
      defaultLabel="Decisión"
      sourceHandleId="out"
    />
  );
}
