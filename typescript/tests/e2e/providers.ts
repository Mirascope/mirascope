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
 */
export const PROVIDERS: ProviderConfig[] = [
  { providerId: 'anthropic', model: 'anthropic/claude-haiku-4-5' },
  { providerId: 'google', model: 'google/gemini-2.5-flash' },
];
