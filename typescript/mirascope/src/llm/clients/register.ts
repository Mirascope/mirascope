/**
 * @fileoverview All of the LLMs registered with Mirascope.
 */

/**
 * The Anthropic models registered with Mirascope.
 */
export type AnthropicRegisteredLLMs = "anthropic:claude-3-5-sonnet-latest";

/**
 * The Google models registered with Mirascope.
 */
export type GoogleRegisteredLLMs = "google:gemini-2.5-flash";

/**
 * The OpenAI models registered with Mirascope.
 */
export type OpenAIRegisteredLLMs = "openai:gpt-4o-mini";

/**
 * The models registered with Mirascope.
 */
export type RegisteredLLMs =
  | AnthropicRegisteredLLMs
  | GoogleRegisteredLLMs
  | OpenAIRegisteredLLMs;
