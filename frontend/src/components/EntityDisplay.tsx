"use client";

import { Entity } from "@/lib/api";

interface EntityDisplayProps {
  entities: {
    persons: Entity[];
    dates: Entity[];
    amounts: Entity[];
    organizations: Entity[];
    locations: Entity[];
    misc: Entity[];
  };
  entityCount: number;
}

const CATEGORY_CONFIG: Record<string, { label: string; color: string; bgColor: string; icon: string }> = {
  persons: { label: "People", color: "text-blue-300", bgColor: "bg-blue-500/20", icon: "👤" },
  dates: { label: "Dates", color: "text-amber-300", bgColor: "bg-amber-500/20", icon: "📅" },
  amounts: { label: "Amounts", color: "text-emerald-300", bgColor: "bg-emerald-500/20", icon: "💰" },
  organizations: { label: "Organizations", color: "text-purple-300", bgColor: "bg-purple-500/20", icon: "🏢" },
  locations: { label: "Locations", color: "text-rose-300", bgColor: "bg-rose-500/20", icon: "📍" },
  misc: { label: "Other", color: "text-gray-300", bgColor: "bg-gray-500/20", icon: "🏷️" },
};

export default function EntityDisplay({ entities, entityCount }: EntityDisplayProps) {
  if (!entityCount) {
    return (
      <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 p-6">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500/30 to-orange-500/30 flex items-center justify-center">
            <span className="text-lg">🔍</span>
          </div>
          <h3 className="text-base font-semibold text-white/90">Named Entities</h3>
        </div>
        <p className="text-sm text-white/40">No entities were detected in this document.</p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl bg-white/5 backdrop-blur-xl border border-white/10 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-amber-500/30 to-orange-500/30 flex items-center justify-center">
            <span className="text-lg">🔍</span>
          </div>
          <div>
            <h3 className="text-base font-semibold text-white/90">Named Entities</h3>
            <p className="text-xs text-white/40">{entityCount} entities extracted via NLP</p>
          </div>
        </div>
      </div>

      {/* Entity Categories */}
      <div className="p-4 space-y-4">
        {Object.entries(entities).map(([category, entityList]) => {
          if (!entityList || entityList.length === 0) return null;
          const config = CATEGORY_CONFIG[category] || CATEGORY_CONFIG.misc;

          return (
            <div key={category}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm">{config.icon}</span>
                <span className={`text-sm font-medium ${config.color}`}>{config.label}</span>
                <span className="text-xs text-white/30">({entityList.length})</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {entityList.map((entity, i) => (
                  <span
                    key={i}
                    className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium ${config.bgColor} ${config.color} border border-white/5`}
                  >
                    {entity.text}
                    <span className="opacity-50 text-[10px]">{entity.label}</span>
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
