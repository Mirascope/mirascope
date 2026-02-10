import {
  CheckCircle2Icon,
  LoaderIcon,
  MessageSquareIcon,
  SendIcon,
} from "lucide-react";
import { type ReactNode, useEffect, useState } from "react";

import { ClawIcon } from "@/app/components/icons/claw-icon";
import { cn } from "@/app/lib/utils";

interface ClawDemoIntegrateProps {
  isActive: boolean;
  onComplete?: () => void;
}

const INTEGRATIONS: Array<{
  name: string;
  description: string;
  icon: ReactNode;
}> = [
  {
    name: "Slack",
    description: "Post to channels",
    icon: (
      <MessageSquareIcon className="size-4 text-slate-600 dark:text-muted-foreground" />
    ),
  },
  {
    name: "Discord",
    description: "Bot integration",
    icon: (
      <MessageSquareIcon className="size-4 text-slate-600 dark:text-muted-foreground" />
    ),
  },
  {
    name: "Telegram",
    description: "Message automation",
    icon: (
      <SendIcon className="size-4 text-slate-600 dark:text-muted-foreground" />
    ),
  },
  {
    name: "Mirascope",
    description: "Native platform",
    icon: (
      <ClawIcon className="size-4 text-slate-600 dark:text-muted-foreground" />
    ),
  },
];

type CardState = "hidden" | "loading" | "done";

export function ClawDemoIntegrate({
  isActive,
  onComplete,
}: ClawDemoIntegrateProps) {
  const [cardStates, setCardStates] = useState<CardState[]>(
    INTEGRATIONS.map(() => "hidden"),
  );

  useEffect(() => {
    if (!isActive) {
      setCardStates(INTEGRATIONS.map(() => "hidden"));
      return;
    }

    // Reveal cards one by one: hidden → loading → done
    const timers: ReturnType<typeof setTimeout>[] = [];

    INTEGRATIONS.forEach((_, i) => {
      // Show card with loader
      timers.push(
        setTimeout(
          () => {
            setCardStates((prev) => {
              const next = [...prev];
              next[i] = "loading";
              return next;
            });
          },
          300 + i * 600,
        ),
      );

      // Switch to done (green check)
      timers.push(
        setTimeout(
          () => {
            setCardStates((prev) => {
              const next = [...prev];
              next[i] = "done";
              return next;
            });
          },
          300 + i * 600 + 500,
        ),
      );
    });

    // Complete after all cards done
    timers.push(
      setTimeout(() => onComplete?.(), 300 + INTEGRATIONS.length * 600 + 2000),
    );

    return () => timers.forEach(clearTimeout);
  }, [isActive, onComplete]);

  return (
    <div className="grid grid-cols-2 gap-3 p-4">
      {INTEGRATIONS.map((integration, i) => {
        const state = cardStates[i];
        return (
          <div
            key={integration.name}
            className={cn(
              "flex flex-col items-center gap-2 rounded-lg border p-3 text-center transition-all duration-300",
              state === "hidden"
                ? "translate-y-2 border-transparent opacity-0"
                : state === "loading"
                  ? "border-slate-200 bg-slate-50 opacity-100 dark:border-border dark:bg-muted/30"
                  : "border-green-200 bg-green-50/50 opacity-100 dark:border-green-800/50 dark:bg-green-950/20",
            )}
          >
            <div className="flex items-center gap-2">
              {integration.icon}
              <span className="text-xs font-medium text-slate-700 dark:text-foreground">
                {integration.name}
              </span>
            </div>
            <p className="text-[10px] leading-tight text-slate-400 dark:text-muted-foreground">
              {integration.description}
            </p>
            <div className="h-4">
              {state === "loading" && (
                <LoaderIcon className="size-4 animate-spin text-slate-400 dark:text-muted-foreground" />
              )}
              {state === "done" && (
                <CheckCircle2Icon className="size-4 text-green-500 dark:text-green-400" />
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
