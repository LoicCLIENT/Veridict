"use client";

import { useRef, useEffect, useState } from "react";
import { motion, useInView, Variants } from "framer-motion";

interface BlurTextProps {
  text: string;
  delay?: number;
  className?: string;
  animateBy?: "words" | "letters";
  direction?: "top" | "bottom" | "left" | "right";
  onAnimationComplete?: () => void;
}

export default function BlurText({
  text,
  delay = 0.05,
  className = "",
  animateBy = "words",
  direction = "top",
  onAnimationComplete,
}: BlurTextProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-50px" });
  const [hasAnimated, setHasAnimated] = useState(false);

  const elements = animateBy === "words" ? text.split(" ") : text.split("");

  const getInitialPosition = () => {
    switch (direction) {
      case "top":
        return { y: -20 };
      case "bottom":
        return { y: 20 };
      case "left":
        return { x: -20 };
      case "right":
        return { x: 20 };
      default:
        return { y: -20 };
    }
  };

  const variants: Variants = {
    hidden: {
      opacity: 0,
      filter: "blur(10px)",
      ...getInitialPosition(),
    },
    visible: (i: number) => ({
      opacity: 1,
      filter: "blur(0px)",
      x: 0,
      y: 0,
      transition: {
        delay: i * delay,
        duration: 0.5,
        ease: [0.22, 1, 0.36, 1],
      },
    }),
  };

  useEffect(() => {
    if (isInView && !hasAnimated) {
      const totalDuration = elements.length * delay * 1000 + 500;
      const timer = setTimeout(() => {
        setHasAnimated(true);
        onAnimationComplete?.();
      }, totalDuration);
      return () => clearTimeout(timer);
    }
  }, [isInView, hasAnimated, elements.length, delay, onAnimationComplete]);

  return (
    <p ref={ref} className={className}>
      {elements.map((element, i) => (
        <motion.span
          key={i}
          custom={i}
          variants={variants}
          initial="hidden"
          animate={isInView ? "visible" : "hidden"}
          style={{ display: "inline-block", whiteSpace: "pre" }}
        >
          {element}
          {animateBy === "words" && i < elements.length - 1 ? " " : ""}
        </motion.span>
      ))}
    </p>
  );
}
