import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE,
  timeout: 300000, // 5 min for large files
});

export interface UploadResponse {
  file_id: string;
  filename: string;
  saved_as: string;
  file_type: string;
  size_bytes: number;
  message: string;
}

export interface ProcessResponse {
  job_id: string;
  file_id: string;
  status: string;
  message: string;
}

export interface StatusResponse {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  progress: number;
  stage: string;
  started_at: string;
  completed_at: string | null;
  error: string | null;
}

export interface Entity {
  text: string;
  label: string;
  start: number;
  end: number;
}

export interface TableData {
  table_index: number;
  rows: number;
  columns: number;
  column_names: string[];
  data: Record<string, string>[];
  html: string;
  csv: string;
}

export interface ProcessingResults {
  file_name: string;
  file_type: string;
  processing_time: number;
  classification: {
    document_type: string;
    confidence: number;
    scores: Record<string, number>;
    top_keywords: string[];
  };
  ocr_results: {
    full_text: string;
    page_count: number;
    primary_engine: string;
    combined_confidence: number;
    total_words: number;
  };
  nlp_results: {
    entities: {
      persons: Entity[];
      dates: Entity[];
      amounts: Entity[];
      organizations: Entity[];
      locations: Entity[];
      misc: Entity[];
    };
    entity_count: number;
    summary: Record<string, number>;
  };
  tables: TableData[];
  embedded_images: { filename: string; page: number; width: number; height: number }[];
  page_image_urls: string[];
  embedded_image_urls: string[];
  page_count: number;
}

export interface ResultsResponse {
  job_id: string;
  status: string;
  results: ProcessingResults;
  output_files: Record<string, string>;
}

export async function uploadFile(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await api.post<UploadResponse>("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function processDocument(fileId: string): Promise<ProcessResponse> {
  const res = await api.post<ProcessResponse>(`/process-document/${fileId}`);
  return res.data;
}

export async function getStatus(jobId: string): Promise<StatusResponse> {
  const res = await api.get<StatusResponse>(`/status/${jobId}`);
  return res.data;
}

export async function getResults(jobId: string): Promise<ResultsResponse> {
  const res = await api.get<ResultsResponse>(`/results/${jobId}`);
  return res.data;
}

export function getDownloadUrl(jobId: string, format: "json" | "csv" | "excel"): string {
  return `${API_BASE}/download/${jobId}?format=${format}`;
}

export function getImageUrl(path: string): string {
  return `${API_BASE}${path}`;
}

export default api;
