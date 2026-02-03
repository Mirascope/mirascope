/**
 * MCP tools with streaming and thinking example.
 *
 * Demonstrates using MCP tools with streaming responses and
 * model thinking enabled.
 *
 * Run with: bun run example examples/mcp/with-thinking.ts
 */
import { llm } from "mirascope";

await llm.mcp.using(
  llm.mcp.streamableHttpClient("https://gofastmcp.com/mcp"),
  async (client) => {
    const tools = await client.listTools();

    const learnMcp = llm.defineCall({
      model: "google/gemini-2.0-flash",
      thinking: { level: "medium", includeThoughts: true },
      tools,
      template: () =>
        "Use the tools to learn about FastMCP, and write a report on the library.",
    });

    let response = await learnMcp.stream();

    while (true) {
      // Stream the response
      for await (const chunk of response.chunkStream()) {
        if (chunk.type === "thought_chunk") {
          process.stdout.write(`[thinking] ${chunk.delta}`);
        } else if (chunk.type === "text_chunk") {
          process.stdout.write(chunk.delta);
        } else if (chunk.type === "tool_call_start_chunk") {
          console.log(`\n[tool call] ${chunk.name}`);
        }
      }
      console.log();

      if (response.toolCalls.length > 0) {
        const toolOutputs = await response.executeTools();
        response = await response.resume(toolOutputs);
      } else {
        break;
      }
    }
  },
);
