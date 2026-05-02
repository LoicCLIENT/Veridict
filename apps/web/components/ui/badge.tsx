import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2.5 py-0.5 text-xs font-medium transition-colors duration-200",
  {
    variants: {
      variant: {
        default:
          "bg-[#C2E94B]/20 text-[#C2E94B]",
        success:
          "bg-[#C2E94B]/20 text-[#C2E94B]",
        neutral:
          "bg-white/[0.08] text-[#A3A99E]",
        error:
          "bg-[#E94B4B]/20 text-[#E94B4B]",
        destructive:
          "bg-[#E94B4B]/20 text-[#E94B4B] border border-[#E94B4B]/30",
        outline:
          "border border-white/20 text-[#F5F5F0] bg-transparent",
        secondary:
          "bg-[#355541] text-[#F5F5F0]",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
