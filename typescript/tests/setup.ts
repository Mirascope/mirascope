/**
 * Vitest setup file.
 *
 * Sets dummy API keys for testing when real keys aren't available.
 * This allows tests using recorded cassettes (Polly.js) to run without
 * actual API keys, since the HTTP requests are intercepted and replayed.
 *
 * Real API keys from .env will take precedence if available.
 */

const DUMMY_API_KEYS: Record<string, string> = {
  ANTHROPIC_API_KEY: "test-anthropic-api-key",
  GOOGLE_API_KEY: "test-google-api-key",
  OPENAI_API_KEY: "test-openai-api-key",
  TOGETHER_API_KEY: "test-together-api-key",
  MIRASCOPE_API_KEY: "test-mirascope-api-key",
};

// Set dummy API keys only if not already set (real keys from .env take precedence)
for (const [key, value] of Object.entries(DUMMY_API_KEYS)) {
  if (!process.env[key]) {
    process.env[key] = value;
  }
}
