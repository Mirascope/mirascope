/**
 * Custom API key example.
 *
 * Demonstrates registering a provider with a custom API key or base URL.
 *
 * Run with: bun run example examples/providers/custom-api-key.ts
 */
import { llm } from "mirascope";

// Use a different API key for OpenAI
llm.registerProvider("openai", { apiKey: "sk-my-other-key" });

// Or point to a different endpoint (e.g., a proxy)
llm.registerProvider("openai", { baseURL: "https://my-proxy.example.com/v1" });

// Now all openai/ calls use the registered configuration
const response = await llm.useModel("openai/gpt-4o-mini").call("Say hello");
console.log(response.text());
