import { Handle, Position } from 'reactflow';

export default function FlowNodeCard({
  data,
  selected,
  type,
  icon,
  title,
  defaultLabel,
  sourceHandleId,
  target = true,
  source = true,
  badge = null,
}) {
  return (
    <div className={`flow-node flow-node--${type} ${selected ? 'is-selected' : ''}`}>
      {target && <Handle className="flow-node-handle" type="target" position={Position.Top} />}
      <div className="flow-node__icon">{icon}</div>
      <div className="flow-node__type">{title}</div>
      <div className="flow-node__label">{data.label || defaultLabel}</div>
      {data.descripcion && (
        <div className="flow-node__description">{data.descripcion}</div>
      )}
      {badge}
      {source && <Handle className="flow-node-handle" type="source" position={Position.Bottom} id={sourceHandleId} />}
    </div>
  );
}