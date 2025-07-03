/**
 * @fileoverview All of the LLMs registered with Mirascope.
 */

/**
 * The Anthropic models registered with Mirascope.
 */
export type ANTHROPIC_REGISTERED_LLMS = 'anthropic:claude-3-5-sonnet-latest';

/**
 * The Google models registered with Mirascope.
 */
export type GOOGLE_REGISTERED_LLMS = 'google:gemini-2.5-flash';

/**
 * The OpenAI models registered with Mirascope.
 */
export type OPENAI_REGISTERED_LLMS = 'openai:gpt-4o-mini';

/**
 * The models registered with Mirascope.
 */
export type REGISTERED_LLMS =
  | ANTHROPIC_REGISTERED_LLMS
  | GOOGLE_REGISTERED_LLMS
  | OPENAI_REGISTERED_LLMS;
