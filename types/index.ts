export interface DayRecord {
  date: string;           // "YYYY-MM-DD" — staleness key for midnight reset
  objective: string;
  decision: string;
  setupComplete: boolean;
  createdAt: number;      // Unix ms
}

export type AppPhase = "loading" | "setup" | "main";
