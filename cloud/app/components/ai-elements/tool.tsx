"use client";

import type { ToolUIPart } from "ai";
import type { ComponentProps, ReactNode } from "react";

import {
  CheckCircleIcon,
  ChevronDownIcon,
  CircleIcon,
  ClockIcon,
  WrenchIcon,
  XCircleIcon,
} from "lucide-react";
import { isValidElement } from "react";

import { Badge } from "@/app/components/ui/badge";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/app/components/ui/collapsible";
import { cn } from "@/app/lib/utils";

import { CodeBlock } from "./code-block";

export type ToolProps = ComponentProps<typeof Collapsible>;

export const Tool = ({ className, ...props }: ToolProps) => (
  <Collapsible
    className={cn("not-prose w-full rounded-md border", className)}
    {...props}
  />
);

export type ToolHeaderProps = {
  title?: string;
  type: ToolUIPart["type"];
  state: ToolUIPart["state"];
  className?: string;
};

const getStatusBadge = (status: ToolUIPart["state"]) => {
  const config: Record<
    ToolUIPart["state"],
    { label: string; icon: ReactNode; className: string }
  > = {
    "input-streaming": {
      label: "Pending",
      icon: <CircleIcon className="size-3.5" />,
      className:
        "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
    },
    "input-available": {
      label: "Running",
      icon: <ClockIcon className="size-3.5 animate-pulse" />,
      className:
        "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
    },
    "approval-requested": {
      label: "Awaiting Approval",
      icon: <ClockIcon className="size-3.5" />,
      className:
        "bg-amber-100 text-amber-700 dark:bg-amber-900 dark:text-amber-300",
    },
    "approval-responded": {
      label: "Responded",
      icon: <CheckCircleIcon className="size-3.5" />,
      className:
        "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300",
    },
    "output-available": {
      label: "Completed",
      icon: <CheckCircleIcon className="size-3.5" />,
      className:
        "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
    },
    "output-error": {
      label: "Error",
      icon: <XCircleIcon className="size-3.5" />,
      className: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
    },
    "output-denied": {
      label: "Denied",
      icon: <XCircleIcon className="size-3.5" />,
      className:
        "bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300",
    },
  };

  const { label, icon, className } = config[status];

  return (
    <Badge
      variant="outline"
      className={cn(
        "gap-1.5 rounded-full border-0 text-xs font-medium",
        className,
      )}
    >
      {icon}
      {label}
    </Badge>
  );
};

export const ToolHeader = ({
  className,
  title,
  type,
  state,
  ...props
}: ToolHeaderProps) => (
  <CollapsibleTrigger
    className={cn(
      "flex w-full items-center justify-between gap-4 p-3",
      className,
    )}
    {...props}
  >
    <div className="flex items-center gap-2">
      <WrenchIcon className="size-4 text-muted-foreground" />
      <span className="font-medium text-sm">
        {title ?? type.split("-").slice(1).join("-")}
      </span>
      {getStatusBadge(state)}
    </div>
    <ChevronDownIcon className="size-4 text-muted-foreground transition-transform group-data-[state=open]:rotate-180" />
  </CollapsibleTrigger>
);

export type ToolContentProps = ComponentProps<typeof CollapsibleContent>;

export const ToolContent = ({ className, ...props }: ToolContentProps) => (
  <CollapsibleContent
    className={cn(
      "data-[state=closed]:fade-out-0 data-[state=closed]:slide-out-to-top-2 data-[state=open]:slide-in-from-top-2 text-popover-foreground outline-none data-[state=closed]:animate-out data-[state=open]:animate-in",
      className,
    )}
    {...props}
  />
);

export type ToolInputProps = ComponentProps<"div"> & {
  input: ToolUIPart["input"];
};

export const ToolInput = ({ className, input, ...props }: ToolInputProps) => (
  <div className={cn("space-y-2 overflow-hidden p-4", className)} {...props}>
    <h4 className="font-medium text-muted-foreground text-xs uppercase tracking-wide">
      Parameters
    </h4>
    <div className="rounded-md bg-muted/50">
      <CodeBlock code={JSON.stringify(input, null, 2)} language="json" />
    </div>
  </div>
);

export type ToolOutputProps = ComponentProps<"div"> & {
  output: ToolUIPart["output"];
  errorText: ToolUIPart["errorText"];
};

export const ToolOutput = ({
  className,
  output,
  errorText,
  ...props
}: ToolOutputProps) => {
  if (!(output || errorText)) {
    return null;
  }

  let Output = <div>{output as ReactNode}</div>;

  if (typeof output === "object" && !isValidElement(output)) {
    Output = (
      <CodeBlock code={JSON.stringify(output, null, 2)} language="json" />
    );
  } else if (typeof output === "string") {
    Output = <CodeBlock code={output} language="json" />;
  }

  return (
    <div className={cn("space-y-2 p-4", className)} {...props}>
      <h4 className="font-medium text-muted-foreground text-xs uppercase tracking-wide">
        {errorText ? "Error" : "Result"}
      </h4>
      <div
        className={cn(
          "overflow-x-auto rounded-md text-xs [&_table]:w-full",
          errorText
            ? "bg-destructive/10 text-destructive"
            : "bg-muted/50 text-foreground",
        )}
      >
        {errorText && <div>{errorText}</div>}
        {Output}
      </div>
    </div>
  );
};
