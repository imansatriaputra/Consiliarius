"use client";

import { EditableStatement } from "./EditableStatement";

interface DecisionCardProps {
  decision: string;
  onUpdate: (text: string) => void;
}

export function DecisionCard({ decision, onUpdate }: DecisionCardProps) {
  return (
    <div className="group relative">
      {/* Cyan left border */}
      <div
        className="absolute left-0 top-0 bottom-0 w-[2px] rounded-full"
        style={{
          background: "linear-gradient(180deg, #06b6d4, #3b82f6)",
        }}
      />

      <div
        className="
          pl-5 pr-4 py-5 rounded-r-xl
          bg-bg-card/80 backdrop-blur-sm
          border border-white/[0.04] border-l-0
          transition-all duration-300
          group-hover:bg-bg-card-hover/90
          group-hover:shadow-glow-cyan
        "
      >
        <p
          className="text-[11px] tracking-[0.18em] uppercase text-text-secondary mb-3 font-body"
          style={{ fontFamily: "var(--font-body)" }}
        >
          Key Decision
        </p>
        <EditableStatement
          value={decision}
          onSave={onUpdate}
          placeholder="What decision must you make?"
        />
      </div>
    </div>
  );
}
