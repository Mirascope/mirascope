/**
 * @fileoverview Centralized provider registry and configuration.
 *
 * Consolidates all provider-specific configuration including:
 * - API proxy settings (base URLs, auth headers)
 * - Provider ID mappings for pricing lookups
 * - Environment variable mappings
 * - Helper functions for provider operations
 */

import {
  OpenAICostCalculator,
  AnthropicCostCalculator,
  GoogleCostCalculator,
  type BaseCostCalculator,
} from "@/api/router/cost-calculator";

/**
 * Configuration for AI provider proxying.
 */
export interface ProxyConfig {
  /** Base URL of the provider API */
  baseUrl: string;
  /** Header name for authentication (e.g., "Authorization", "x-api-key") */
  authHeader: string;
  /** Format for the auth header value (e.g., "Bearer {key}" or just "{key}") */
  authFormat: (key: string) => string;
}

/**
 * Provider configurations for proxying.
 * Defines base URLs, authentication patterns, and models.dev IDs for each provider.
 */
export const PROVIDER_CONFIGS: Record<
  "anthropic" | "google" | "openai",
  ProxyConfig & { modelsDotDevIds: string[] }
> = {
  anthropic: {
    baseUrl: "https://api.anthropic.com",
    authHeader: "x-api-key",
    authFormat: (key: string) => key,
    modelsDotDevIds: ["anthropic"],
  },
  google: {
    baseUrl: "https://generativelanguage.googleapis.com",
    authHeader: "x-goog-api-key",
    authFormat: (key: string) => key,
    modelsDotDevIds: ["google", "google-ai-studio"],
  },
  openai: {
    baseUrl: "https://api.openai.com",
    authHeader: "Authorization",
    authFormat: (key: string) => `Bearer ${key}`,
    modelsDotDevIds: ["openai"],
  },
} as const;

/**
 * Supported provider names.
 */
export type ProviderName = keyof typeof PROVIDER_CONFIGS;

/**
 * Returns list of supported provider names.
 */
export function getSupportedProviders(): ProviderName[] {
  return Object.keys(PROVIDER_CONFIGS) as ProviderName[];
}

/**
 * Checks if a provider is supported.
 */
export function isValidProvider(provider: string): provider is ProviderName {
  return provider in PROVIDER_CONFIGS;
}

/**
 * Gets provider configuration for proxying.
 *
 * @param provider - The provider name
 * @returns Provider config without API key, or null if provider not found
 */
export function getProviderConfig(
  provider: string,
): Omit<ProxyConfig, "apiKey"> | null {
  if (!isValidProvider(provider)) {
    return null;
  }
  return PROVIDER_CONFIGS[provider];
}

/**
 * Gets the API key for a provider from environment variables.
 *
 * @param provider - The provider name
 * @returns The API key or undefined if not configured
 */
export function getProviderApiKey(provider: ProviderName): string | undefined {
  switch (provider) {
    case "openai":
      return process.env.OPENAI_API_KEY;
    case "anthropic":
      return process.env.ANTHROPIC_API_KEY;
    case "google":
      return process.env.GEMINI_API_KEY;
    /* v8 ignore next 4 */
    default: {
      const exhaustiveCheck: never = provider;
      throw new Error(`Unsupported provider: ${exhaustiveCheck as string}`);
    }
  }
}

/**
 * Gets the provider IDs used in models.dev for a given provider.
 *
 * @param provider - The provider name
 * @returns Array of provider IDs
 */
export function getModelsDotDevProviderIds(provider: ProviderName): string[] {
  return PROVIDER_CONFIGS[provider].modelsDotDevIds;
}

/**
 * Gets the cost calculator for a specific provider.
 *
 * @param provider - The provider name
 * @returns Cost calculator instance for the provider
 */
export function getCostCalculator(provider: ProviderName): BaseCostCalculator {
  switch (provider) {
    case "openai":
      return new OpenAICostCalculator();
    case "anthropic":
      return new AnthropicCostCalculator();
    case "google":
      return new GoogleCostCalculator();
    /* v8 ignore next 4 */
    default: {
      const exhaustiveCheck: never = provider;
      throw new Error(`Unsupported provider: ${exhaustiveCheck as string}`);
    }
  }
}
