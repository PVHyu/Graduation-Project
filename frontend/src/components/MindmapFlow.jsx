import { useMemo } from "react";
import {
  ReactFlow,
  Controls,
  MiniMap,
  Background,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { mindmapToFlow } from "../utils/mindmapToFlow";

function MindmapFlow ({ tree }) {
  const { nodes, edges } = useMemo(() => {
    if (!tree) return { nodes: [], edges: [] };
    return mindmapToFlow(tree);
  }, [tree]);

  if (!tree) return null;

  return (
    <div
      style={{
        width: "100%",
        height: "650px",
        background: "#ffffff",
        borderRadius: "12px",
        overflow: "hidden",
      }}
    >
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable
        nodesConnectable={false}
        elementsSelectable
        panOnDrag
        zoomOnScroll
      >
        <MiniMap />
        <Controls />
        <Background />
      </ReactFlow>
    </div>
  );
}

export default MindmapFlow;