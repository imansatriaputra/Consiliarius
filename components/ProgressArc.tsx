"use client";

import { useEffect } from "react";
import { motion, useSpring, useTransform } from "framer-motion";
import { useClock } from "@/hooks/useClock";

const SIZE = 160;
const RADIUS = 64;
const STROKE_WIDTH = 5;
const CIRCUMFERENCE = 2 * Math.PI * RADIUS;

// Working day: 07:00 to 22:00 (15 hours)
const DAY_START_HOUR = 7;
const DAY_END_HOUR = 22;

function getDayProgress(date: Date): number {
  const hours = date.getHours() + date.getMinutes() / 60;
  if (hours <= DAY_START_HOUR) return 0;
  if (hours >= DAY_END_HOUR) return 1;
  return (hours - DAY_START_HOUR) / (DAY_END_HOUR - DAY_START_HOUR);
}

export function ProgressArc() {
  const { time } = useClock();
  const progress = getDayProgress(time);
  const percentage = Math.round(progress * 100);

  const springProgress = useSpring(0, {
    stiffness: 60,
    damping: 20,
  });

  // Animate to actual progress on mount and every minute
  useEffect(() => {
    springProgress.set(progress);
  }, [progress, springProgress]);

  const strokeDashoffset = useTransform(
    springProgress,
    (v) => CIRCUMFERENCE * (1 - v)
  );

  const center = SIZE / 2;

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: SIZE, height: SIZE }}>
        <svg
          width={SIZE}
          height={SIZE}
          viewBox={`0 0 ${SIZE} ${SIZE}`}
          style={{ transform: "rotate(-90deg)" }}
        >
          <defs>
            <linearGradient
              id="arcGradient"
              x1="0%"
              y1="0%"
              x2="100%"
              y2="0%"
            >
              <stop offset="0%" stopColor="#3b82f6" />
              <stop offset="100%" stopColor="#06b6d4" />
            </linearGradient>
            <filter id="arcGlow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={RADIUS}
            fill="none"
            stroke="rgba(255,255,255,0.05)"
            strokeWidth={STROKE_WIDTH}
          />

          {/* Progress arc */}
          <motion.circle
            cx={center}
            cy={center}
            r={RADIUS}
            fill="none"
            stroke="url(#arcGradient)"
            strokeWidth={STROKE_WIDTH}
            strokeLinecap="round"
            strokeDasharray={CIRCUMFERENCE}
            style={{ strokeDashoffset }}
          />
        </svg>

        {/* Center content */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center"
          style={{ transform: "rotate(0deg)" }}
        >
          <span
            className="font-body text-3xl tabular-nums text-text-primary leading-none"
            style={{ fontFamily: "var(--font-body)" }}
          >
            {percentage}
            <span className="text-base text-text-secondary">%</span>
          </span>
          <span
            className="font-body text-[10px] text-text-muted tracking-wider uppercase mt-1"
            style={{ fontFamily: "var(--font-body)" }}
          >
            of your day
          </span>
        </div>
      </div>

      <p
        className="text-[11px] text-text-muted font-body tracking-wide"
        style={{ fontFamily: "var(--font-body)" }}
      >
        {DAY_START_HOUR}:00 — {DAY_END_HOUR}:00
      </p>
    </div>
  );
}
