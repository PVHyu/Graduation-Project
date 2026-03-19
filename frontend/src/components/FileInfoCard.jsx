function FileInfoCard({ fileInfo }) {
  if (!fileInfo) return null;

  return (
    <div className="card">
      <h2>Thông tin file</h2>
      <p><strong>Tên gốc:</strong> {fileInfo.original_filename}</p>
      <p><strong>Tên lưu:</strong> {fileInfo.saved_filename}</p>
      <p><strong>Định dạng:</strong> {fileInfo.extension}</p>
      <p><strong>Kích thước:</strong> {fileInfo.size} bytes</p>
    </div>
  );
}

export default FileInfoCard;