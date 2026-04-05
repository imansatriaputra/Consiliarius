"use client";

import { EditableStatement } from "./EditableStatement";

interface ObjectiveCardProps {
  objective: string;
  onUpdate: (text: string) => void;
}

export function ObjectiveCard({ objective, onUpdate }: ObjectiveCardProps) {
  return (
    <div className="group relative">
      {/* Gradient left border */}
      <div
        className="absolute left-0 top-0 bottom-0 w-[2px] rounded-full"
        style={{
          background: "linear-gradient(180deg, #3b82f6, #06b6d4)",
        }}
      />

      <div
        className="
          pl-5 pr-4 py-5 rounded-r-xl
          bg-bg-card/80 backdrop-blur-sm
          border border-white/[0.04] border-l-0
          transition-all duration-300
          group-hover:bg-bg-card-hover/90
          group-hover:shadow-glow-blue
        "
      >
        <p
          className="text-[11px] tracking-[0.18em] uppercase text-text-secondary mb-3 font-body"
          style={{ fontFamily: "var(--font-body)" }}
        >
          Today&apos;s Objective
        </p>
        <EditableStatement
          value={objective}
          onSave={onUpdate}
          placeholder="What matters most today?"
        />
      </div>
    </div>
  );
}
