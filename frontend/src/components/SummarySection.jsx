function SummarySection({ summaryData }) {
  if (!summaryData) return null;

  return (
    <div className="card">
      <h2>Bản tóm tắt</h2>
      <p>{summaryData.summary}</p>

      <h3>Ý chính</h3>
      <ul>
        {summaryData.main_points.map((point, index) => (
          <li key={index}>{point}</li>
        ))}
      </ul>

      <p><strong>Số chunk:</strong> {summaryData.chunks_count}</p>
    </div>
  );
}

export default SummarySection;