/**
 * Configuration for retry behavior.
 */

import type { Model } from "@/llm/models";
import type { ModelId } from "@/llm/providers";

import {
  ConnectionError,
  RateLimitError,
  ServerError,
  TimeoutError,
} from "@/llm/exceptions";

/**
 * Default exceptions that trigger a retry.
 *
 * These are transient errors that are likely to succeed on retry:
 * - ConnectionError: Network issues, DNS failures
 * - RateLimitError: Rate limits exceeded (429)
 * - ServerError: Provider-side errors (500+)
 * - TimeoutError: Request timeouts
 */
export const DEFAULT_RETRYABLE_ERRORS: ErrorConstructor[] = [
  ConnectionError,
  RateLimitError,
  ServerError,
  TimeoutError,
];

/**
 * Default maximum number of retries after the initial attempt fails.
 */
export const DEFAULT_MAX_RETRIES = 3;

/**
 * Default initial delay in seconds before the first retry.
 */
export const DEFAULT_INITIAL_DELAY = 0.5;

/**
 * Default maximum delay in seconds between retries.
 */
export const DEFAULT_MAX_DELAY = 60.0;

/**
 * Default multiplier for exponential backoff (delay *= multiplier after each retry).
 */
export const DEFAULT_BACKOFF_MULTIPLIER = 2.0;

/**
 * Default jitter factor (0.0 to 1.0) to add randomness to delays.
 *
 * A jitter of 0.1 means +/- 10% random variation on the calculated delay.
 */
export const DEFAULT_JITTER = 0.0;

/**
 * Constructor type for error classes.
 * Uses a generic signature to match both built-in Error and custom error classes.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type ErrorConstructor = new (...args: any[]) => Error;

/**
 * Arguments for configuring retry behavior.
 *
 * This interface is used for the user-facing API where all fields are optional.
 * Use RetryConfig for the internal representation with defaults applied.
 */
export interface RetryArgs {
  /**
   * Maximum number of retries after the initial attempt fails. Defaults to 3.
   */
  maxRetries?: number;

  /**
   * Array of exception types that should trigger a retry.
   *
   * Defaults to DEFAULT_RETRYABLE_ERRORS (ConnectionError, RateLimitError,
   * ServerError, TimeoutError).
   */
  retryOn?: ErrorConstructor[];

  /**
   * Initial delay in seconds before the first retry. Defaults to 0.5.
   */
  initialDelay?: number;

  /**
   * Maximum delay in seconds between retries. Defaults to 60.0.
   */
  maxDelay?: number;

  /**
   * Multiplier for exponential backoff (delay *= multiplier after each retry). Defaults to 2.0.
   */
  backoffMultiplier?: number;

  /**
   * Jitter factor (0.0 to 1.0) to add randomness to delays. Defaults to 0.0.
   */
  jitter?: number;

  /**
   * Sequence of fallback models to try if the primary model fails.
   *
   * Each model gets its own full retry budget (maxRetries applies per model).
   * ModelId strings inherit params from the primary model; Model instances
   * use their own params. Defaults to empty array (no fallbacks).
   */
  fallbackModels?: Array<Model | ModelId>;
}

/**
 * Configuration for retry behavior with defaults applied.
 *
 * This class validates configuration values and provides defaults for any
 * unspecified options.
 */
export class RetryConfig {
  /**
   * Maximum number of retries after the initial attempt fails.
   */
  readonly maxRetries: number;

  /**
   * Array of exception types that should trigger a retry.
   */
  readonly retryOn: ErrorConstructor[];

  /**
   * Sequence of fallback models to try if the primary model fails.
   */
  readonly fallbackModels: Array<Model | ModelId>;

  /**
   * Initial delay in seconds before the first retry.
   */
  readonly initialDelay: number;

  /**
   * Maximum delay in seconds between retries.
   */
  readonly maxDelay: number;

  /**
   * Multiplier for exponential backoff.
   */
  readonly backoffMultiplier: number;

  /**
   * Jitter factor (0.0 to 1.0) to add randomness to delays.
   */
  readonly jitter: number;

  /**
   * Create a RetryConfig with optional overrides.
   *
   * @param args - Optional configuration overrides.
   * @throws Error if any configuration values are invalid.
   */
  constructor(args: RetryArgs = {}) {
    this.maxRetries = args.maxRetries ?? DEFAULT_MAX_RETRIES;
    this.retryOn = args.retryOn ?? [...DEFAULT_RETRYABLE_ERRORS];
    this.fallbackModels = args.fallbackModels ?? [];
    this.initialDelay = args.initialDelay ?? DEFAULT_INITIAL_DELAY;
    this.maxDelay = args.maxDelay ?? DEFAULT_MAX_DELAY;
    this.backoffMultiplier =
      args.backoffMultiplier ?? DEFAULT_BACKOFF_MULTIPLIER;
    this.jitter = args.jitter ?? DEFAULT_JITTER;

    // Validation
    if (this.maxRetries < 0) {
      throw new Error("maxRetries must be non-negative");
    }
    if (this.initialDelay < 0) {
      throw new Error("initialDelay must be non-negative");
    }
    if (this.maxDelay < 0) {
      throw new Error("maxDelay must be non-negative");
    }
    if (this.backoffMultiplier < 1) {
      throw new Error("backoffMultiplier must be >= 1");
    }
    if (this.jitter < 0 || this.jitter > 1) {
      throw new Error("jitter must be between 0.0 and 1.0");
    }
  }

  /**
   * Create a RetryConfig from RetryArgs.
   *
   * @param args - Optional configuration overrides.
   * @returns A new RetryConfig instance.
   */
  static fromArgs(args: RetryArgs = {}): RetryConfig {
    return new RetryConfig(args);
  }
}
