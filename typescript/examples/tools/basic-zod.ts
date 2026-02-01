/**
 * Zod-native tool usage example.
 *
 * Demonstrates defining tools using Zod schemas for validation and type inference.
 * This pattern works WITHOUT the compile-time transformer - perfect for runtime-only usage.
 *
 * Run with: bun run example examples/tools/basic-zod.ts
 */
import { llm } from "mirascope";
import { z } from "zod";

// Define tool with Zod schema - no transformer needed!
// Use .describe() on each field to provide descriptions
const sqrtTool = llm.defineTool({
  name: "sqrt_tool",
  description: "Computes the square root of a number",
  validator: z.object({
    number: z.number().describe("The number to compute the square root of"),
  }),
  // TypeScript automatically infers { number: number } from the validator
  tool: ({ number }) => Math.sqrt(number),
});

// More complex example with multiple fields and validation
const weatherTool = llm.defineTool({
  name: "get_weather",
  description: "Get the current weather for a location",
  validator: z.object({
    city: z.string().describe("The city to get weather for"),
    units: z
      .enum(["celsius", "fahrenheit"])
      .default("celsius")
      .describe("Temperature units"),
  }),
  tool: ({ city, units }) => ({
    city,
    temperature: units === "celsius" ? 22 : 72,
    units,
    conditions: "sunny",
  }),
});

const assistant = llm.defineCall<{ query: string }>({
  model: "openai/gpt-4o-mini",
  tools: [sqrtTool, weatherTool],
  template: ({ query }) => query,
});

// Example 1: Math query
console.log("=== Math Query ===");
let response = await assistant({
  query: "What's the square root of 4242?",
});

let toolOutputs = await response.executeTools();
let answer = await response.resume(toolOutputs);
console.log(answer.text());

// Example 2: Weather query
console.log("\n=== Weather Query ===");
response = await assistant({
  query: "What's the weather in Tokyo?",
});

toolOutputs = await response.executeTools();
answer = await response.resume(toolOutputs);
console.log(answer.text());
