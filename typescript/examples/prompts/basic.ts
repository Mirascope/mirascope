/**
 * Basic prompt usage example.
 *
 * Demonstrates using definePrompt to create a reusable prompt
 * that can be called with different models.
 *
 * Run with: bun run example examples/prompts/basic.ts
 */
import { llm } from "mirascope";

/**
 * A reusable prompt for recommending books.
 * The prompt is model-agnostic - you choose the model at call time.
 */
const recommendBook = llm.definePrompt<{ genre: string }>({
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

// Call the prompt with a model
const response = await recommendBook("anthropic/claude-haiku-4-5", {
  genre: "fantasy",
});

console.log(response.text());
// The Name of the Wind by Patrick Rothfuss...
