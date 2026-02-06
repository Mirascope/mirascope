import { useRef, useState, useEffect, useCallback } from "react";

import type { Claw } from "@/api/claws.schemas";

import { Badge } from "@/app/components/ui/badge";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/app/components/ui/tooltip";

export const statusConfig: Record<
  Claw["status"],
  {
    card: string;
    pill: string;
    label: string;
  }
> = {
  active: {
    card: "border-green-300/40 bg-green-100/60 hover:bg-green-100/80 dark:border-green-700/40 dark:bg-green-950/40 dark:hover:bg-green-950/60",
    pill: "bg-white text-green-700 border-green-400 dark:bg-green-950 dark:text-green-300 dark:border-green-600",
    label: "Active",
  },
  pending: {
    card: "border-yellow-300/40 bg-yellow-100/60 hover:bg-yellow-100/80 dark:border-yellow-700/40 dark:bg-yellow-950/40 dark:hover:bg-yellow-950/60",
    pill: "bg-white text-yellow-700 border-yellow-500 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-600",
    label: "Pending",
  },
  provisioning: {
    card: "border-yellow-300/40 bg-yellow-100/60 hover:bg-yellow-100/80 dark:border-yellow-700/40 dark:bg-yellow-950/40 dark:hover:bg-yellow-950/60",
    pill: "bg-white text-yellow-700 border-yellow-500 dark:bg-yellow-950 dark:text-yellow-300 dark:border-yellow-600",
    label: "Provisioning",
  },
  error: {
    card: "border-red-300/40 bg-red-100/60 hover:bg-red-100/80 dark:border-red-700/40 dark:bg-red-950/40 dark:hover:bg-red-950/60",
    pill: "bg-white text-red-700 border-red-400 dark:bg-red-950 dark:text-red-300 dark:border-red-600",
    label: "Error",
  },
  paused: {
    card: "border-gray-300/40 bg-gray-100/60 hover:bg-gray-100/80 dark:border-gray-700/40 dark:bg-gray-800/40 dark:hover:bg-gray-800/60",
    pill: "bg-white text-gray-600 border-gray-400 dark:bg-gray-900 dark:text-gray-300 dark:border-gray-600",
    label: "Paused",
  },
};

export const instanceConfig: Record<Claw["instanceType"], string> = {
  lite: "Lite",
  basic: "Small",
  "standard-1": "Medium",
  "standard-2": "Medium",
  "standard-3": "Large",
  "standard-4": "XL",
};

function useIsTruncated() {
  const ref = useRef<HTMLSpanElement>(null);
  const [truncated, setTruncated] = useState(false);

  const check = useCallback(() => {
    const el = ref.current;
    if (el) {
      setTruncated(el.scrollWidth > el.clientWidth);
    }
  }, []);

  useEffect(() => {
    check();
    const observer = new ResizeObserver(check);
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [check]);

  return { ref, truncated };
}

/** Color class for the filled portion of usage bars, keyed by claw status. */
export const statusBarColor: Record<Claw["status"], string> = {
  active: "bg-green-500 dark:bg-green-400",
  pending: "bg-yellow-500 dark:bg-yellow-400",
  provisioning: "bg-yellow-500 dark:bg-yellow-400",
  error: "bg-red-500 dark:bg-red-400",
  paused: "bg-gray-400 dark:bg-gray-500",
};

export function UsageMeter({
  usage,
  limit,
  barColor,
  className,
}: {
  usage: number;
  limit: number;
  barColor: string;
  className?: string;
}) {
  const pct = limit > 0 ? Math.min((usage / limit) * 100, 100) : 0;
  const ratio = limit > 0 ? usage / limit : 0;

  let color = barColor;
  if (ratio > 1) {
    color = "bg-red-500 dark:bg-red-400";
  } else if (ratio > 0.9) {
    color = "bg-amber-500 dark:bg-amber-400";
  }

  return (
    <div
      className={`h-1.5 rounded-full bg-black/5 dark:bg-white/10 overflow-hidden ${className ?? ""}`}
    >
      <div
        className={`h-full rounded-full transition-all ${color}`}
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

interface ClawCardProps {
  claw: Claw;
  onClick?: () => void;
  burstLimitCenticents?: number | null;
}

export function ClawCard({
  claw,
  onClick,
  burstLimitCenticents,
}: ClawCardProps) {
  const status = statusConfig[claw.status];
  const name = useIsTruncated();
  const slug = useIsTruncated();

  const nameText = claw.displayName ?? claw.slug;
  return (
    <Card
      className={`cursor-pointer transition-colors min-h-[5.5rem] ${status.card}`}
      onClick={onClick}
    >
      <CardHeader className="p-4">
        <CardTitle className="flex items-center gap-2 text-base">
          <Tooltip>
            <TooltipTrigger asChild>
              <span ref={name.ref} className="truncate">
                {nameText}
              </span>
            </TooltipTrigger>
            {name.truncated && <TooltipContent>{nameText}</TooltipContent>}
          </Tooltip>
          <Badge
            pill
            variant="outline"
            className="shrink-0 font-normal bg-white text-primary border-primary/40 dark:bg-primary/10 dark:text-primary-foreground dark:border-primary/40"
          >
            {instanceConfig[claw.instanceType]}
          </Badge>
          <Badge
            pill
            variant="outline"
            className={`shrink-0 ml-auto ${status.pill}`}
          >
            {status.label}
          </Badge>
        </CardTitle>
        <CardDescription className="flex items-center gap-2 text-sm">
          <Tooltip>
            <TooltipTrigger asChild>
              <span ref={slug.ref} className="truncate shrink-0">
                {claw.slug}
              </span>
            </TooltipTrigger>
            {slug.truncated && <TooltipContent>{claw.slug}</TooltipContent>}
          </Tooltip>
          {burstLimitCenticents != null && (
            <UsageMeter
              usage={Number(claw.burstUsageCenticents ?? 0n)}
              limit={burstLimitCenticents}
              barColor={statusBarColor[claw.status]}
              className="flex-1 min-w-8 ml-2"
            />
          )}
        </CardDescription>
      </CardHeader>
    </Card>
  );
}
