/**
 * Token usage example.
 *
 * Demonstrates accessing token usage statistics from a response.
 *
 * Run with: bun run example examples/responses/usage.ts
 */
import { llm } from "mirascope";

const model = llm.useModel("openai/gpt-4o");
const response = await model.call("Write a haiku about programming.");

if (response.usage) {
  console.log(`Input tokens: ${response.usage.inputTokens}`);
  console.log(`Output tokens: ${response.usage.outputTokens}`);
  console.log(`Total tokens: ${llm.totalTokens(response.usage)}`);
}
