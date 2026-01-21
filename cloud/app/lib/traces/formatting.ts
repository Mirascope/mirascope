import { formatDistanceToNow } from "date-fns";

/**
 * Format a duration in milliseconds to a human-readable string.
 * Shows milliseconds for values < 1000, otherwise shows seconds with 2 decimal places.
 */
export function formatDuration(ms: number | null): string {
  if (ms === null) return "-";
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}

/**
 * Format a timestamp to a relative time string (e.g., "5 minutes ago").
 * Falls back to the original string if parsing fails.
 */
export function formatTimestamp(timestamp: string): string {
  try {
    return formatDistanceToNow(new Date(timestamp), { addSuffix: true });
  } catch {
    return timestamp;
  }
}

/**
 * Format a token count with locale-specific number formatting.
 * Returns "-" for null values.
 */
export function formatTokens(tokens: number | null): string {
  if (tokens === null) return "-";
  return tokens.toLocaleString();
}

/**
 * Format a cost in USD to a human-readable string.
 * Shows 4 decimal places for small values, 2 for larger values.
 * Returns "-" for null values.
 */
export function formatCost(costUsd: number | null): string {
  if (costUsd === null) return "-";
  if (costUsd === 0) return "$0.00";
  // Show 4 decimal places for small values (< $0.01)
  if (costUsd < 0.01) return `$${costUsd.toFixed(4)}`;
  return `$${costUsd.toFixed(2)}`;
}
