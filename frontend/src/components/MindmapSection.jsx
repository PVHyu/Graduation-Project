function MindmapSection({ mindmapData }) {
  if (!mindmapData) return null;

  return (
    <div className="card">
      <h2>Mind map data</h2>

      <h3>Central Topic</h3>
      <p>{mindmapData.mindmap.title}</p>

      <h3>JSON Mind Map</h3>
      <pre className="json-box">
        {JSON.stringify(mindmapData.mindmap, null, 2)}
      </pre>
    </div>
  );
}

export default MindmapSection;