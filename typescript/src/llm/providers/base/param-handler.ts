/**
 * Reusable utility for handling LLM parameters with strict checking.
 *
 * Ensures all provided params are explicitly handled, preventing silent
 * misconfiguration.
 */

import { FeatureNotSupportedError } from '@/llm/exceptions';
import type { Params } from '@/llm/models';
import type { ProviderId } from '@/llm/providers/provider-id';

/**
 * Helper for safely accessing and tracking params.
 *
 * Tracks which params have been accessed and ensures all provided params
 * are handled before completing. This prevents silently ignoring user
 * configuration.
 *
 * @example
 * ```typescript
 * // Use the static `with()` method for automatic checking:
 * const result = ParamHandler.with(params, 'anthropic', modelId, (p) => {
 *   return {
 *     max_tokens: p.getOrDefault('maxTokens', 4096),
 *     temperature: p.get('temperature'),
 *   };
 * }); // checkAllHandled() called automatically
 * ```
 */
export class ParamHandler {
  /**
   * Execute a callback with param handling, automatically checking all params
   * were handled when done.
   *
   * This is the preferred way to use ParamHandler - it ensures checkAllHandled()
   * is always called.
   */
  static with<T>(
    params: Params,
    providerId: ProviderId,
    modelId: string,
    fn: (handler: ParamHandler) => T
  ): T {
    const handler = new ParamHandler(params, providerId, modelId);
    const result = fn(handler);
    handler.checkAllHandled();
    return result;
  }
  private readonly params: Params;
  private readonly handled: Set<string> = new Set();
  private readonly providerId: ProviderId;
  private readonly modelId: string;

  constructor(params: Params, providerId: ProviderId, modelId: string) {
    this.params = params;
    this.providerId = providerId;
    this.modelId = modelId;
  }

  /**
   * Get a param value, marking it as handled.
   */
  get<K extends keyof Params>(key: K): Params[K] {
    this.handled.add(key as string);
    return this.params[key];
  }

  /**
   * Get a param value with a default, marking it as handled.
   */
  getOrDefault<K extends keyof Params, D>(
    key: K,
    defaultValue: D
  ): NonNullable<Params[K]> | D {
    this.handled.add(key as string);
    const value = this.params[key];
    return value !== undefined ? value : defaultValue;
  }

  /**
   * Check if a param is set (not undefined), marking it as handled.
   */
  has<K extends keyof Params>(key: K): boolean {
    this.handled.add(key as string);
    return this.params[key] !== undefined;
  }

  /**
   * Mark a param as not yet implemented - logs a warning if set.
   *
   * Use this for features that are planned but not yet supported.
   */
  warnNotImplemented<K extends keyof Params>(
    key: K,
    featureName: string
  ): void {
    this.handled.add(key as string);
    const value = this.params[key];
    if (value !== undefined && value !== null) {
      console.warn(
        `[mirascope] Warning: ${featureName} is not yet implemented for ${this.providerId} provider. ` +
          `The '${key as string}' parameter will be ignored.`
      );
    }
  }

  /**
   * Mark a param as unsupported by this provider - logs a warning if set.
   *
   * Use this for features the provider fundamentally doesn't support.
   * The param will be ignored but the call will proceed.
   */
  warnUnsupported<K extends keyof Params>(key: K, message?: string): void {
    this.handled.add(key as string);
    if (this.params[key] !== undefined) {
      console.warn(
        `[mirascope] Warning: ${message ?? `${this.providerId} does not support the '${key as string}' parameter`}. ` +
          `The '${key as string}' parameter will be ignored.`
      );
    }
  }

  /**
   * Verify all provided params were handled.
   *
   * Call this after processing all params. Throws if any param was
   * provided but not explicitly handled.
   */
  checkAllHandled(): void {
    for (const key of Object.keys(this.params)) {
      if (!this.handled.has(key)) {
        throw new FeatureNotSupportedError(
          `unknown param: ${key}`,
          this.providerId,
          this.modelId,
          `Unknown parameter '${key}' is not supported by ${this.providerId}`
        );
      }
    }
  }
}
