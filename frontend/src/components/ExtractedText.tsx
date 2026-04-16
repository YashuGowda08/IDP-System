"use client";

import { useState } from "react";

interface ExtractedTextProps {
  text: string;
  confidence: number;
  engine: string;
  wordCount: number;
}

export default function ExtractedText({ text, confidence, engine, wordCount }: ExtractedTextProps) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const displayText = expanded ? text : text.slice(0, 1000);

  const copyText = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const confidenceColor =
    confidence >= 80
      ? "text-emerald-400"
      : confidence >= 50
      ? "text-yellow-400"
      : "text-red-400";

  return (
    <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500/30 to-cyan-500/30 flex items-center justify-center">
            <svg className="w-5 h-5 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
            </svg>
          </div>
          <div>
            <h3 className="text-base font-semibold text-white/90">Extracted Text</h3>
            <p className="text-xs text-white/40">{wordCount} words • Engine: {engine}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-mono ${confidenceColor}`}>{confidence}% confidence</span>
          <button
            onClick={copyText}
            className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-xs text-white/70 hover:text-white transition-all"
          >
            {copied ? "Copied!" : "Copy"}
          </button>
        </div>
      </div>

      {/* Text Content */}
      <div className="p-4">
        <pre className="whitespace-pre-wrap text-sm text-white/70 font-mono leading-relaxed max-h-[400px] overflow-y-auto custom-scrollbar">
          {displayText}
          {!expanded && text.length > 1000 && "..."}
        </pre>

        {text.length > 1000 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-3 text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
          >
            {expanded ? "Show less ↑" : `Show all (${text.length.toLocaleString()} characters) ↓`}
          </button>
        )}
      </div>
    </div>
  );
}
