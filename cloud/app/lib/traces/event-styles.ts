import type { ReactNode } from "react";
import { AlertCircle, AlertTriangle, Bug, Info } from "lucide-react";
import { createElement } from "react";

/** Known event levels that have special styling */
export const KNOWN_LEVELS = new Set([
  "info",
  "warning",
  "error",
  "critical",
  "debug",
]);

export type EventLevel = "info" | "warning" | "error" | "critical" | "debug";

export interface LevelStyles {
  icon: ReactNode;
  badgeClass: string;
}

/**
 * Get level-specific styles for event display.
 * Returns an icon component and Tailwind CSS classes for the badge.
 */
export function getLevelStyles(level: string): LevelStyles {
  switch (level.toLowerCase()) {
    case "info":
      return {
        icon: createElement(Info, { size: 14 }),
        badgeClass:
          "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900/30",
      };
    case "warning":
      return {
        icon: createElement(AlertTriangle, { size: 14 }),
        badgeClass:
          "text-amber-600 bg-amber-100 dark:text-amber-400 dark:bg-amber-900/30",
      };
    case "error":
      return {
        icon: createElement(AlertCircle, { size: 14 }),
        badgeClass:
          "text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/30",
      };
    case "critical":
      return {
        icon: createElement(AlertCircle, { size: 14 }),
        badgeClass:
          "text-red-800 bg-red-200 dark:text-red-300 dark:bg-red-900/50",
      };
    case "debug":
      return {
        icon: createElement(Bug, { size: 14 }),
        badgeClass:
          "text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-800",
      };
    default:
      return { icon: null, badgeClass: "bg-muted" };
  }
}
