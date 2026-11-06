/**
 * Identifiers for all registered providers.
 */

/**
 * Array of known provider IDs for runtime checks.
 */
export const KNOWN_PROVIDER_IDS = [
  "anthropic",
  "anthropic-beta",
  "api-route",
  "atlascloud",
  "cheaperinference",
  "google",
  "minimax",
  "mirascope",
  "ollama",
  "openai",
  "openrouter",
  "opper",
  "requesty",
  "together",
  "xai",
] as const;

/**
 * Known provider identifiers.
 */
export type KnownProviderId = (typeof KNOWN_PROVIDER_IDS)[number];

/**
 * Provider identifier.
 *
 * Can be a known provider or any custom string for extensibility.
 */
export type ProviderId = KnownProviderId | (string & {});
