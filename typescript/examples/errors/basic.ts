/**
 * Basic error handling example.
 *
 * Demonstrates catching and handling common LLM errors.
 *
 * Run with: bun run example examples/errors/basic.ts
 */
import { llm } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "openai/gpt-4o-mini",
  template: ({ genre }) => `Recommend a ${genre} book.`,
});

try {
  const response = await recommendBook({ genre: "fantasy" });
  console.log(response.text());
} catch (e) {
  if (e instanceof llm.AuthenticationError) {
    console.log(`Invalid API key: ${e.message}`);
  } else if (e instanceof llm.RateLimitError) {
    console.log(`Rate limit exceeded: ${e.message}`);
  } else if (e instanceof llm.MirascopeError) {
    console.log(`LLM error: ${e.message}`);
  } else {
    throw e;
  }
}
