"use client";

import { useRef, useState } from "react";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/app/components/ui/tooltip";
import { cn } from "@/app/lib/utils";

export interface TruncatedTextProps {
  children: string;
  className?: string;
}

/**
 * Text component that shows a tooltip only when the text is truncated.
 * The text is displayed with ellipsis when it overflows its container.
 */
export function TruncatedText({ children, className }: TruncatedTextProps) {
  const textRef = useRef<HTMLSpanElement>(null);
  const [showTooltip, setShowTooltip] = useState(false);

  const handleMouseEnter = () => {
    const el = textRef.current;
    if (el && el.scrollWidth > el.clientWidth) {
      setShowTooltip(true);
    }
  };

  const handleMouseLeave = () => {
    setShowTooltip(false);
  };

  return (
    <Tooltip open={showTooltip}>
      <TooltipTrigger asChild>
        <span
          ref={textRef}
          className={cn(
            "block overflow-hidden text-ellipsis whitespace-nowrap",
            className,
          )}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
        >
          {children}
        </span>
      </TooltipTrigger>
      <TooltipContent>{children}</TooltipContent>
    </Tooltip>
  );
}
