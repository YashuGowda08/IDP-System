"use client";

import { useCallback, useState } from "react";

interface FileUploadProps {
  onFileSelected: (file: File) => void;
  isProcessing: boolean;
}

const ACCEPTED = {
  "application/pdf": ".pdf",
  "image/jpeg": ".jpg,.jpeg",
  "image/png": ".png",
};

export default function FileUpload({ onFileSelected, isProcessing }: FileUploadProps) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      const ext = file.name.split(".").pop()?.toLowerCase();
      const allowed = ["pdf", "jpg", "jpeg", "png"];
      if (!ext || !allowed.includes(ext)) {
        alert("Please upload a PDF, JPG, or PNG file.");
        return;
      }
      if (file.size > 50 * 1024 * 1024) {
        alert("File size exceeds 50 MB limit.");
        return;
      }
      setSelectedFile(file);
      onFileSelected(file);
    },
    [onFileSelected]
  );

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      if (e.dataTransfer.files?.[0]) {
        handleFile(e.dataTransfer.files[0]);
      }
    },
    [handleFile]
  );

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const onDragLeave = () => setDragActive(false);

  const onFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) handleFile(e.target.files[0]);
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="w-full">
      <div
        onDrop={onDrop}
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-300 cursor-pointer group
          ${dragActive
            ? "border-cyan-400 bg-cyan-400/10 scale-[1.02]"
            : "border-white/20 hover:border-cyan-400/50 bg-white/5 hover:bg-white/10"
          }
          ${isProcessing ? "pointer-events-none opacity-50" : ""}
        `}
        onClick={() => !isProcessing && document.getElementById("file-input")?.click()}
      >
        <input
          id="file-input"
          type="file"
          accept=".pdf,.jpg,.jpeg,.png"
          onChange={onFileInput}
          className="hidden"
          disabled={isProcessing}
        />

        {/* Icon */}
        <div className="mx-auto w-16 h-16 mb-4 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
          <svg className="w-8 h-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
          </svg>
        </div>

        <p className="text-lg font-medium text-white/90 mb-1">
          {dragActive ? "Drop your file here" : "Drag & drop your document"}
        </p>
        <p className="text-sm text-white/50">
          or <span className="text-cyan-400 underline underline-offset-2">browse files</span>
        </p>
        <p className="text-xs text-white/30 mt-3">
          Supports PDF, JPG, PNG • Max 50 MB
        </p>
      </div>

      {/* Selected file info */}
      {selectedFile && (
        <div className="mt-4 flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500/30 to-purple-500/30 flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-bold text-cyan-300 uppercase">
              {selectedFile.name.split(".").pop()}
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-white/90 truncate">{selectedFile.name}</p>
            <p className="text-xs text-white/40">{formatSize(selectedFile.size)}</p>
          </div>
          {!isProcessing && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                setSelectedFile(null);
              }}
              className="text-white/30 hover:text-red-400 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      )}
    </div>
  );
}
