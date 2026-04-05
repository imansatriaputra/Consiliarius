"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface EditableStatementProps {
  value: string;
  onSave: (newValue: string) => void;
  placeholder?: string;
  className?: string;
}

export function EditableStatement({
  value,
  onSave,
  placeholder = "Tap to write...",
  className = "",
}: EditableStatementProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [draft, setDraft] = useState(value);
  const [showHint, setShowHint] = useState(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const hasInteracted = useRef(false);

  // Sync draft when value changes externally
  useEffect(() => {
    if (!isEditing) setDraft(value);
  }, [value, isEditing]);

  // Hide hint after 3 seconds
  useEffect(() => {
    const timer = setTimeout(() => setShowHint(false), 3000);
    return () => clearTimeout(timer);
  }, []);

  const startEdit = useCallback(() => {
    setDraft(value);
    setIsEditing(true);
    hasInteracted.current = true;
    setShowHint(false);
  }, [value]);

  const commit = useCallback(() => {
    const trimmed = draft.trim();
    if (trimmed && trimmed !== value) {
      onSave(trimmed);
    }
    setIsEditing(false);
  }, [draft, value, onSave]);

  const cancel = useCallback(() => {
    setDraft(value);
    setIsEditing(false);
  }, [value]);

  // Auto-focus textarea when entering edit mode
  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
      // Place cursor at end
      const len = textareaRef.current.value.length;
      textareaRef.current.setSelectionRange(len, len);
    }
  }, [isEditing]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      commit();
    }
    if (e.key === "Escape") {
      cancel();
    }
  };

  return (
    <div className={`relative ${className}`}>
      <AnimatePresence mode="wait">
        {isEditing ? (
          <motion.div
            key="editing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            <textarea
              ref={textareaRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onBlur={commit}
              onKeyDown={handleKeyDown}
              placeholder={placeholder}
              rows={1}
              className={`
                w-full bg-transparent
                font-display text-xl leading-relaxed text-text-primary
                placeholder:text-text-muted
                border-b border-accent-blue/30 focus:border-accent-blue/60
                pb-1 transition-colors duration-200
                resize-none outline-none
              `}
              style={{ fontFamily: "var(--font-display)" }}
            />
            <p
              className="mt-1 text-[11px] text-text-muted font-body tracking-wide"
              style={{ fontFamily: "var(--font-body)" }}
            >
              Enter to save · Esc to cancel
            </p>
          </motion.div>
        ) : (
          <motion.div
            key="display"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
          >
            <p
              onClick={startEdit}
              className={`
                font-display text-xl leading-relaxed text-text-primary
                cursor-pointer hover:text-white transition-colors duration-200
              `}
              style={{ fontFamily: "var(--font-display)" }}
            >
              {value || (
                <span className="text-text-muted italic">{placeholder}</span>
              )}
            </p>
            <AnimatePresence>
              {showHint && !hasInteracted.current && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.4 }}
                  className="mt-1 text-[11px] text-text-muted font-body tracking-wide"
                  style={{ fontFamily: "var(--font-body)" }}
                >
                  tap to edit
                </motion.p>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
