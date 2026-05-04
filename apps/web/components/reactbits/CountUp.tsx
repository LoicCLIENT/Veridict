"use client";

import { useEffect, useRef, useState } from "react";
import { useInView, motion, useSpring, useTransform } from "framer-motion";

interface CountUpProps {
  to: number;
  from?: number;
  duration?: number;
  delay?: number;
  className?: string;
  separator?: string;
  decimals?: number;
  onStart?: () => void;
  onEnd?: () => void;
}

export default function CountUp({
  to,
  from = 0,
  duration = 2,
  delay = 0,
  className = "",
  separator = "",
  decimals = 0,
  onStart,
  onEnd,
}: CountUpProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });
  const [hasStarted, setHasStarted] = useState(false);

  const spring = useSpring(from, {
    duration: duration * 1000,
    bounce: 0,
  });

  const display = useTransform(spring, (current): string => {
    const value = decimals > 0 ? current.toFixed(decimals) : Math.round(current).toString();
    if (separator) {
      return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, separator);
    }
    return value.toString();
  });

  useEffect(() => {
    if (isInView && !hasStarted) {
      const timer = setTimeout(() => {
        setHasStarted(true);
        onStart?.();
        spring.set(to);
      }, delay * 1000);

      return () => clearTimeout(timer);
    }
  }, [isInView, hasStarted, delay, spring, to, onStart]);

  useEffect(() => {
    if (hasStarted) {
      const timer = setTimeout(() => {
        onEnd?.();
      }, duration * 1000);
      return () => clearTimeout(timer);
    }
  }, [hasStarted, duration, onEnd]);

  return (
    <motion.span ref={ref} className={className}>
      {display}
    </motion.span>
  );
}
