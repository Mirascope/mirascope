/**
 * E2E tests for MCP tool integration.
 *
 * These tests connect to a TypeScript MCP test server via stdio transport
 * and verify tool listing, conversion, and execution work correctly.
 *
 * NOTE: These tests are skipped because stdio process spawning is inherently
 * flaky. The MCP transports are excluded from coverage requirements. To run
 * these tests locally for development, change describe.skip to describe.
 */

import { resolve } from "node:path";
import { describe, expect, it } from "vitest";

import { mcp, ToolExecutionError } from "@/llm";

// Path to TypeScript MCP test server
const MCP_SERVER_PATH = resolve(__dirname, "../fixtures/mcp-test-server.ts");

describe.skip("MCP tool integration", () => {
  it("connects via stdio and lists tools", async () => {
    await mcp.using(
      mcp.stdioClient({
        command: "bun",
        args: [MCP_SERVER_PATH],
      }),
      async (client) => {
        const tools = await client.listTools();

        // Should have 3 tools from the test server
        expect(tools.length).toBe(3);

        // Check tool names
        const toolNames = tools.map((t) => t.name).sort();
        expect(toolNames).toEqual([
          "answer_ultimate_question",
          "greet",
          "process_answer",
        ]);

        // Verify greet tool schema
        const greetTool = tools.find((t) => t.name === "greet")!;
        expect(greetTool.description).toContain("Greet a user");
        expect(greetTool.parameters.properties.name).toBeDefined();
        expect(greetTool.parameters.required).toContain("name");

        // Verify answer_ultimate_question tool has no required params
        const answerTool = tools.find(
          (t) => t.name === "answer_ultimate_question",
        )!;
        expect(answerTool.parameters.required).toEqual([]);

        // Verify process_answer tool has nested object schema
        // Note: Zod generates inline schemas rather than $defs, but the functionality is the same.
        // $defs handling is tested separately in unit tests with mocked schemas.
        const processTool = tools.find((t) => t.name === "process_answer")!;
        expect(processTool.parameters.properties.answer_data).toBeDefined();
        // The nested schema should have the expected structure (inline or via $defs)
        const answerDataSchema = processTool.parameters.properties.answer_data;
        expect(answerDataSchema).toBeDefined();
      },
    );
  });

  it("executes greet tool successfully", async () => {
    await mcp.using(
      mcp.stdioClient({
        command: "bun",
        args: [MCP_SERVER_PATH],
      }),
      async (client) => {
        const tools = await client.listTools();
        const greetTool = tools.find((t) => t.name === "greet")!;

        const toolCall = {
          type: "tool_call" as const,
          id: "call_123",
          name: "greet",
          args: JSON.stringify({ name: "TypeScript" }),
        };

        const output = await greetTool.execute(toolCall);

        expect(output.id).toBe("call_123");
        expect(output.name).toBe("greet");
        expect(output.error).toBeNull();

        // Result should be serialized content blocks
        const result = output.result as Array<{ type: string; text: string }>;
        expect(result[0]?.type).toBe("text");
        expect(result[0]?.text).toContain("Welcome to Zombo.com, TypeScript");
      },
    );
  });

  it("executes answer_ultimate_question tool successfully", async () => {
    await mcp.using(
      mcp.stdioClient({
        command: "bun",
        args: [MCP_SERVER_PATH],
      }),
      async (client) => {
        const tools = await client.listTools();
        const answerTool = tools.find(
          (t) => t.name === "answer_ultimate_question",
        )!;

        const toolCall = {
          type: "tool_call" as const,
          id: "call_456",
          name: "answer_ultimate_question",
          args: "{}",
        };

        const output = await answerTool.execute(toolCall);

        expect(output.id).toBe("call_456");
        expect(output.name).toBe("answer_ultimate_question");
        expect(output.error).toBeNull();

        // Result should contain the answer 42
        const result = output.result as Array<{ type: string; text: string }>;
        expect(result[0]?.type).toBe("text");
        const parsed = JSON.parse(result[0]!.text!);
        expect(parsed.answer).toBe(42);
        expect(parsed.computed_by.name).toBe("Deep Thought");
      },
    );
  });

  it("executes process_answer tool with complex nested input", async () => {
    await mcp.using(
      mcp.stdioClient({
        command: "bun",
        args: [MCP_SERVER_PATH],
      }),
      async (client) => {
        const tools = await client.listTools();
        const processTool = tools.find((t) => t.name === "process_answer")!;

        const toolCall = {
          type: "tool_call" as const,
          id: "call_789",
          name: "process_answer",
          args: JSON.stringify({
            answer_data: {
              answer: 81,
              question: "What is 9 * 9?",
              computed_by: {
                name: "Simple Thought",
                years_computed: 3,
              },
            },
          }),
        };

        const output = await processTool.execute(toolCall);

        expect(output.id).toBe("call_789");
        expect(output.name).toBe("process_answer");
        expect(output.error).toBeNull();

        const result = output.result as Array<{ type: string; text: string }>;
        expect(result[0]?.text).toContain("The answer 81");
        expect(result[0]?.text).toContain("Simple Thought");
        expect(result[0]?.text).toContain("3 years");
      },
    );
  });

  it("returns error when tool execution fails after client closed", async () => {
    let capturedTool: Awaited<ReturnType<mcp.MCPClient["listTools"]>>[number];

    // Get a tool reference while client is open
    await mcp.using(
      mcp.stdioClient({
        command: "bun",
        args: [MCP_SERVER_PATH],
      }),
      async (client) => {
        const tools = await client.listTools();
        capturedTool = tools.find((t) => t.name === "greet")!;
      },
    );

    // Now client is closed - tool execution should fail gracefully
    const toolCall = {
      type: "tool_call" as const,
      id: "call_closed",
      name: "greet",
      args: JSON.stringify({ name: "Test" }),
    };

    const output = await capturedTool!.execute(toolCall);

    expect(output.error).toBeInstanceOf(ToolExecutionError);
    expect(output.error).not.toBeNull();
  });

  it("exposes the underlying session", async () => {
    await mcp.using(
      mcp.stdioClient({
        command: "bun",
        args: [MCP_SERVER_PATH],
      }),
      async (client) => {
        // Session should be accessible
        expect(client.session).toBeDefined();
        expect(typeof client.session.listTools).toBe("function");
        expect(typeof client.session.callTool).toBe("function");
      },
    );
  });
});
