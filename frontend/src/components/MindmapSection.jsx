import MindmapFlow  from "./MindmapFlow";

function MindmapSection({ mindmapData }) {
  if (!mindmapData) return null;

  return (
    <div className="card">
      <h2>Mind Map</h2>

      <h3>Central Topic</h3>
      <p>{mindmapData.mindmap.title}</p>

      <MindmapFlow  tree={mindmapData.mindmap} />

      <h3 style={{ marginTop: "20px" }}>Mind Map JSON</h3>
      <pre className="json-box">
        {JSON.stringify(mindmapData.mindmap, null, 2)}
      </pre>
    </div>
  );
}

export default MindmapSection;