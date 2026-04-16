"use client";

import { getDownloadUrl } from "@/lib/api";

interface DownloadButtonsProps {
  jobId: string;
}

const FORMATS = [
  {
    key: "json" as const,
    label: "JSON",
    icon: "{ }",
    color: "from-amber-500/30 to-orange-500/30",
    textColor: "text-amber-300",
    borderHover: "hover:border-amber-400/50",
    description: "Structured data",
  },
  {
    key: "csv" as const,
    label: "CSV",
    icon: "▦",
    color: "from-emerald-500/30 to-green-500/30",
    textColor: "text-emerald-300",
    borderHover: "hover:border-emerald-400/50",
    description: "Spreadsheet ready",
  },
  {
    key: "excel" as const,
    label: "Excel",
    icon: "📊",
    color: "from-blue-500/30 to-indigo-500/30",
    textColor: "text-blue-300",
    borderHover: "hover:border-blue-400/50",
    description: "Multi-sheet workbook",
  },
];

export default function DownloadButtons({ jobId }: DownloadButtonsProps) {
  const handleDownload = (format: "json" | "csv" | "excel") => {
    window.open(getDownloadUrl(jobId, format), "_blank");
  };

  return (
    <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden">
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500/30 to-blue-500/30 flex items-center justify-center">
            <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3" />
            </svg>
          </div>
          <div>
            <h3 className="text-base font-semibold text-white/90">Download Results</h3>
            <p className="text-xs text-white/40">Export processed data in your preferred format</p>
          </div>
        </div>
      </div>

      <div className="p-4 grid grid-cols-3 gap-3">
        {FORMATS.map((fmt) => (
          <button
            key={fmt.key}
            onClick={() => handleDownload(fmt.key)}
            className={`flex flex-col items-center gap-2 p-4 rounded-xl bg-gradient-to-br ${fmt.color} border border-white/10 ${fmt.borderHover} transition-all hover:scale-105 active:scale-95`}
          >
            <span className="text-2xl">{fmt.icon}</span>
            <span className={`text-sm font-semibold ${fmt.textColor}`}>{fmt.label}</span>
            <span className="text-[10px] text-white/40">{fmt.description}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
