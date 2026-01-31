/**
 * Tool calling loop example.
 *
 * Demonstrates a loop that continues until the model stops requesting tools.
 * Useful for complex tasks that require multiple tool calls.
 *
 * Run with: bun run example examples/tools/loop.ts
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

const sumTool = llm.defineTool({
  name: "sum_tool",
  description: "Computes the sum of a list of numbers",
  validator: z.object({
    numbers: z.array(z.number()).describe("The numbers to sum"),
  }),
  tool: ({ numbers }) => numbers.reduce((a, b) => a + b, 0),
});

const mathAssistant = llm.defineCall<{ query: string }>({
  model: "openai/gpt-4o-mini",
  tools: [sqrtTool, sumTool],
  template: ({ query }) => query,
});

let response = await mathAssistant({
  query: "What's the sum of the square roots of 137, 4242, and 6900?",
});

// Loop until no more tool calls
while (response.toolCalls.length > 0) {
  const toolOutputs = await response.executeTools();
  response = await response.resume(toolOutputs);
}

console.log(response.text());
// sqrt(137) + sqrt(4242) + sqrt(6900) ≈ 159.9015764916355
