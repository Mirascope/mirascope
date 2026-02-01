/**
 * Prompt with model parameters example.
 *
 * Demonstrates using llm.Model to configure model parameters
 * like temperature when calling a prompt.
 *
 * Run with: bun run example examples/prompts/with-params.ts
 */
import { llm } from "mirascope";

/**
 * A reusable prompt for recommending books.
 */
const recommendBook = llm.definePrompt<{ genre: string }>({
  template: ({ genre }) => `Please recommend a book in ${genre}.`,
});

// Use llm.Model when you need to configure parameters
const model = llm.model("openai/gpt-4o", { temperature: 0.9 });
const response = await recommendBook(model, { genre: "fantasy" });

console.log(response.text());
// A highly creative recommendation with temperature=0.9...
