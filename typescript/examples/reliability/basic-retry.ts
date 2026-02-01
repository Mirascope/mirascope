/**
 * Basic retry example.
 *
 * Demonstrates a simple retry loop for handling transient LLM errors.
 *
 * Run with: bun run example examples/reliability/basic-retry.ts
 */
import { llm } from "mirascope";

const recommendBook = llm.defineCall<{ genre: string }>({
  model: "openai/gpt-4o-mini",
  template: ({ genre }) => `Recommend a ${genre} book.`,
});

const maxRetries = 3;
for (let attempt = 0; attempt < maxRetries; attempt++) {
  try {
    const response = await recommendBook({ genre: "fantasy" });
    console.log(response.text());
    break;
  } catch (e) {
    if (e instanceof llm.MirascopeError) {
      if (attempt === maxRetries - 1) {
        throw e;
      }
      console.log(`Attempt ${attempt + 1} failed, retrying...`);
    } else {
      throw e;
    }
  }
}
