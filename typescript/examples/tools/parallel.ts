/**
 * Parallel tool execution example.
 *
 * Demonstrates executing multiple tool calls in parallel when the model
 * requests multiple tools at once.
 *
 * Run with: bun run example examples/tools/parallel.ts
 */
import { llm } from "mirascope";
import { z } from "zod";

const sqrtTool = llm.defineTool({
  name: "sqrt_tool",
  description: "Computes the square root of a number",
  validator: z.object({
    number: z.number().describe("The number to compute the square root of"),
  }),
  tool: ({ number }) => Math.sqrt(number),
});

const mathAssistant = llm.defineCall<{ query: string }>({
  model: "openai/gpt-4o-mini",
  tools: [sqrtTool],
  template: ({ query }) => query,
});

const response = await mathAssistant({
  query: "What are the square roots of 3737, 4242, and 6464?",
});

// executeTools() handles all tool calls in parallel
const toolOutputs = await response.executeTools();

const answer = await response.resume(toolOutputs);
console.log(answer.text());
// The square roots (approximate) are:
// - sqrt(3737) ≈ 61.13
// - sqrt(4242) ≈ 65.13
// - sqrt(6464) ≈ 80.40
