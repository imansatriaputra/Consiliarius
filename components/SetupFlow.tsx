"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

const EASE_SMOOTH = [0.16, 1, 0.3, 1] as const;

interface SetupFlowProps {
  onComplete: (objective: string, decision: string) => void;
}

const steps = [
  {
    id: 1,
    question: "What is the one thing\nthat matters today?",
    placeholder: "State your objective for today...",
    cta: "Continue",
  },
  {
    id: 2,
    question: "What is the one decision\nyou must make?",
    placeholder: "Describe the decision clearly...",
    cta: "Begin your day",
  },
];

export function SetupFlow({ onComplete }: SetupFlowProps) {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState(["", ""]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const current = steps[step];
  const value = answers[step];
  const canProceed = value.trim().length > 0;

  // Auto-focus on step change
  useEffect(() => {
    const timer = setTimeout(() => {
      textareaRef.current?.focus();
    }, 350);
    return () => clearTimeout(timer);
  }, [step]);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const updated = [...answers];
    updated[step] = e.target.value;
    setAnswers(updated);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey && canProceed) {
      e.preventDefault();
      handleNext();
    }
  };

  const handleNext = () => {
    if (!canProceed) return;
    if (step < steps.length - 1) {
      setStep((s) => s + 1);
    } else {
      onComplete(answers[0].trim(), answers[1].trim());
    }
  };

  return (
    <motion.div
      key="setup"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, scale: 0.98 }}
      transition={{ duration: 0.5, ease: EASE_SMOOTH }}
      className="fixed inset-0 flex items-center justify-center px-6 z-20"
    >
      {/* Subtle background vignette */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background:
            "radial-gradient(ellipse at center, transparent 40%, rgba(10,15,30,0.5) 100%)",
        }}
      />

      <div className="w-full max-w-[560px] relative">
        {/* Step indicator */}
        <div className="flex gap-2 mb-10">
          {steps.map((s, i) => (
            <div
              key={s.id}
              className="h-[2px] flex-1 rounded-full overflow-hidden"
              style={{ background: "rgba(255,255,255,0.08)" }}
            >
              <motion.div
                className="h-full rounded-full"
                style={{
                  background:
                    i <= step
                      ? "linear-gradient(90deg, #3b82f6, #06b6d4)"
                      : "transparent",
                }}
                initial={false}
                animate={{ width: i <= step ? "100%" : "0%" }}
                transition={{ duration: 0.4, ease: EASE_SMOOTH }}
              />
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.35, ease: EASE_SMOOTH }}
          >
            {/* Question */}
            <h2
              className="font-display text-3xl sm:text-4xl text-text-primary leading-tight mb-10 whitespace-pre-line"
              style={{ fontFamily: "var(--font-display)" }}
            >
              {current.question}
            </h2>

            {/* Textarea */}
            <textarea
              ref={textareaRef}
              value={value}
              onChange={handleChange}
              onKeyDown={handleKeyDown}
              placeholder={current.placeholder}
              rows={3}
              className="
                w-full bg-transparent
                font-body text-lg text-text-primary
                placeholder:text-text-muted
                border-b border-white/10 focus:border-accent-blue/50
                pb-3 mb-10
                transition-colors duration-300
                resize-none outline-none
              "
              style={{ fontFamily: "var(--font-body)" }}
            />

            {/* CTA button */}
            <AnimatePresence>
              {canProceed && (
                <motion.button
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 8 }}
                  transition={{ duration: 0.25, ease: EASE_SMOOTH }}
                  onClick={handleNext}
                  className="
                    group flex items-center gap-3
                    text-text-primary font-body text-sm tracking-wide
                    transition-all duration-300
                    hover:gap-4
                  "
                  style={{ fontFamily: "var(--font-body)" }}
                >
                  <span
                    className="
                      inline-flex items-center justify-center
                      w-10 h-10 rounded-full
                      transition-all duration-300
                      group-hover:shadow-glow-blue
                    "
                    style={{
                      background:
                        "linear-gradient(135deg, #3b82f6, #06b6d4)",
                    }}
                  >
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 16 16"
                      fill="none"
                    >
                      <path
                        d="M3 8h10M9 4l4 4-4 4"
                        stroke="white"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  </span>
                  {current.cta}
                </motion.button>
              )}
            </AnimatePresence>
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
}
