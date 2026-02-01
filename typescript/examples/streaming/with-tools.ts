/**
 * Streaming with tools example.
 *
 * Demonstrates streaming responses while using tools.
 *
 * Run with: bun run example examples/streaming/with-tools.ts
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

let response = await mathAssistant.stream({
  query: "What's the square root of 4242?",
});

// Loop to ensure we execute all tool calls
while (true) {
  // Stream the response
  for await (const text of response.textStream()) {
    process.stdout.write(text);
  }
  console.log();

  // Check if there are tool calls after consuming the stream
  if (response.toolCalls.length === 0) {
    break;
  }

  // Execute tools and resume
  const toolOutputs = await response.executeTools();
  response = await response.resume(toolOutputs);
}
