import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-10 w-full rounded-lg bg-[#2A4435] px-3 py-2 text-sm text-[#F5F5F0] border border-white/[0.12] transition-colors duration-200 ease-out",
          "placeholder:text-[#A3A99E]",
          "focus:outline-none focus:border-[#C2E94B] focus:ring-1 focus:ring-[#C2E94B]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-[#F5F5F0]",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
