function FileUploadForm({
  selectedFile,
  onFileChange,
  onSubmit,
  loading,
}) {
  return (
    <div className="card">
      <h2>Tải tài liệu</h2>

      <input
        type="file"
        accept=".txt,.docx,.pdf"
        onChange={onFileChange}
        disabled={loading}
      />

      <button onClick={onSubmit} disabled={!selectedFile || loading}>
        {loading ? "Đang xử lý..." : "Tóm tắt & tạo mind map"}
      </button>
    </div>
  );
}

export default FileUploadForm;