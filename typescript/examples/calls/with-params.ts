/**
 * Call with parameters example.
 *
 * Demonstrates passing call parameters like temperature, topP, etc.
 * at definition time.
 *
 * Run with: bun run example examples/calls/with-params.ts
 */
import { llm } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "openai/gpt-4o-mini",
  temperature: 0.9,
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

const response = await recommendBook({ genre: "fantasy" });
console.log(response.text());
