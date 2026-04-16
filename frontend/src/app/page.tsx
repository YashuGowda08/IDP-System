"use client";

import { useState, useCallback, useRef } from "react";
import FileUpload from "@/components/FileUpload";
import ProcessingStatus from "@/components/ProcessingStatus";
import ExtractedText from "@/components/ExtractedText";
import TableView from "@/components/TableView";
import ImageGallery from "@/components/ImageGallery";
import EntityDisplay from "@/components/EntityDisplay";
import DocumentInfo from "@/components/DocumentInfo";
import DownloadButtons from "@/components/DownloadButtons";
import {
  uploadFile,
  processDocument,
  getStatus,
  getResults,
  ProcessingResults,
} from "@/lib/api";

type AppStatus = "idle" | "uploading" | "queued" | "processing" | "completed" | "failed";

export default function Home() {
  const [status, setStatus] = useState<AppStatus>("idle");
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [results, setResults] = useState<ProcessingResults | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  const pollStatus = useCallback(
    (jobId: string) => {
      pollingRef.current = setInterval(async () => {
        try {
          const statusRes = await getStatus(jobId);

          setProgress(statusRes.progress);
          setStage(statusRes.stage);

          if (statusRes.status === "processing") {
            setStatus("processing");
          }

          if (statusRes.status === "completed") {
            stopPolling();
            const resultRes = await getResults(jobId);
            setResults(resultRes.results);
            setStatus("completed");
            setProgress(100);
            setStage("Complete");
          }

          if (statusRes.status === "failed") {
            stopPolling();
            setStatus("failed");
            setError(statusRes.error || "Processing failed");
          }
        } catch {
          stopPolling();
          setStatus("failed");
          setError("Connection lost. Please check if the backend is running.");
        }
      }, 1500);
    },
    [stopPolling]
  );

  const handleFileSelected = useCallback(
    async (file: File) => {
      stopPolling();
      setStatus("uploading");
      setProgress(5);
      setStage("Uploading file...");
      setError(null);
      setResults(null);
      setJobId(null);

      try {
        // Upload
        const uploadRes = await uploadFile(file);
        setProgress(15);
        setStage("File uploaded. Starting processing...");

        // Start processing
        const processRes = await processDocument(uploadRes.file_id);
        setJobId(processRes.job_id);
        setStatus("queued");
        setProgress(20);
        setStage("Queued for processing");

        // Poll for results
        pollStatus(processRes.job_id);
      } catch (err: unknown) {
        setStatus("failed");
        const msg =
          err instanceof Error ? err.message : "Upload failed. Is the backend running?";
        setError(msg);
      }
    },
    [stopPolling, pollStatus]
  );

  const handleReset = () => {
    stopPolling();
    setStatus("idle");
    setProgress(0);
    setStage("");
    setError(null);
    setResults(null);
    setJobId(null);
  };

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="border-b border-white/5">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center animate-pulse-glow">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
              </svg>
            </div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                IDP System
              </h1>
              <p className="text-xs text-white/40">Intelligent Document Processing</p>
            </div>
          </div>

          {status === "completed" && (
            <button
              onClick={handleReset}
              className="px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-sm text-white/70 hover:text-white transition-all"
            >
              Process New Document
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Hero / Upload Section */}
        {(status === "idle" || status === "uploading") && (
          <section className="text-center mb-4">
            <h2 className="text-3xl md:text-4xl font-bold text-white/90 mb-3">
              Extract Intelligence from Documents
            </h2>
            <p className="text-white/50 max-w-xl mx-auto mb-8">
              Upload a PDF, JPG, or PNG document. Our AI pipeline will extract text via OCR,
              detect tables, identify entities, and generate structured outputs.
            </p>
            <FileUpload
              onFileSelected={handleFileSelected}
              isProcessing={status === "uploading"}
            />
          </section>
        )}

        {/* Processing Status */}
        {status !== "idle" && (
          <ProcessingStatus
            status={status}
            progress={progress}
            stage={stage}
            error={error}
          />
        )}

        {/* Error retry */}
        {status === "failed" && (
          <div className="text-center">
            <button
              onClick={handleReset}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-purple-600 text-white font-medium hover:opacity-90 transition-all"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Results Sections */}
        {status === "completed" && results && (
          <div className="space-y-6">
            {/* Document Info + Download */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <DocumentInfo
                fileName={results.file_name}
                fileType={results.file_type}
                pageCount={results.page_count}
                processingTime={results.processing_time}
                classification={results.classification}
                wordCount={results.ocr_results.total_words}
              />
              {jobId && <DownloadButtons jobId={jobId} />}
            </div>

            {/* Extracted Text */}
            <ExtractedText
              text={results.ocr_results.full_text}
              confidence={results.ocr_results.combined_confidence}
              engine={results.ocr_results.primary_engine}
              wordCount={results.ocr_results.total_words}
            />

            {/* Entities */}
            <EntityDisplay
              entities={results.nlp_results.entities}
              entityCount={results.nlp_results.entity_count}
            />

            {/* Tables */}
            <TableView tables={results.tables} />

            {/* Images */}
            <ImageGallery
              pageImageUrls={results.page_image_urls}
              embeddedImageUrls={results.embedded_image_urls}
              embeddedImages={results.embedded_images}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-white/5 mt-16">
        <div className="max-w-6xl mx-auto px-6 py-6 text-center">
          <p className="text-xs text-white/30">
            AI-Powered Intelligent Document Processing System • Built with FastAPI, Next.js, Tesseract, EasyOCR & spaCy
          </p>
        </div>
      </footer>
    </div>
  );
}
