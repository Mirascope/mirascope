/**
 * Basic MCP tool usage example.
 *
 * Demonstrates connecting to an MCP server, listing tools, and using them
 * with defineCall to get responses from the LLM.
 *
 * IMPORTANT: All tool usage must happen inside the `using()` callback
 * to keep the MCP connection open for tool execution.
 *
 * Run with: bun run example examples/mcp/basic-call.ts
 */
import { llm } from "mirascope";

await llm.mcp.using(
  llm.mcp.streamableHttpClient("https://gofastmcp.com/mcp"),
  async (client) => {
    const tools = await client.listTools();

    const assistant = llm.defineCall<{ query: string }>({
      model: "openai/gpt-4o-mini",
      tools,
      template: ({ query }) => query,
    });

    let response = await assistant({
      query: "Give me a getting started primer on FastMCP.",
    });

    while (response.toolCalls.length > 0) {
      const toolOutputs = await response.executeTools();
      response = await response.resume(toolOutputs);
    }

    console.log(response.text());
  },
);
