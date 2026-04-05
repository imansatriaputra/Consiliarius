"use client";

import { motion } from "framer-motion";
import { GreetingHeader } from "./GreetingHeader";
import { ObjectiveCard } from "./ObjectiveCard";
import { DecisionCard } from "./DecisionCard";
import { ProgressArc } from "./ProgressArc";
import type { DayRecord } from "@/types";

const EASE_SMOOTH = [0.16, 1, 0.3, 1] as const;

const fadeUp = (delay: number) => ({
  initial: { opacity: 0, y: 24 },
  animate: { opacity: 1, y: 0 },
  transition: {
    duration: 0.7,
    delay,
    ease: EASE_SMOOTH,
  },
});

interface MainViewProps {
  record: DayRecord;
  onUpdateObjective: (text: string) => void;
  onUpdateDecision: (text: string) => void;
}

export function MainView({
  record,
  onUpdateObjective,
  onUpdateDecision,
}: MainViewProps) {
  return (
    <div className="min-h-dvh flex flex-col px-6 py-10 max-w-lg mx-auto relative z-10">
      {/* Header */}
      <motion.div {...fadeUp(0)}>
        <GreetingHeader />
      </motion.div>

      {/* Cards — vertically centered in remaining space */}
      <div className="flex-1 flex flex-col justify-center gap-4 py-10">
        <motion.div {...fadeUp(0.15)}>
          <ObjectiveCard
            objective={record.objective}
            onUpdate={onUpdateObjective}
          />
        </motion.div>

        <motion.div {...fadeUp(0.3)}>
          <DecisionCard
            decision={record.decision}
            onUpdate={onUpdateDecision}
          />
        </motion.div>
      </div>

      {/* Progress arc */}
      <motion.div
        {...fadeUp(0.45)}
        className="flex justify-center pb-4"
      >
        <ProgressArc />
      </motion.div>
    </div>
  );
}
