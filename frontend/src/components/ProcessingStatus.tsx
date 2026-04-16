"use client";

interface ProcessingStatusProps {
  status: "idle" | "uploading" | "queued" | "processing" | "completed" | "failed";
  progress: number;
  stage: string;
  error?: string | null;
}

const stages = [
  { key: "uploading", label: "Uploading", icon: "📤" },
  { key: "queued", label: "Queued", icon: "📋" },
  { key: "processing", label: "Processing", icon: "⚙️" },
  { key: "completed", label: "Completed", icon: "✅" },
];

export default function ProcessingStatus({ status, progress, stage, error }: ProcessingStatusProps) {
  if (status === "idle") return null;

  const currentIdx = stages.findIndex((s) => s.key === status);

  return (
    <div className="w-full p-6 rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white/90">Processing Status</h3>
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            status === "completed"
              ? "bg-emerald-500/20 text-emerald-300"
              : status === "failed"
              ? "bg-red-500/20 text-red-300"
              : "bg-cyan-500/20 text-cyan-300"
          }`}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      </div>

      {/* Progress bar */}
      <div className="relative w-full h-2 bg-white/10 rounded-full overflow-hidden mb-4">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${
            status === "completed"
              ? "bg-gradient-to-r from-emerald-500 to-emerald-400"
              : status === "failed"
              ? "bg-gradient-to-r from-red-500 to-red-400"
              : "bg-gradient-to-r from-cyan-500 to-purple-500"
          }`}
          style={{ width: `${progress}%` }}
        />
        {status === "processing" && (
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer" />
        )}
      </div>

      <div className="flex items-center justify-between text-sm">
        <span className="text-white/60">{stage}</span>
        <span className="text-white/60 font-mono">{progress}%</span>
      </div>

      {/* Stage Steps */}
      <div className="flex items-center justify-between mt-6 gap-1">
        {stages.map((s, i) => {
          const isDone = currentIdx > i || status === "completed";
          const isCurrent = currentIdx === i;
          return (
            <div key={s.key} className="flex flex-col items-center gap-1 flex-1">
              <div
                className={`w-9 h-9 rounded-full flex items-center justify-center text-sm transition-all duration-500 ${
                  isDone
                    ? "bg-emerald-500/30 border-2 border-emerald-400"
                    : isCurrent
                    ? "bg-cyan-500/30 border-2 border-cyan-400 animate-pulse"
                    : "bg-white/5 border-2 border-white/10"
                }`}
              >
                {isDone ? "✓" : s.icon}
              </div>
              <span className={`text-xs ${isDone || isCurrent ? "text-white/80" : "text-white/30"}`}>
                {s.label}
              </span>
            </div>
          );
        })}
      </div>

      {/* Error */}
      {status === "failed" && error && (
        <div className="mt-4 p-3 rounded-xl bg-red-500/10 border border-red-500/30">
          <p className="text-sm text-red-300">
            <span className="font-semibold">Error:</span> {error}
          </p>
        </div>
      )}
    </div>
  );
}
