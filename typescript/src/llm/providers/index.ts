/**
 * Interfaces for LLM providers.
 */

export type { AnthropicModelId } from '@/llm/providers/anthropic';
export type { GoogleModelId } from '@/llm/providers/google';
export type { OpenAIModelId, ApiMode } from '@/llm/providers/openai';
export type { ModelId } from '@/llm/providers/model-id';
export type { KnownProviderId, ProviderId } from '@/llm/providers/provider-id';
export { KNOWN_PROVIDER_IDS } from '@/llm/providers/provider-id';

// Base provider
export { BaseProvider } from '@/llm/providers/base';
export type { Provider, ProviderErrorMap } from '@/llm/providers/base';

export { AnthropicProvider } from '@/llm/providers/anthropic';

// Google provider
export { GoogleProvider } from '@/llm/providers/google';

// Mirascope provider
export { MirascopeProvider } from '@/llm/providers/mirascope';

// OpenAI provider
export {
  OpenAIProvider,
  OpenAICompletionsProvider,
} from '@/llm/providers/openai';

// Provider registry
export {
  getProviderForModel,
  getProviderSingleton,
  registerProvider,
  resetProviderRegistry,
} from '@/llm/providers/registry';
