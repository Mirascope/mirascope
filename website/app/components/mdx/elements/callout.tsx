import {
  AlertCircle,
  Info as InfoIcon,
  CheckCircle,
  AlertTriangle,
  ChevronDown,
  Terminal,
} from "lucide-react";
import React, { useState } from "react";

import { cn } from "@/app/lib/utils";

type CalloutType = "note" | "warning" | "info" | "success" | "api";

interface CalloutProps {
  type: CalloutType;
  title?: string;
  children: React.ReactNode;
  className?: string;
  collapsible?: boolean;
  defaultOpen?: boolean;
  customIcon?: React.ReactNode;
  contentClassName?: string;
}

const calloutStyles: Record<
  CalloutType,
  {
    containerClass: string;
    iconClass: string;
    bgClass: string;
    Icon: React.ElementType;
  }
> = {
  note: {
    containerClass: "border-primary",
    iconClass: "text-primary",
    bgClass: "bg-primary/10",
    Icon: AlertCircle,
  },
  info: {
    containerClass: "border-secondary",
    iconClass: "text-secondary",
    bgClass: "bg-secondary/10",
    Icon: InfoIcon,
  },
  warning: {
    containerClass: "border-destructive",
    iconClass: "text-destructive",
    bgClass: "bg-destructive/10",
    Icon: AlertTriangle,
  },
  success: {
    containerClass: "border-secondary",
    iconClass: "text-secondary",
    bgClass: "bg-secondary/10",
    Icon: CheckCircle,
  },
  api: {
    containerClass: "border-primary",
    iconClass: "text-primary",
    bgClass: "bg-primary/10",
    Icon: Terminal,
  },
};

export function Callout({
  type,
  title,
  children,
  className,
  collapsible = type === "api" ? true : false,
  defaultOpen = type === "api" ? false : true,
  customIcon,
  contentClassName: customContentClassName,
}: CalloutProps) {
  const { containerClass, iconClass, bgClass, Icon } = calloutStyles[type];
  const [isOpen, setIsOpen] = useState(defaultOpen);

  // Determine if we should show a header
  const showHeader = collapsible || title !== undefined;

  // Only use default title if we need a header but no title was provided
  const defaultTitle =
    showHeader && title === undefined
      ? type === "note"
        ? "Note"
        : type === "warning"
          ? "Warning"
          : type === "info"
            ? "Info"
            : type === "success"
              ? "Success"
              : type === "api"
                ? "API Documentation"
                : "Mirascope"
      : "";

  const displayTitle = title || defaultTitle;

  // Content styling changes based on whether we have a header
  const contentClassName = cn(
    showHeader ? "rounded-b-lg" : "rounded-lg",
    customContentClassName ?? "px-3 py-2",
  );

  return (
    <div className={cn("my-4 rounded-lg border", containerClass, className)}>
      {/* Title bar - only render if we need a header */}
      {showHeader && (
        <div
          className={cn(
            "flex items-center gap-1 px-2 py-2",
            // Use rounded-lg when collapsed and collapsible, otherwise just round the top
            collapsible && !isOpen ? "rounded-lg" : "rounded-t-lg",
            // Only show the bottom border when the content is expanded
            isOpen && "border-b",
            bgClass,
            isOpen ? containerClass.replace("border-", "border-b-") : "",
            collapsible && "cursor-pointer",
          )}
          onClick={collapsible ? () => setIsOpen(!isOpen) : undefined}
          aria-expanded={collapsible ? isOpen : undefined}
        >
          <div
            className={cn(
              "flex h-6 w-6 items-center justify-center rounded-full",
              iconClass,
            )}
          >
            {customIcon || <Icon className={cn("h-4 w-4")} />}
          </div>
          <div className="flex-1 text-base font-medium">{displayTitle}</div>
          {collapsible && (
            <div className="text-foreground">
              <ChevronDown
                className={cn(
                  "h-4 w-4 transition-transform",
                  !isOpen ? "" : "rotate-180",
                )}
              />
            </div>
          )}
        </div>
      )}

      {/* Content - only show if not collapsed */}
      {(!showHeader || isOpen) && (
        <div className={cn(contentClassName, "callout-content bg-background")}>
          {children}
        </div>
      )}
    </div>
  );
}

// Shorthand components
export function Note(props: Omit<CalloutProps, "type">) {
  return <Callout type="note" {...props} />;
}

export function Warning(props: Omit<CalloutProps, "type">) {
  return <Callout type="warning" {...props} />;
}

export function Info(props: Omit<CalloutProps, "type">) {
  return <Callout type="info" {...props} />;
}

export function Success(props: Omit<CalloutProps, "type">) {
  return <Callout type="success" {...props} />;
}
