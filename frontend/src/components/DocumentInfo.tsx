"use client";

interface DocumentInfoProps {
  fileName: string;
  fileType: string;
  pageCount: number;
  processingTime: number;
  classification: {
    document_type: string;
    confidence: number;
    top_keywords: string[];
  };
  wordCount: number;
}

const TYPE_ICONS: Record<string, string> = {
  invoice: "🧾",
  resume: "📄",
  form: "📝",
  report: "📊",
  letter: "✉️",
  receipt: "🧾",
  contract: "📑",
  general: "📃",
  unknown: "❓",
};

export default function DocumentInfo({
  fileName,
  fileType,
  pageCount,
  processingTime,
  classification,
  wordCount,
}: DocumentInfoProps) {
  const typeIcon = TYPE_ICONS[classification.document_type] || "📃";

  return (
    <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden">
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-indigo-500/30 to-blue-500/30 flex items-center justify-center">
            <span className="text-lg">{typeIcon}</span>
          </div>
          <div>
            <h3 className="text-base font-semibold text-white/90">Document Info</h3>
            <p className="text-xs text-white/40">{fileName}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-white/5">
        <InfoCard label="Type" value={classification.document_type} accent="cyan" />
        <InfoCard label="Confidence" value={`${classification.confidence}%`} accent="emerald" />
        <InfoCard label="Pages" value={String(pageCount)} accent="purple" />
        <InfoCard label="Words" value={wordCount.toLocaleString()} accent="amber" />
      </div>

      <div className="grid grid-cols-2 gap-px bg-white/5">
        <InfoCard label="Format" value={fileType.toUpperCase().replace(".", "")} accent="rose" />
        <InfoCard label="Processed In" value={`${processingTime}s`} accent="blue" />
      </div>

      {classification.top_keywords.length > 0 && (
        <div className="p-4 border-t border-white/10">
          <p className="text-xs text-white/40 mb-2">Classification Keywords</p>
          <div className="flex flex-wrap gap-1.5">
            {classification.top_keywords.slice(0, 8).map((kw, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded-md bg-white/5 text-xs text-white/50 border border-white/5"
              >
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function InfoCard({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent: string;
}) {
  const accentClasses: Record<string, string> = {
    cyan: "text-cyan-400",
    emerald: "text-emerald-400",
    purple: "text-purple-400",
    amber: "text-amber-400",
    rose: "text-rose-400",
    blue: "text-blue-400",
  };

  return (
    <div className="p-4 bg-white/[0.02]">
      <p className="text-xs text-white/40 mb-1">{label}</p>
      <p className={`text-lg font-semibold capitalize ${accentClasses[accent] || "text-white"}`}>
        {value}
      </p>
    </div>
  );
}
