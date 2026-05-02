import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-all duration-200 ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#C2E94B] focus-visible:ring-offset-2 focus-visible:ring-offset-[#1F3329] disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default:
          "bg-[#C2E94B] text-[#1F3329] font-semibold hover:bg-[#D4F06A] active:bg-[#B5DC3E]",
        destructive:
          "bg-[#E94B4B] text-[#F5F5F0] font-semibold hover:bg-[#E94B4B]/90",
        outline:
          "border border-white/20 bg-transparent text-[#F5F5F0] hover:bg-white/5 hover:border-white/30",
        secondary:
          "border border-white/20 bg-transparent text-[#F5F5F0] hover:bg-white/5 hover:border-white/30",
        ghost:
          "text-[#A3A99E] hover:text-[#F5F5F0] hover:bg-transparent",
        link:
          "text-[#C2E94B] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3 text-xs",
        lg: "h-11 rounded-md px-8 text-base",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
