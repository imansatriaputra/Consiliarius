"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useDayStore } from "@/hooks/useDayStore";
import { SetupFlow } from "@/components/SetupFlow";
import { MainView } from "@/components/MainView";

export default function Home() {
  const { phase, record, completeSetup, updateObjective, updateDecision } =
    useDayStore();

  return (
    <>
      <AnimatePresence mode="wait">
        {phase === "loading" && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 0 }}
            exit={{ opacity: 0 }}
            className="min-h-dvh"
          />
        )}

        {phase === "setup" && (
          <SetupFlow key="setup" onComplete={completeSetup} />
        )}

        {phase === "main" && record && (
          <motion.div
            key="main"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.5 }}
          >
            <MainView
              record={record}
              onUpdateObjective={updateObjective}
              onUpdateDecision={updateDecision}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
