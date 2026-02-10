import { useEffect, useState } from "react";

import { Badge } from "@/app/components/ui/badge";
import { cn } from "@/app/lib/utils";

const CLAW_NAME = "Kevin";
const MODEL = "Claude Sonnet 4.5";

const STATUS_SEQUENCE: Array<{
  label: string;
  pill: string;
  duration: number;
}> = [
  {
    label: "Pending",
    pill: "bg-white text-yellow-700 border-yellow-500 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-600",
    duration: 1200,
  },
  {
    label: "Provisioning",
    pill: "bg-white text-yellow-700 border-yellow-500 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-600",
    duration: 1500,
  },
  {
    label: "Active",
    pill: "bg-white text-green-700 border-green-400 dark:bg-green-950 dark:text-green-300 dark:border-green-600",
    duration: 0,
  },
];

interface ClawDemoDeployProps {
  isActive: boolean;
  onComplete?: () => void;
}

export function ClawDemoDeploy({ isActive, onComplete }: ClawDemoDeployProps) {
  const [nameChars, setNameChars] = useState(0);
  const [statusIndex, setStatusIndex] = useState(0);
  const [showModel, setShowModel] = useState(false);

  // Reset animation when tab becomes active
  useEffect(() => {
    if (!isActive) return;
    setNameChars(0);
    setStatusIndex(0);
    setShowModel(false);
  }, [isActive]);

  // Typewriter for claw name
  useEffect(() => {
    if (!isActive) return;
    if (nameChars >= CLAW_NAME.length) {
      const t = setTimeout(() => setShowModel(true), 300);
      return () => clearTimeout(t);
    }
    const t = setTimeout(() => setNameChars((c) => c + 1), 60);
    return () => clearTimeout(t);
  }, [nameChars, isActive]);

  // Status progression
  useEffect(() => {
    if (!isActive || !showModel) return;
    if (statusIndex >= STATUS_SEQUENCE.length - 1) {
      // Deploy complete — notify parent after a brief pause
      const t = setTimeout(() => onComplete?.(), 1000);
      return () => clearTimeout(t);
    }
    const t = setTimeout(
      () => setStatusIndex((i) => i + 1),
      STATUS_SEQUENCE[statusIndex].duration,
    );
    return () => clearTimeout(t);
  }, [statusIndex, showModel, isActive, onComplete]);

  const status = STATUS_SEQUENCE[statusIndex];

  return (
    <div className="flex flex-col gap-3 p-4">
      {/* Claw name input */}
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-500 dark:text-muted-foreground">
          Claw Name
        </label>
        <div className="rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-900 dark:border-border dark:bg-muted/50 dark:text-foreground">
          {CLAW_NAME.slice(0, nameChars)}
          {nameChars < CLAW_NAME.length && (
            <span className="inline-block h-[1em] w-[2px] translate-y-[1px] animate-pulse bg-mirple" />
          )}
          {nameChars === 0 && (
            <span className="text-slate-400 dark:text-muted-foreground">
              Name your Claw...
            </span>
          )}
        </div>
      </div>

      {/* Model selector */}
      <div
        className={cn(
          "transition-all duration-300",
          showModel ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0",
        )}
      >
        <label className="mb-1 block text-xs font-medium text-slate-500 dark:text-muted-foreground">
          Model
        </label>
        <div className="flex items-center justify-between rounded-md border border-slate-200 bg-white px-3 py-1.5 text-sm dark:border-border dark:bg-muted/50">
          <span className="text-slate-900 dark:text-foreground">{MODEL}</span>
          <svg
            className="size-4 text-slate-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </div>
      </div>

      {/* Status */}
      <div
        className={cn(
          "transition-all duration-300",
          showModel ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0",
        )}
      >
        <div className="flex items-center gap-3">
          <span className="text-xs font-medium text-slate-500 dark:text-muted-foreground">
            Status
          </span>
          <Badge pill variant="outline" className={cn("shrink-0", status.pill)}>
            {status.label}
          </Badge>
        </div>
      </div>
    </div>
  );
}
