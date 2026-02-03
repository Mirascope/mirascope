/**
 * Combined MCP and local tools example.
 *
 * Demonstrates combining MCP tools with locally defined tools
 * in a single defineCall.
 *
 * Run with: bun run example examples/mcp/combined-tools.ts
 */
import { spawn } from "child_process";
import { llm } from "mirascope";

/**
 * Arguments for the codebase search tool.
 */
type SearchArgs = {
  /** The pattern to search for in the codebase */
  pattern: string;
};

const searchCodebase = llm.defineTool<SearchArgs>({
  name: "search_codebase",
  description: "Search the local codebase for a pattern using ripgrep",
  tool: async ({ pattern }) => {
    return new Promise<string>((resolve) => {
      const proc = spawn("rg", ["--max-count=5", pattern, "./"]);
      let output = "";
      proc.stdout.on("data", (data) => {
        output += data.toString();
      });
      proc.on("close", () => {
        resolve(output || "No matches found.");
      });
    });
  },
});

await llm.mcp.using(
  llm.mcp.streamableHttpClient("https://gofastmcp.com/mcp"),
  async (client) => {
    const mcpTools = await client.listTools();
    const allTools = [searchCodebase, ...mcpTools];

    const assistant = llm.defineCall<{ query: string }>({
      model: "openai/gpt-4o-mini",
      tools: allTools,
      template: ({ query }) => query,
    });

    let response = await assistant({
      query:
        "How does FastMCP handle tool registration? " +
        "Search the FastMCP docs, then check our codebase for similar patterns.",
    });

    while (response.toolCalls.length > 0) {
      console.log(
        "Tool calls:",
        response.toolCalls.map((tc) => tc.name).join(", "),
      );
      const toolOutputs = await response.executeTools();
      response = await response.resume(toolOutputs);
    }

    console.log(response.text());
  },
);
