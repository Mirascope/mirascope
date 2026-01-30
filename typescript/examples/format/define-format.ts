/**
 * Example using defineFormat for explicit mode control.
 *
 * Shows how to use defineFormat() to specify the formatting mode
 * (tool, json, or strict) when you need explicit control.
 *
 * Run with: bun run example examples/format/define-format.ts
 */
import { z } from 'zod';
import { llm } from 'mirascope';

// Define a Zod schema for recipe information
const RecipeSchema = z.object({
  name: z.string().describe('The name of the recipe'),
  servings: z.number().describe('Number of servings'),
  prepTime: z.string().describe('Preparation time'),
  cookTime: z.string().describe('Cooking time'),
  ingredients: z.array(z.string()).describe('List of ingredients'),
  instructions: z.array(z.string()).describe('Step-by-step instructions'),
});

type Recipe = z.infer<typeof RecipeSchema>;

// Create the call using the explicit format
// Use defineCall<VarsType>()({...}) to specify variables type while inferring format type.
const getRecipe = llm.defineCall<{ dish: string }>()({
  model: 'openai/gpt-4o-mini',
  maxTokens: 2048,
  format: llm.defineFormat<Recipe>({
    mode: 'json',
    validator: RecipeSchema,
  }),
  template: ({ dish }) =>
    `Provide a detailed recipe for making ${dish}. Include all ingredients and step-by-step instructions.`,
});

const response = await getRecipe({ dish: 'chocolate chip cookies' });
// parse() returns the parsed object (fully typed)
const recipe = response.parse();

console.log('Recipe:');
console.log('=======\n');
console.log(`Name: ${recipe.name}`);
console.log(`Servings: ${recipe.servings}`);
console.log(`Prep Time: ${recipe.prepTime}`);
console.log(`Cook Time: ${recipe.cookTime}`);

console.log('\nIngredients:');
for (const ingredient of recipe.ingredients) {
  console.log(`  - ${ingredient}`);
}

console.log('\nInstructions:');
for (let i = 0; i < recipe.instructions.length; i++) {
  console.log(`  ${i + 1}. ${recipe.instructions[i]}`);
}
