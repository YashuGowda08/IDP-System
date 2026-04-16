"use client";

import { TableData } from "@/lib/api";
import { useState } from "react";

interface TableViewProps {
  tables: TableData[];
}

export default function TableView({ tables }: TableViewProps) {
  const [activeTable, setActiveTable] = useState(0);

  if (!tables || tables.length === 0) {
    return (
      <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-green-500/30 to-emerald-500/30 flex items-center justify-center">
            <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-7.5A1.125 1.125 0 0112 18.375m9.75-12.75c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125m19.5 0v1.5c0 .621-.504 1.125-1.125 1.125M2.25 5.625v1.5c0 .621.504 1.125 1.125 1.125m0 0h17.25m-17.25 0h7.5c.621 0 1.125.504 1.125 1.125M3.375 8.25c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m17.25-3.75h-7.5c-.621 0-1.125.504-1.125 1.125m8.625-1.125c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125M12 10.875v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125M13.125 12h7.5m-7.5 0c-.621 0-1.125.504-1.125 1.125M20.625 12c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h7.5M12 14.625v-1.5m0 1.5c0 .621-.504 1.125-1.125 1.125M12 14.625c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m0 0v1.5" />
            </svg>
          </div>
          <h3 className="text-base font-semibold text-white/90">Extracted Tables</h3>
        </div>
        <p className="text-sm text-white/40">No tables were detected in this document.</p>
      </div>
    );
  }

  const table = tables[activeTable];

  return (
    <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-green-500/30 to-emerald-500/30 flex items-center justify-center">
            <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h7.5c.621 0 1.125-.504 1.125-1.125m-9.75 0V5.625" />
            </svg>
          </div>
          <div>
            <h3 className="text-base font-semibold text-white/90">Extracted Tables</h3>
            <p className="text-xs text-white/40">{tables.length} table{tables.length > 1 ? "s" : ""} found</p>
          </div>
        </div>

        {/* Table Tabs */}
        {tables.length > 1 && (
          <div className="flex gap-1">
            {tables.map((_, i) => (
              <button
                key={i}
                onClick={() => setActiveTable(i)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                  activeTable === i
                    ? "bg-emerald-500/30 text-emerald-300"
                    : "bg-white/5 text-white/40 hover:bg-white/10"
                }`}
              >
                Table {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Table info */}
      <div className="px-4 py-2 bg-white/[0.02] border-b border-white/5 text-xs text-white/40">
        {table.rows} rows × {table.columns} columns
      </div>

      {/* Table Content */}
      <div className="overflow-x-auto custom-scrollbar">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-white/10">
              {table.column_names.map((col, i) => (
                <th
                  key={i}
                  className="px-4 py-3 text-left text-xs font-semibold text-cyan-300 uppercase tracking-wider bg-white/[0.03]"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {table.data.map((row, rowIdx) => (
              <tr
                key={rowIdx}
                className="border-b border-white/5 hover:bg-white/5 transition-colors"
              >
                {table.column_names.map((col, colIdx) => (
                  <td
                    key={colIdx}
                    className="px-4 py-2.5 text-white/70 whitespace-nowrap"
                  >
                    {row[col] ?? ""}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
