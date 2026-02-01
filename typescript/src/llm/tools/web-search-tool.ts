/**
 * Web search tool for provider-native web search capabilities.
 */

import { ProviderTool } from "./provider-tool";

/**
 * Web search tool that allows the model to search the internet.
 *
 * This is a provider tool - the search is executed server-side by the provider,
 * not by your code. The model decides when to search based on the prompt,
 * and the provider returns search results with citations.
 *
 * Supported providers include Anthropic, Google, and OpenAI (when using the Responses API).
 *
 * @example
 * ```typescript
 * import { defineCall, WebSearchTool } from '@anthropic-ai/mirascope';
 *
 * const searchWeb = defineCall({
 *   model: 'anthropic/claude-sonnet-4-5',
 *   tools: [new WebSearchTool()],
 * }, () => 'Search the web for: Who won the 2024 Super Bowl?');
 *
 * const response = await searchWeb();
 * console.log(response.text()); // Response includes citations from web search
 * ```
 */
export class WebSearchTool extends ProviderTool {
  constructor() {
    super("web_search");
  }
}

/**
 * Type guard to check if a value is a WebSearchTool.
 */
export function isWebSearchTool(value: unknown): value is WebSearchTool {
  return value instanceof WebSearchTool;
}
