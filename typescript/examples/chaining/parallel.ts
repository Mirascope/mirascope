/**
 * Parallel call execution example.
 *
 * Demonstrates running multiple LLM calls in parallel using Promise.all,
 * then combining their results in a final call.
 *
 * Run with: bun run example examples/chaining/parallel.ts
 */
import { llm } from "mirascope";
import { z } from "zod";

const model = "openai/gpt-4o-mini";

const chefSelector = llm.defineCall<{ ingredient: string }>({
  model,
  template: ({ ingredient }) =>
    `Identify a chef known for cooking with ${ingredient}. Return only their name.`,
});

const ingredientsIdentifier = llm.defineCall<{ ingredient: string }>()({
  model,
  format: z.array(z.string()),
  template: ({ ingredient }) =>
    `List 5 ingredients that complement ${ingredient}.`,
});

const recommend = llm.defineCall<{ chef: string; ingredients: string[] }>({
  model,
  template: ({ chef, ingredients }) =>
    `As chef ${chef}, recommend a recipe using: ${ingredients.join(", ")}`,
});

async function recipeRecommender(ingredient: string): Promise<string> {
  // Run two calls in parallel
  const [chefResponse, ingredientsResponse] = await Promise.all([
    chefSelector({ ingredient }),
    ingredientsIdentifier({ ingredient }),
  ]);

  // Combine results in a final call
  const response = await recommend({
    chef: chefResponse.text(),
    ingredients: ingredientsResponse.parse(),
  });

  return response.text();
}

const recipe = await recipeRecommender("apples");
console.log(recipe);
