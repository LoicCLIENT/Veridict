"use client";

import { motion } from "framer-motion";
import { Check } from "lucide-react";
import { WIZARD_STEPS } from "./types";

interface StepIndicatorProps {
  currentStep: number;
  onStepClick?: (step: number) => void;
}

export function StepIndicator({ currentStep, onStepClick }: StepIndicatorProps) {
  return (
    <div className="w-full">
      {/* Mobile: Simple progress bar */}
      <div className="lg:hidden mb-8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-veridict-white">
            Step {currentStep} of {WIZARD_STEPS.length}
          </span>
          <span className="text-sm text-veridict-gray">
            {WIZARD_STEPS[currentStep - 1]?.title}
          </span>
        </div>
        <div className="h-1 bg-veridict-green-800 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-veridict-lime rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${(currentStep / WIZARD_STEPS.length) * 100}%` }}
            transition={{ duration: 0.3, ease: "easeOut" }}
          />
        </div>
      </div>

      {/* Desktop: Full stepper */}
      <div className="hidden lg:flex items-center justify-center gap-0 mb-12">
        {WIZARD_STEPS.map((step, index) => {
          const isCompleted = currentStep > step.id;
          const isCurrent = currentStep === step.id;
          const isClickable = onStepClick && (isCompleted || isCurrent);

          return (
            <div key={step.id} className="flex items-center">
              {/* Step circle and content */}
              <button
                onClick={() => isClickable && onStepClick?.(step.id)}
                disabled={!isClickable}
                className={`
                  flex flex-col items-center gap-2 group relative
                  ${isClickable ? "cursor-pointer" : "cursor-default"}
                `}
              >
                {/* Circle */}
                <motion.div
                  className={`
                    relative w-10 h-10 rounded-full flex items-center justify-center
                    font-semibold text-sm transition-all duration-300
                    ${isCompleted
                      ? "bg-veridict-lime text-veridict-green-900"
                      : isCurrent
                        ? "bg-veridict-lime/20 text-veridict-lime border-2 border-veridict-lime"
                        : "bg-veridict-green-800 text-veridict-gray border border-veridict-green-700"
                    }
                    ${isClickable && !isCurrent ? "group-hover:scale-110" : ""}
                  `}
                  initial={false}
                  animate={isCurrent ? { scale: [1, 1.05, 1] } : {}}
                  transition={{ duration: 0.5, repeat: isCurrent ? Infinity : 0, repeatDelay: 2 }}
                >
                  {isCompleted ? (
                    <Check className="w-5 h-5" strokeWidth={3} />
                  ) : (
                    step.id
                  )}

                  {/* Pulse ring for current step */}
                  {isCurrent && (
                    <motion.div
                      className="absolute inset-0 rounded-full border-2 border-veridict-lime"
                      initial={{ scale: 1, opacity: 0.5 }}
                      animate={{ scale: 1.4, opacity: 0 }}
                      transition={{ duration: 1.5, repeat: Infinity }}
                    />
                  )}
                </motion.div>

                {/* Label */}
                <div className="text-center">
                  <p className={`
                    text-xs font-medium transition-colors
                    ${isCurrent ? "text-veridict-lime" : isCompleted ? "text-veridict-white" : "text-veridict-gray"}
                  `}>
                    {step.title}
                  </p>
                </div>
              </button>

              {/* Connector line */}
              {index < WIZARD_STEPS.length - 1 && (
                <div className="w-16 xl:w-24 h-px mx-4 relative">
                  <div className="absolute inset-0 bg-veridict-green-700" />
                  <motion.div
                    className="absolute inset-y-0 left-0 bg-veridict-lime"
                    initial={{ width: 0 }}
                    animate={{ width: isCompleted ? "100%" : "0%" }}
                    transition={{ duration: 0.3, ease: "easeOut" }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
