/**
 * Runtime model override example.
 *
 * Demonstrates overriding the model at runtime using withModel.
 *
 * Run with: bun run example examples/calls/override.ts
 */
import { llm } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "openai/gpt-4o-mini",
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

// Override the model at runtime
const response = await llm.withModel(
  "anthropic/claude-haiku-4-5",
  { temperature: 0.9 },
  async () => {
    return recommendBook({ genre: "fantasy" });
  },
);

console.log(response.text());
