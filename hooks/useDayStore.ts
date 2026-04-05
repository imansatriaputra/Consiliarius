"use client";

import { useState, useEffect, useCallback } from "react";
import type { DayRecord, AppPhase } from "@/types";
import {
  getTodayRecord,
  saveDayRecord,
  getTodayDateString,
} from "@/lib/storage";

interface DayStore {
  phase: AppPhase;
  record: DayRecord | null;
  completeSetup: (objective: string, decision: string) => void;
  updateObjective: (text: string) => void;
  updateDecision: (text: string) => void;
}

export function useDayStore(): DayStore {
  const [phase, setPhase] = useState<AppPhase>("loading");
  const [record, setRecord] = useState<DayRecord | null>(null);

  useEffect(() => {
    const existing = getTodayRecord();
    if (!existing) {
      setPhase("setup");
    } else if (existing.setupComplete) {
      setRecord(existing);
      setPhase("main");
    } else {
      setRecord(existing);
      setPhase("setup");
    }
  }, []);

  const completeSetup = useCallback(
    (objective: string, decision: string) => {
      const newRecord: DayRecord = {
        date: getTodayDateString(),
        objective,
        decision,
        setupComplete: true,
        createdAt: Date.now(),
      };
      saveDayRecord(newRecord);
      setRecord(newRecord);
      setPhase("main");
    },
    []
  );

  const updateObjective = useCallback(
    (text: string) => {
      if (!record) return;
      const updated = { ...record, objective: text };
      saveDayRecord(updated);
      setRecord(updated);
    },
    [record]
  );

  const updateDecision = useCallback(
    (text: string) => {
      if (!record) return;
      const updated = { ...record, decision: text };
      saveDayRecord(updated);
      setRecord(updated);
    },
    [record]
  );

  return { phase, record, completeSetup, updateObjective, updateDecision };
}
