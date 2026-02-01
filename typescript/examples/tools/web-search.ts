/**
 * Web search tool example.
 *
 * Demonstrates using the provider-native web search tool.
 * The search is executed server-side by the provider, not locally.
 *
 * Run with: bun run example examples/tools/web-search.ts
 */
import { llm } from "mirascope";

const weatherAssistant = llm.defineCall<{ query: string }>({
  model: "anthropic/claude-sonnet-4-5",
  tools: [new llm.WebSearchTool()],
  template: ({ query }) => query,
});

const response = await weatherAssistant({
  query: "What's the current weather in San Francisco?",
});
console.log(response.text());
// Today features intervals of clouds and sunshine with a couple of showers...
