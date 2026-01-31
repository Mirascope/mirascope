/**
 * OpenAI-compatible provider example.
 *
 * Demonstrates routing models through the OpenAI provider using
 * an OpenAI-compatible endpoint (like xAI, Together, etc.).
 *
 * Run with: bun run example examples/providers/openai-compatible.ts
 */
import { llm } from "mirascope";

// Route grok/ models through the OpenAI provider
// using xAI's OpenAI-compatible endpoint
llm.registerProvider("openai", {
  scope: "grok/",
  baseURL: "https://api.x.ai/v1",
  apiKey: process.env.XAI_API_KEY,
});

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "grok/grok-4-latest",
  template: ({ genre }) => `Recommend a ${genre} book.`,
});

const response = await recommendBook({ genre: "fantasy" });
console.log(response.text());
