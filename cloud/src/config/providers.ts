/**
 * Provider configuration and defaults
 *
 * This file defines the available providers, their defaults, and related configuration.
 * It serves as the single source of truth for provider information used throughout the application.
 */

// Define available providers using their package names
export type Provider =
  | "openai"
  | "anthropic"
  | "mistral"
  | "google"
  | "groq"
  | "xai"
  | "cohere"
  | "litellm"
  | "azure"
  | "bedrock";

// All available providers
export const providers: Provider[] = [
  "openai",
  "anthropic",
  "google",
  "groq",
  "xai",
  "mistral",
  "cohere",
  "litellm",
  "azure",
  "bedrock",
];

// Provider information including display name and default model
export const providerDefaults: Record<
  Provider,
  {
    displayName: string;
    defaultModel: string;
  }
> = {
  openai: {
    displayName: "OpenAI",
    defaultModel: "gpt-4o-mini",
  },
  anthropic: {
    displayName: "Anthropic",
    defaultModel: "claude-3-5-sonnet-latest",
  },
  mistral: {
    displayName: "Mistral",
    defaultModel: "mistral-large-latest",
  },
  xai: {
    displayName: "xAI",
    defaultModel: "grok-3",
  },
  google: {
    displayName: "Google",
    defaultModel: "gemini-2.0-flash",
  },
  groq: {
    displayName: "Groq",
    defaultModel: "llama-3.3-70b-versatile",
  },
  cohere: {
    displayName: "Cohere",
    defaultModel: "command-r-plus",
  },
  litellm: {
    displayName: "LiteLLM",
    defaultModel: "gpt-4o-mini",
  },
  azure: {
    displayName: "Azure AI",
    defaultModel: "gpt-4o-mini",
  },
  bedrock: {
    displayName: "Bedrock",
    defaultModel: "amazon.nova-lite-v1:0",
  },
};

/**
 * Get the default alternative provider and model
 * Uses Anthropic as the alternative unless the primary provider is Anthropic,
 * in which case it uses OpenAI
 */
export function getAlternativeProvider(primaryProvider: Provider): {
  provider: Provider;
  model: string;
} {
  const alternativeProvider =
    primaryProvider === "anthropic" ? "openai" : "anthropic";
  return {
    provider: alternativeProvider,
    model: providerDefaults[alternativeProvider].defaultModel,
  };
}

/**
 * Replace provider variables in content
 * Replaces $PROVIDER, $MODEL, $OTHER_PROVIDER, $OTHER_MODEL, and $PROVIDER:MODEL
 */
export function replaceProviderVariables(
  content: string,
  primaryProvider: Provider,
): string {
  const primaryInfo = providerDefaults[primaryProvider];
  const { provider: secondaryProvider, model: secondaryModel } =
    getAlternativeProvider(primaryProvider);

  const after = content
    .replace(
      /\$PROVIDER:MODEL/g,
      `${primaryProvider}:${primaryInfo.defaultModel}`,
    )
    .replace(/\$PROVIDER/g, primaryProvider)
    .replace(/\$MODEL/g, primaryInfo.defaultModel)
    .replace(/\$OTHER_PROVIDER/g, secondaryProvider)
    .replace(/\$OTHER_MODEL/g, secondaryModel);
  return after;
}
