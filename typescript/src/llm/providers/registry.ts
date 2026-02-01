/**
 * Provider registry for managing provider instances.
 *
 * Provides automatic provider resolution based on model ID prefixes.
 */

import {
  MissingAPIKeyError,
  NoRegisteredProviderError,
} from '@/llm/exceptions';
import type { BaseProvider } from '@/llm/providers/base';
import { AnthropicProvider } from '@/llm/providers/anthropic';
import { GoogleProvider } from '@/llm/providers/google';
import { MirascopeProvider } from '@/llm/providers/mirascope';
import { OllamaProvider } from '@/llm/providers/ollama';
import { OpenAIProvider } from '@/llm/providers/openai/provider';
import type { ProviderId } from '@/llm/providers/provider-id';

/**
 * Global registry mapping scopes to providers.
 * Scopes are matched by prefix (longest match wins).
 */
const PROVIDER_REGISTRY: Map<string, BaseProvider> = new Map();

/**
 * Reset the provider registry, clearing all registered providers.
 * Primarily useful for testing.
 */
export function resetProviderRegistry(): void {
  PROVIDER_REGISTRY.clear();
  providerCache.clear();
}

/**
 * Configuration for a provider in the auto-registration fallback chain.
 */
interface ProviderDefault {
  providerId: ProviderId;
  apiKeyEnvVar: string | null;
}

/**
 * Default auto-registration scopes with fallback chains.
 */
const DEFAULT_AUTO_REGISTER_SCOPES: Record<string, ProviderDefault[]> = {
  'anthropic/': [
    { providerId: 'anthropic', apiKeyEnvVar: 'ANTHROPIC_API_KEY' },
  ],
  'google/': [{ providerId: 'google', apiKeyEnvVar: 'GOOGLE_API_KEY' }],
  'mirascope/': [
    { providerId: 'mirascope', apiKeyEnvVar: 'MIRASCOPE_API_KEY' },
  ],
  'ollama/': [{ providerId: 'ollama', apiKeyEnvVar: null }],
  'openai/': [{ providerId: 'openai', apiKeyEnvVar: 'OPENAI_API_KEY' }],
};

/**
 * Check if an API key is available for a provider default.
 */
function hasApiKey(defaultConfig: ProviderDefault): boolean {
  /* v8 ignore start - no current providers without API key requirement */
  if (defaultConfig.apiKeyEnvVar === null) {
    return true; // Provider doesn't require API key
  }
  /* v8 ignore stop */
  return process.env[defaultConfig.apiKeyEnvVar] !== undefined;
}

/**
 * Cache for provider singletons.
 */
const providerCache: Map<string, BaseProvider> = new Map();

/**
 * Create a cached provider instance for the specified provider ID.
 * Uses a cache keyed by providerId + apiKey + baseURL for reuse.
 */
export function getProviderSingleton(
  providerId: ProviderId,
  options?: { apiKey?: string; baseURL?: string }
): BaseProvider {
  const cacheKey = `${providerId}:${options?.apiKey ?? ''}:${options?.baseURL ?? ''}`;
  const cached = providerCache.get(cacheKey);
  if (cached) {
    return cached;
  }

  let provider: BaseProvider;
  switch (providerId) {
    case 'anthropic':
      provider = new AnthropicProvider({
        apiKey: options?.apiKey,
        baseURL: options?.baseURL,
      });
      break;
    case 'google':
      provider = new GoogleProvider({
        apiKey: options?.apiKey,
        baseURL: options?.baseURL,
      });
      break;
    case 'mirascope':
      provider = new MirascopeProvider({
        apiKey: options?.apiKey,
        baseURL: options?.baseURL,
      });
      break;
    case 'ollama':
      provider = new OllamaProvider({
        apiKey: options?.apiKey,
        baseURL: options?.baseURL,
      });
      break;
    case 'openai':
      provider = new OpenAIProvider({
        apiKey: options?.apiKey,
        baseURL: options?.baseURL,
      });
      break;
    default:
      throw new Error(`Unknown provider: '${providerId}'`);
  }

  providerCache.set(cacheKey, provider);
  return provider;
}

/**
 * Register a provider with scope(s) in the global registry.
 *
 * Scopes use prefix matching on model IDs:
 * - "anthropic/" matches "anthropic/*"
 * - "anthropic/claude-sonnet-4" matches "anthropic/claude-sonnet-4*"
 *
 * When multiple scopes match a model_id, the longest match wins.
 *
 * @example
 * ```typescript
 * // Register with default scope
 * registerProvider('anthropic', { apiKey: 'key' });
 *
 * // Register for specific models
 * registerProvider('anthropic', { scope: 'anthropic/claude-sonnet-4' });
 *
 * // Register a custom instance
 * const custom = new AnthropicProvider({ apiKey: 'team-key' });
 * registerProvider(custom, { scope: 'anthropic/claude-sonnet-4' });
 * ```
 */
export function registerProvider(
  provider: ProviderId | BaseProvider,
  options?: {
    scope?: string | string[];
    apiKey?: string;
    baseURL?: string;
  }
): BaseProvider {
  let providerInstance: BaseProvider;

  if (typeof provider === 'string') {
    providerInstance = getProviderSingleton(provider, {
      apiKey: options?.apiKey,
      baseURL: options?.baseURL,
    });
  } else {
    providerInstance = provider;
  }

  // Determine scopes to register
  let scopes: string[];
  if (options?.scope) {
    scopes = Array.isArray(options.scope) ? options.scope : [options.scope];
  } else {
    // Use default scope based on provider ID
    scopes = [`${providerInstance.id}/`];
  }

  for (const scope of scopes) {
    PROVIDER_REGISTRY.set(scope, providerInstance);
  }

  return providerInstance;
}

/**
 * Get the provider for a model ID based on the registry.
 *
 * Uses longest prefix matching to find the most specific provider for the model.
 * If no explicit registration is found, checks for auto-registration defaults
 * and automatically registers the provider on first use.
 *
 * @param modelId - The full model ID (e.g., "anthropic/claude-sonnet-4-20250514").
 * @returns The provider instance registered for this model.
 * @throws NoRegisteredProviderError if no provider scope matches the model ID.
 * @throws MissingAPIKeyError if no provider has its API key set.
 *
 * @example
 * ```typescript
 * // Auto-registration on first use:
 * const provider = getProviderForModel('anthropic/claude-sonnet-4-20250514');
 * // Automatically loads and registers AnthropicProvider for "anthropic/"
 * ```
 */
export function getProviderForModel(modelId: string): BaseProvider {
  // Try explicit registry first (longest match wins)
  const matchingScopes = [...PROVIDER_REGISTRY.keys()].filter((scope) =>
    modelId.startsWith(scope)
  );

  if (matchingScopes.length > 0) {
    /* v8 ignore next 3 - reduce comparison for multiple scope matches, only Anthropic implemented */
    const bestScope = matchingScopes.reduce((a, b) =>
      a.length > b.length ? a : b
    );
    return PROVIDER_REGISTRY.get(bestScope)!;
  }

  // Fall back to auto-registration
  const matchingDefaults = Object.keys(DEFAULT_AUTO_REGISTER_SCOPES).filter(
    (scope) => modelId.startsWith(scope)
  );

  if (matchingDefaults.length > 0) {
    /* v8 ignore next 3 - reduce only runs with multiple scope matches, only Anthropic implemented */
    const bestScope = matchingDefaults.reduce((a, b) =>
      a.length > b.length ? a : b
    );
    const fallbackChain = DEFAULT_AUTO_REGISTER_SCOPES[bestScope]!;

    // Try each provider in the fallback chain
    for (const defaultConfig of fallbackChain) {
      if (hasApiKey(defaultConfig)) {
        const provider = getProviderSingleton(defaultConfig.providerId);
        // Register for just this scope
        PROVIDER_REGISTRY.set(bestScope, provider);
        return provider;
      }
    }

    // No provider in chain has API key - raise helpful error
    const primary = fallbackChain[0]!;
    throw new MissingAPIKeyError(
      primary.providerId,
      /* v8 ignore next - apiKeyEnvVar always defined for current providers */
      primary.apiKeyEnvVar ?? '',
      false
    );
  }

  // No matching scope at all
  throw new NoRegisteredProviderError(modelId);
}
