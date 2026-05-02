"use client";

import { CSSProperties } from "react";

interface ShinyTextProps {
  text: string;
  disabled?: boolean;
  speed?: number;
  className?: string;
}

export default function ShinyText({
  text,
  disabled = false,
  speed = 5,
  className = "",
}: ShinyTextProps) {
  const animationDuration = `${speed}s`;

  const shinyStyle: CSSProperties = {
    backgroundImage:
      "linear-gradient(120deg, rgba(255,255,255,0) 40%, rgba(255,255,255,0.8) 50%, rgba(255,255,255,0) 60%)",
    backgroundSize: "200% 100%",
    WebkitBackgroundClip: "text",
    backgroundClip: "text",
    animation: disabled ? "none" : `shine ${animationDuration} linear infinite`,
  };

  return (
    <>
      <style jsx>{`
        @keyframes shine {
          0% {
            background-position: 100% 0;
          }
          100% {
            background-position: -100% 0;
          }
        }
      `}</style>
      <span className={className} style={shinyStyle}>
        {text}
      </span>
    </>
  );
}
