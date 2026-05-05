import { useCallback, useEffect, useRef, useState } from 'react';
import ReactFlow, {
  addEdge,
  Background,
  BackgroundVariant,
  Controls,
  MarkerType,
  MiniMap,
  useEdgesState,
  useNodesState,
} from 'reactflow';

import NodePanel from './components/NodePanel.jsx';
import AccionEmailNode from './components/nodes/AccionEmailNode.jsx';
import PropertiesPanel from './components/PropertiesPanel.jsx';
import AccionHumanaNode from './components/nodes/AccionHumanaNode.jsx';
import AccionHttpNode from './components/nodes/AccionHttpNode.jsx';
import DecisionNode from './components/nodes/DecisionNode.jsx';
import EsperaNode from './components/nodes/EsperaNode.jsx';
import FinNode from './components/nodes/FinNode.jsx';
import InicioNode from './components/nodes/InicioNode.jsx';
import { cargarDefinicion, guardarDefinicion, publicarFlujo } from './utils/api.js';
import { puedePublicar, validarFlujo } from './utils/validators.js';

const NODE_TYPES = {
  inicio: InicioNode,
  fin: FinNode,
  accion_humana: AccionHumanaNode,
  accion_email: AccionEmailNode,
  accion_http: AccionHttpNode,
  espera: EsperaNode,
  decision: DecisionNode,
};

const NODO_INICIO_DEFAULT = {
  id: 'n_inicio',
  type: 'inicio',
  position: { x: 250, y: 80 },
  data: { tipo: 'inicio', label: 'Inicio', descripcion: '' },
};

let nodeCounter = 1;
function nuevoId() {
  return `n_${Date.now()}_${nodeCounter++}`;
}

function parseDropTemplate(event) {
  const rawTemplate = event.dataTransfer.getData('application/reactflow-template');
  if (!rawTemplate) {
    return null;
  }

  try {
    return JSON.parse(rawTemplate);
  } catch {
    return null;
  }
}

function definicionToFlow(definicion) {
  if (!definicion || !definicion.nodos) return { nodes: [NODO_INICIO_DEFAULT], edges: [] };

  const nodes = definicion.nodos.map((nodo, i) => {
    const rawConfig = nodo.config || {};
    const {
      position,
      descripcion,
      formulario,
      ui,
      ...extraConfig
    } = rawConfig;
    const config = {
      ...extraConfig,
      formulario: formulario || null,
      ui: ui || null,
    };

    return {
      id: nodo.id,
      type: nodo.tipo,
      position: position || { x: 100 + i * 200, y: 100 + (i % 2) * 120 },
      data: {
        tipo: nodo.tipo,
        label: nodo.nombre,
        descripcion: descripcion || '',
        config,
        actor: nodo.actor || null,
        surface: Array.isArray(nodo.surface) ? nodo.surface : [],
      },
    };
  });

  const edges = (definicion.transiciones || []).map((t, i) => ({
    id: `e_${t.desde}_${t.hasta}_${i}`,
    source: t.desde,
    target: t.hasta,
    data: { condicion: t.condicion ?? null },
    label: t.condicion ? `${t.condicion.campo} ${t.condicion.operador} ${t.condicion.valor}` : '',
    animated: false,
  }));

  return { nodes, edges };
}

function flowToDefinicion(nodes, edges) {
  const usesSchemaV4 = nodes.some((node) => (
    node.data?.tipo === 'accion_email' || node.data?.tipo === 'accion_http'
  ));
  const usesSchemaV3 = nodes.some((node) => (
    node.data?.tipo === 'accion_humana'
    && (
      node.data?.actor
      || (Array.isArray(node.data?.surface) && node.data.surface.length > 0)
      || node.data?.config?.ui
    )
  ));

  return {
    schema_version: usesSchemaV4 ? 4 : (usesSchemaV3 ? 3 : 2),
    nodos: nodes.map((n) => {
      const config = {
        ...(n.data.config || {}),
        descripcion: n.data.descripcion || '',
        position: n.position,
      };
      if (!config.formulario) {
        delete config.formulario;
      }
      if (!config.ui) {
        delete config.ui;
      }

      const serializedNode = {
        id: n.id,
        tipo: n.data.tipo,
        nombre: n.data.label || '',
        config,
      };

      if (n.data?.actor?.mode && n.data?.actor?.value) {
        serializedNode.actor = n.data.actor;
      }
      if (Array.isArray(n.data?.surface) && n.data.surface.length > 0) {
        serializedNode.surface = n.data.surface;
      }

      return serializedNode;
    }),
    transiciones: edges.map((e) => ({
      desde: e.source,
      hasta: e.target,
      condicion: e.data?.condicion ?? null,
    })),
  };
}

export default function App({ programaId, programaNombre, apiDefinicionUrl, apiPublicarUrl }) {
  const reactFlowWrapper = useRef(null);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);
  const [nodes, setNodes, onNodesChange] = useNodesState([NODO_INICIO_DEFAULT]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [selectedEdge, setSelectedEdge] = useState(null);
  const [toast, setToast] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [publicando, setPublicando] = useState(false);
  const [versionInfo, setVersionInfo] = useState(null);

  const showToast = (mensaje, tipo = 'success') => {
    setToast({ mensaje, tipo });
    setTimeout(() => setToast(null), 4000);
  };

  // Carga inicial
  useEffect(() => {
    if (!apiDefinicionUrl) return;
    cargarDefinicion(apiDefinicionUrl)
      .then((data) => {
        if (data.definicion) {
          const { nodes: n, edges: e } = definicionToFlow(data.definicion);
          setNodes(n);
          setEdges(e);
          setVersionInfo({ id: data.version_id, numero: data.numero_version, estado: data.estado });
        }
      })
      .catch((err) => showToast(err.message, 'error'))
      .finally(() => setCargando(false));
  }, [apiDefinicionUrl]);

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge({ ...params, data: { condicion: null } }, eds)),
    [setEdges]
  );

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();
      const template = parseDropTemplate(event);
      const tipo = template?.tipo || event.dataTransfer.getData('application/reactflow-tipo');
      if (!tipo || !reactFlowInstance) return;

      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });

      const id = nuevoId();
      const etiquetas = {
        inicio: 'Inicio', fin: 'Fin', accion_humana: 'Acción', accion_email: 'Email', accion_http: 'HTTP', espera: 'Espera', decision: 'Decisión',
      };
      const nuevoNodo = {
        id,
        type: tipo,
        position,
        data: {
          tipo,
          label: template?.label || etiquetas[tipo] || tipo,
          descripcion: template?.descripcion || '',
          config: template?.config || {},
          actor: template?.actor || null,
          surface: template?.surface || [],
        },
      };
      setNodes((ns) => [...ns, nuevoNodo]);
    },
    [reactFlowInstance, setNodes]
  );

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
  }, []);

  const onEdgeClick = useCallback((_, edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
  }, []);

  const onPaneClick = useCallback(() => {
    setSelectedNode(null);
    setSelectedEdge(null);
  }, []);

  const onUpdateNode = useCallback((nodeId, patch) => {
    setNodes((ns) =>
      ns.map((n) => n.id === nodeId ? { ...n, data: { ...n.data, ...patch } } : n)
    );
    setSelectedNode((prev) => prev?.id === nodeId ? { ...prev, data: { ...prev.data, ...patch } } : prev);
  }, [setNodes]);

  const onUpdateEdge = useCallback((edgeId, patch) => {
    setEdges((es) =>
      es.map((e) => {
        if (e.id !== edgeId) return e;
        const newData = { ...e.data, ...patch };
        const cond = newData.condicion;
        return {
          ...e,
          data: newData,
          label: cond ? `${cond.campo} ${cond.operador} ${cond.valor}` : '',
        };
      })
    );
    setSelectedEdge((prev) => {
      if (!prev || prev.id !== edgeId) return prev;
      const newData = { ...prev.data, ...patch };
      return { ...prev, data: newData };
    });
  }, [setEdges]);

  const handleGuardar = async () => {
    if (!apiDefinicionUrl) return;
    setGuardando(true);
    try {
      const definicion = flowToDefinicion(nodes, edges);
      const result = await guardarDefinicion(apiDefinicionUrl, definicion);
      setVersionInfo({ id: result.version_id, numero: result.numero_version, estado: 'BORRADOR' });
      showToast(`Borrador v${result.numero_version} guardado.`);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setGuardando(false);
    }
  };

  const handlePublicar = async () => {
    if (!apiDefinicionUrl || !apiPublicarUrl) return;
    setPublicando(true);
    try {
      const definicion = flowToDefinicion(nodes, edges);
      const saved = await guardarDefinicion(apiDefinicionUrl, definicion);
      const published = await publicarFlujo(apiPublicarUrl);
      setVersionInfo({ id: published.version_id, numero: saved.numero_version, estado: 'PUBLICADA' });
      showToast(`Flujo v${saved.numero_version} publicado correctamente.`);
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      setPublicando(false);
    }
  };

  const tieneInicio = nodes.some((n) => n.data?.tipo === 'inicio');
  const { errores, advertencias } = validarFlujo(nodes, edges);
  const puedePublicarAhora = puedePublicar(nodes, edges);
  const selectionLabel = selectedNode
    ? `Nodo: ${selectedNode.data?.label || selectedNode.data?.tipo || selectedNode.id}`
    : selectedEdge
      ? `Transición: ${selectedEdge.source} -> ${selectedEdge.target}`
      : 'Sin selección';

  if (cargando) {
    return (
      <div className="flow-loading-state">
        Cargando editor...
      </div>
    );
  }

  return (
    <div className="flow-app">
      <header className="flow-toolbar">
        <div className="flow-toolbar__main">
          <div className="flow-toolbar__eyebrow">Editor operativo</div>
          <div>
            <div className="flow-toolbar__title-row">
              <h3 className="flow-toolbar__title">{programaNombre}</h3>
              <span className={`flow-chip ${versionInfo ? 'flow-chip--status' : ''}`}>
                {versionInfo ? `v${versionInfo.numero} · ${versionInfo.estado}` : 'Sin borrador guardado'}
              </span>
            </div>
            <p className="flow-toolbar__subtitle">
              Arrastrá nodos, conectá decisiones y configurá formularios operativos desde un único espacio de trabajo.
            </p>
          </div>
          <div className="flow-status-row">
            <span className="flow-chip">{nodes.length} nodos</span>
            <span className="flow-chip">{edges.length} transiciones</span>
            <span className={`flow-chip ${puedePublicarAhora ? 'flow-chip--success' : 'flow-chip--warning'}`}>
              {puedePublicarAhora ? 'Listo para publicar' : 'Borrador en revisión'}
            </span>
            {errores.length > 0 && (
              <span className="flow-chip flow-chip--error" title={errores.join('\n')}>
                {errores.length} error{errores.length > 1 ? 'es' : ''}
              </span>
            )}
            {advertencias.length > 0 && (
              <span className="flow-chip flow-chip--warning" title={advertencias.join('\n')}>
                {advertencias.length} advertencia{advertencias.length > 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>

        <div className="flow-actions">
          <button
            onClick={handleGuardar}
            disabled={guardando}
            className="flow-btn flow-btn--secondary"
          >
            {guardando ? 'Guardando...' : 'Guardar borrador'}
          </button>
          <button
            onClick={handlePublicar}
            disabled={!puedePublicarAhora || publicando}
            title={!puedePublicarAhora ? errores.join('\n') : 'Publicar flujo'}
            className="flow-btn flow-btn--primary"
          >
            {publicando ? 'Publicando...' : 'Publicar flujo'}
          </button>
        </div>
      </header>

      {toast && (
        <div className={`flow-toast ${toast.tipo === 'error' ? 'is-error' : 'is-success'}`}>
          {toast.mensaje}
        </div>
      )}

      <div className="flow-body">
        <NodePanel tieneInicio={tieneInicio} />

        <section className="flow-canvas-shell">
          <div className="flow-canvas-topbar">
            <div>
              <div className="flow-panel-kicker">Diseño actual</div>
              <h4 className="flow-canvas-title">Canvas principal</h4>
              <p className="flow-canvas-subtitle">Seleccioná, conectá y ordená el circuito sobre una vista amplia y limpia.</p>
            </div>
            <div className="flow-canvas-meta">
              <span className="flow-chip">{selectionLabel}</span>
              <span className="flow-chip">Delete para borrar</span>
            </div>
          </div>

          <div ref={reactFlowWrapper} className="flow-canvas-view">
            <ReactFlow
              className="flow-canvas"
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              onDrop={onDrop}
              onDragOver={onDragOver}
              onInit={setReactFlowInstance}
              onNodeClick={onNodeClick}
              onEdgeClick={onEdgeClick}
              onPaneClick={onPaneClick}
              nodeTypes={NODE_TYPES}
              fitView
              deleteKeyCode="Delete"
              defaultEdgeOptions={{
                type: 'smoothstep',
                markerEnd: { type: MarkerType.ArrowClosed, color: '#64748b' },
                style: { stroke: '#64748b', strokeWidth: 2 },
              }}
            >
              <Background variant={BackgroundVariant.Dots} color="#cbd5e1" gap={22} size={1.1} />
              <Controls position="bottom-right" />
              <MiniMap className="flow-minimap" nodeStrokeWidth={3} maskColor="rgba(248, 250, 252, 0.78)" />
            </ReactFlow>
          </div>
        </section>

        <PropertiesPanel
          selectedNode={selectedNode}
          selectedEdge={selectedEdge}
          nodes={nodes}
          onUpdateNode={onUpdateNode}
          onUpdateEdge={onUpdateEdge}
        />
      </div>
    </div>
  );
}
