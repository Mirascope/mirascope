/**
 * Utility functions for retry logic.
 */

import type { Model } from "@/llm/models";

import type { RetryConfig } from "./retry-config";

/**
 * A failed attempt to call a model.
 */
export interface RetryFailure {
  /**
   * The model that was tried.
   */
  model: Model;

  /**
   * The exception that was raised.
   */
  exception: Error;
}

/**
 * Calculate the delay before the next retry attempt.
 *
 * @param config - The retry configuration with backoff settings.
 * @param attemptForModel - The retry attempt number for this model (1-indexed).
 * @returns The delay in seconds, with exponential backoff, capped at maxDelay,
 *   and optionally with jitter applied.
 */
export function calculateDelay(
  config: RetryConfig,
  attemptForModel: number,
): number {
  // Calculate base delay with exponential backoff
  let delay =
    config.initialDelay *
    Math.pow(config.backoffMultiplier, attemptForModel - 1);

  // Cap at maxDelay
  delay = Math.min(delay, config.maxDelay);

  // Apply jitter if configured
  if (config.jitter > 0) {
    const jitterRange = delay * config.jitter;
    delay = delay + (Math.random() * 2 - 1) * jitterRange;
    // Ensure delay doesn't go negative
    delay = Math.max(0, delay);
  }

  return delay;
}

/**
 * Check if an error is retryable based on the retry configuration.
 *
 * @param error - The error to check.
 * @param config - The retry configuration.
 * @returns True if the error is retryable, false otherwise.
 */
export function isRetryableError(error: Error, config: RetryConfig): boolean {
  return config.retryOn.some((ErrorClass) => error instanceof ErrorClass);
}

/**
 * Sleep for the specified number of milliseconds.
 *
 * @param ms - The number of milliseconds to sleep.
 * @returns A promise that resolves after the delay.
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
