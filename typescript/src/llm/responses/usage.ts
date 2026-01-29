/**
 * Token usage tracking for LLM responses.
 */

/**
 * Token usage statistics for a response.
 */
export interface Usage {
  /**
   * Total input tokens (includes cache tokens).
   */
  readonly inputTokens: number;

  /**
   * Total output tokens (includes reasoning tokens).
   */
  readonly outputTokens: number;

  /**
   * Tokens read from cache.
   */
  readonly cacheReadTokens: number;

  /**
   * Tokens written to cache.
   */
  readonly cacheWriteTokens: number;

  /**
   * Tokens used for thinking/reasoning.
   */
  readonly reasoningTokens: number;

  /**
   * Provider-specific raw usage object.
   */
  readonly raw: unknown;
}

/**
 * Create a Usage object with default values.
 */
export function createUsage(options: Partial<Usage> = {}): Usage {
  return {
    inputTokens: options.inputTokens ?? 0,
    outputTokens: options.outputTokens ?? 0,
    cacheReadTokens: options.cacheReadTokens ?? 0,
    cacheWriteTokens: options.cacheWriteTokens ?? 0,
    reasoningTokens: options.reasoningTokens ?? 0,
    raw: options.raw ?? null,
  };
}

/**
 * Calculate total tokens from usage.
 */
export function totalTokens(usage: Usage): number {
  return usage.inputTokens + usage.outputTokens;
}
