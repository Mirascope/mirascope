/**
 * Fallback to alternative models example.
 *
 * Demonstrates falling back to alternative models when the primary model fails.
 *
 * Run with: bun run example examples/reliability/fallback.ts
 */
import type { ModelId, Response } from "mirascope";

import { llm } from "mirascope";

const models: ModelId[] = [
  "openai/gpt-4o-mini",
  "anthropic/claude-haiku-4-5",
  "google/gemini-2.0-flash",
];

const recommendBook = llm.defineCall<{ genre: string }>({
  model: models[0]!,
  template: ({ genre }) => `Recommend a ${genre} book.`,
});

async function withFallbacks(
  genre: string,
  maxRetries = 3,
): Promise<Response<string>> {
  const errors: llm.MirascopeError[] = [];

  for (const modelId of models) {
    for (let attempt = 0; attempt < maxRetries; attempt++) {
      try {
        // Use withModel to override the default model
        return await llm.withModel(modelId, async () => {
          return recommendBook({ genre });
        });
      } catch (e) {
        if (e instanceof llm.MirascopeError) {
          errors.push(e);
          if (attempt === maxRetries - 1) {
            console.log(`Model ${modelId} failed after ${maxRetries} attempts`);
            break; // Try next model
          }
        } else {
          throw e;
        }
      }
    }
  }

  // Re-raise last error
  throw errors[errors.length - 1];
}

const response = await withFallbacks("fantasy");
console.log(response.text());
