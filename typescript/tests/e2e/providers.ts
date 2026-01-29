/**
 * Provider configurations for parameterized e2e tests.
 */

/**
 * Configuration for a provider in parameterized tests.
 */
export interface ProviderConfig {
  /** Provider identifier (e.g., 'anthropic', 'google') */
  providerId: string;
  /** Full model ID including provider prefix (e.g., 'anthropic/claude-haiku-4-5') */
  model: string;
}

/**
 * Default providers to test against.
 * Each test will run once per provider.
 *
 * OpenAI uses smart routing - known models default to Responses API.
 * We test both APIs explicitly to ensure coverage.
 */
export const PROVIDERS: ProviderConfig[] = [
  { providerId: 'anthropic', model: 'anthropic/claude-haiku-4-5' },
  { providerId: 'google', model: 'google/gemini-2.5-flash' },
  { providerId: 'openai:completions', model: 'openai/gpt-5-mini:completions' },
  { providerId: 'openai:responses', model: 'openai/gpt-5-mini:responses' },
];

/**
 * Providers for param encoding tests.
 *
 * Uses gpt-4o-mini for OpenAI because gpt-5-mini doesn't support some params
 * (top_p on Responses API, stop sequences on Completions API).
 */
export const PROVIDERS_FOR_PARAM_TESTS: ProviderConfig[] = [
  { providerId: 'anthropic', model: 'anthropic/claude-haiku-4-5' },
  { providerId: 'google', model: 'google/gemini-2.5-flash' },
  { providerId: 'openai:completions', model: 'openai/gpt-4o-mini:completions' },
  { providerId: 'openai:responses', model: 'openai/gpt-4o-mini:responses' },
];

/**
 * Providers for thinking/reasoning tests.
 *
 * These models support extended thinking/reasoning capabilities.
 */
export const PROVIDERS_FOR_THINKING_TESTS: ProviderConfig[] = [
  { providerId: 'anthropic', model: 'anthropic/claude-sonnet-4-20250514' },
  { providerId: 'google', model: 'google/gemini-2.5-flash' },
  { providerId: 'openai:responses', model: 'openai/o4-mini:responses' },
];

/**
 * Providers for tool usage tests.
 *
 * Note: OpenAI Responses API is excluded because gpt-4o-mini keeps making
 * additional tool calls instead of responding with text after receiving
 * tool outputs. This appears to be model-specific behavior that requires
 * further investigation.
 */
export const PROVIDERS_FOR_TOOLS_TESTS: ProviderConfig[] = [
  { providerId: 'anthropic', model: 'anthropic/claude-haiku-4-5' },
  { providerId: 'google', model: 'google/gemini-2.5-flash' },
  { providerId: 'openai:completions', model: 'openai/gpt-4o-mini:completions' },
];
