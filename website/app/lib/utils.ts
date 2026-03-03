import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * Safely parse a JSON string, returning null if parsing fails.
 * Useful for parsing user-provided or potentially malformed JSON.
 */
export function safeParseJSON(
  str: string,
): Record<string, unknown> | unknown[] | null {
  try {
    return JSON.parse(str) as Record<string, unknown> | unknown[];
  } catch {
    return null;
  }
}
