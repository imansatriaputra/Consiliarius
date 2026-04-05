"use client";

import { useClock } from "@/hooks/useClock";

function getGreeting(hour: number): string {
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}

function formatDate(date: Date): string {
  return date.toLocaleDateString("en-GB", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString("en-GB", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

export function GreetingHeader() {
  const { time } = useClock();
  const hour = time.getHours();
  const greeting = getGreeting(hour);

  return (
    <div>
      <p
        className="text-[11px] tracking-[0.2em] uppercase text-text-secondary mb-2 font-body"
        style={{ fontFamily: "var(--font-body)" }}
      >
        {formatDate(time)}
      </p>
      <div className="flex items-end justify-between gap-4">
        <h1
          className="font-display text-3xl sm:text-4xl text-text-primary leading-tight"
          style={{ fontFamily: "var(--font-display)" }}
        >
          {greeting},
          <br />
          <span className="text-accent-gradient">Advisor.</span>
        </h1>
        <span
          className="text-sm text-text-secondary font-body tabular-nums mb-1"
          style={{ fontFamily: "var(--font-body)" }}
        >
          {formatTime(time)}
        </span>
      </div>
    </div>
  );
}
