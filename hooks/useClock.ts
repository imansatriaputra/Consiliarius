"use client";

import { useState, useEffect } from "react";

export function useClock(): { time: Date } {
  const [time, setTime] = useState<Date>(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setTime(new Date());
    }, 60_000);

    return () => clearInterval(interval);
  }, []);

  return { time };
}
