/**
 * Shared utilities for provider implementations.
 */

import type { Params } from "@/llm/models";

/**
 * Extract includeThoughts setting from params.
 *
 * @param params - The params object
 * @returns Whether to include thoughts in the response (defaults to false)
 */
export function getIncludeThoughts(params: Params = {}): boolean {
  return params.thinking?.includeThoughts ?? false;
}
