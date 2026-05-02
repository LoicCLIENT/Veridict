"use client";

import { ReactNode, CSSProperties } from "react";

interface GradientTextProps {
  children: ReactNode;
  colors?: string[];
  animationSpeed?: number;
  showBorder?: boolean;
  className?: string;
}

export default function GradientText({
  children,
  colors = ["#C2E94B", "#60efff", "#C2E94B"],
  animationSpeed = 8,
  showBorder = false,
  className = "",
}: GradientTextProps) {
  const gradientStyle: CSSProperties = {
    backgroundImage: `linear-gradient(90deg, ${colors.join(", ")})`,
    backgroundSize: "300% 100%",
    backgroundClip: "text",
    WebkitBackgroundClip: "text",
    color: "transparent",
    animation: `gradient-flow ${animationSpeed}s linear infinite`,
  };

  const borderStyle: CSSProperties = showBorder
    ? {
        borderRadius: "0.5rem",
        padding: "0.5rem 1rem",
        border: "2px solid transparent",
        backgroundImage: `linear-gradient(#1F3329, #1F3329), linear-gradient(90deg, ${colors.join(", ")})`,
        backgroundOrigin: "border-box",
        backgroundClip: "padding-box, border-box",
      }
    : {};

  return (
    <>
      <style jsx>{`
        @keyframes gradient-flow {
          0% {
            background-position: 0% 50%;
          }
          50% {
            background-position: 100% 50%;
          }
          100% {
            background-position: 0% 50%;
          }
        }
      `}</style>
      <span className={className} style={{ ...gradientStyle, ...borderStyle }}>
        {children}
      </span>
    </>
  );
}
