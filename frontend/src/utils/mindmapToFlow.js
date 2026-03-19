let nodeIdCounter = 0;

function createNodeId() {
  nodeIdCounter += 1;
  return `node_${nodeIdCounter}`;
}

function getNodeStyle(depth) {
  if (depth === 0) {
    return {
      background: "#2563eb",
      color: "white",
      border: "1px solid #1d4ed8",
      borderRadius: "12px",
      padding: "10px 14px",
      width: 220,
      textAlign: "center",
      fontWeight: 700,
    };
  }

  if (depth === 1) {
    return {
      background: "#dbeafe",
      color: "#1e3a8a",
      border: "1px solid #93c5fd",
      borderRadius: "10px",
      padding: "8px 12px",
      width: 220,
      textAlign: "center",
      fontWeight: 600,
    };
  }

  return {
    background: "#f8fafc",
    color: "#0f172a",
    border: "1px solid #cbd5e1",
    borderRadius: "10px",
    padding: "8px 12px",
    width: 220,
    textAlign: "center",
  };
}

export function mindmapToFlow(root) {
  nodeIdCounter = 0;

  const nodes = [];
  const edges = [];

  const levelXGap = 260;
  const rowYGap = 120;

  function countLeafNodes(node) {
    if (!node.children || node.children.length === 0) return 1;
    return node.children.reduce((sum, child) => sum + countLeafNodes(child), 0);
  }

  function traverse(node, depth = 0, top = 0, parentId = null) {
    const currentId = createNodeId();

    const leafCount = countLeafNodes(node);
    const centerY = top + ((leafCount - 1) * rowYGap) / 2;

    nodes.push({
      id: currentId,
      position: {
        x: depth * levelXGap,
        y: centerY,
      },
      data: {
        label: node.title,
      },
      style: getNodeStyle(depth),
      sourcePosition: "right",
      targetPosition: "left",
      draggable: true,
    });

    if (parentId) {
      edges.push({
        id: `edge_${parentId}_${currentId}`,
        source: parentId,
        target: currentId,
      });
    }

    if (node.children && node.children.length > 0) {
      let childTop = top;

      for (const child of node.children) {
        const childLeafCount = countLeafNodes(child);
        traverse(child, depth + 1, childTop, currentId);
        childTop += childLeafCount * rowYGap;
      }
    }
  }

  traverse(root, 0, 0, null);

  return { nodes, edges };
}