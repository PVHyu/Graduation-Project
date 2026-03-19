import { useState } from "react";
import FileUploadForm from "./components/FileUploadForm";
import FileInfoCard from "./components/FileInfoCard";
import SummarySection from "./components/SummarySection";
import MindmapSection from "./components/MindmapSection";
import StatusMessage from "./components/StatusMessage";
import { uploadFileApi, summarizeApi, mindmapApi } from "./services/api";
import "./styles/app.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileInfo, setFileInfo] = useState(null);
  const [summaryData, setSummaryData] = useState(null);
  const [mindmapData, setMindmapData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const handleFileChange = (event) => {
    const file = event.target.files?.[0] || null;
    setSelectedFile(file);
    setErrorMessage("");
    setSuccessMessage("");
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setErrorMessage("Vui lòng chọn file trước.");
      return;
    }

    try {
      setLoading(true);
      setErrorMessage("");
      setSuccessMessage("");
      setFileInfo(null);
      setSummaryData(null);
      setMindmapData(null);

      const uploaded = await uploadFileApi(selectedFile);
      setFileInfo(uploaded);

      const savedFilename = uploaded.saved_filename;

      const summary = await summarizeApi(savedFilename);
      setSummaryData(summary);

      const mindmap = await mindmapApi(savedFilename);
      setMindmapData(mindmap);

      setSuccessMessage("Xử lý tài liệu thành công.");
    } catch (error) {
      const detail =
        error?.response?.data?.detail ||
        error?.message ||
        "Đã xảy ra lỗi khi xử lý tài liệu.";
      setErrorMessage(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Hệ thống tóm tắt tài liệu và sinh sơ đồ tư duy bằng AI</h1>
        <p>Tải file TXT, DOCX hoặc PDF để phân tích nội dung.</p>
      </header>

      <StatusMessage type="error" message={errorMessage} />
      <StatusMessage type="success" message={successMessage} />

      <FileUploadForm
        selectedFile={selectedFile}
        onFileChange={handleFileChange}
        onSubmit={handleAnalyze}
        loading={loading}
      />

      <FileInfoCard fileInfo={fileInfo} />
      <SummarySection summaryData={summaryData} />
      <MindmapSection mindmapData={mindmapData} />
    </div>
  );
}

export default App;