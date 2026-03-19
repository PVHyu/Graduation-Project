import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const uploadFileApi = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload/", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};

export const summarizeApi = async (savedFilename) => {
  const response = await api.post("/summarize/", {
    saved_filename: savedFilename,
  });

  return response.data;
};

export const mindmapApi = async (savedFilename) => {
  const response = await api.post("/mindmap/", {
    saved_filename: savedFilename,
  });

  return response.data;
};