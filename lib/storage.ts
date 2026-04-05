import type { DayRecord } from "@/types";

const STORAGE_KEY = "consiliarius_day";

export function getTodayDateString(): string {
  return new Date().toLocaleDateString("en-CA"); // Returns YYYY-MM-DD
}

export function getTodayRecord(): DayRecord | null {
  if (typeof window === "undefined") return null;

  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;

    const record = JSON.parse(raw) as DayRecord;
    if (record.date !== getTodayDateString()) return null;

    return record;
  } catch {
    return null;
  }
}

export function saveDayRecord(record: DayRecord): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(record));
}
