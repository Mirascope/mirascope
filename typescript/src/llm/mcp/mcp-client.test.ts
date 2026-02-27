/**
 * Tests for MCPClient functionality.
 */

import { describe, expect, it, vi } from "vitest";

import type { ToolCall } from "@/llm/content/tool-call";

import { ToolExecutionError } from "@/llm/exceptions";
import { TOOL_TYPE } from "@/llm/tools/tools";

import type {
  MCPClientSession,
  MCPTool,
  MCPContentBlock,
  MCPCallToolResult,
} from "./types";

import { MCPClient, serializeMCPContent } from "./mcp-client";

// Helper to create a mock MCP session
function createMockSession(
  tools: MCPTool[] = [],
  callToolResult?: MCPCallToolResult,
): MCPClientSession {
  return {
    initialize: vi.fn().mockResolvedValue(undefined),
    listTools: vi.fn().mockResolvedValue({ tools }),
    callTool: vi
      .fn()
      .mockResolvedValue(
        callToolResult ?? { content: [{ type: "text", text: "result" }] },
      ),
  };
}

// Helper to create a mock ToolCall
function createToolCall(name: string, args: Record<string, unknown>): ToolCall {
  return {
    type: "tool_call",
    id: "test-id",
    name,
    args: JSON.stringify(args),
  };
}

describe("serializeMCPContent", () => {
  it("serializes content blocks with all fields", () => {
    const content: MCPContentBlock[] = [
      {
        type: "text",
        text: "Hello",
        data: "base64data",
        mimeType: "text/plain",
        annotations: { key: "value" },
        meta: { info: "data" },
      },
    ];

    const result = serializeMCPContent(content);

    expect(result).toEqual([
      {
        type: "text",
        text: "Hello",
        data: "base64data",
        mimeType: "text/plain",
        annotations: { key: "value" },
        meta: { info: "data" },
      },
    ]);
  });

  it("serializes content blocks with missing optional fields as null", () => {
    const content: MCPContentBlock[] = [{ type: "text" }];

    const result = serializeMCPContent(content);

    expect(result).toEqual([
      {
        type: "text",
        text: null,
        data: null,
        mimeType: null,
        annotations: null,
        meta: null,
      },
    ]);
  });

  it("serializes multiple content blocks", () => {
    const content: MCPContentBlock[] = [
      { type: "text", text: "First" },
      { type: "image", data: "imagedata", mimeType: "image/png" },
    ];

    const result = serializeMCPContent(content);

    expect(result).toHaveLength(2);
    expect(result[0]?.type).toBe("text");
    expect(result[1]?.type).toBe("image");
  });
});

describe("MCPClient", () => {
  describe("constructor and session property", () => {
    it("stores and exposes the session", () => {
      const session = createMockSession();
      const client = new MCPClient(session);

      expect(client.session).toBe(session);
    });
  });

  describe("listTools", () => {
    it("returns empty array when server has no tools", async () => {
      const session = createMockSession([]);
      const client = new MCPClient(session);

      const tools = await client.listTools();

      expect(tools).toHaveLength(0);
      expect(session.listTools).toHaveBeenCalled();
    });

    it("converts MCP tools to BaseTool objects", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "greet",
          description: "Greet a user",
          inputSchema: {
            type: "object",
            properties: { name: { type: "string" } },
            required: ["name"],
          },
        },
      ];
      const session = createMockSession(mcpTools);
      const client = new MCPClient(session);

      const tools = await client.listTools();

      expect(tools).toHaveLength(1);
      expect(tools[0]?.name).toBe("greet");
      expect(tools[0]?.description).toBe("Greet a user");
      expect(tools[0]?.__toolType).toBe(TOOL_TYPE);
    });

    it("uses tool name as description when description is missing", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "my_tool",
          inputSchema: { properties: {} },
        },
      ];
      const session = createMockSession(mcpTools);
      const client = new MCPClient(session);

      const tools = await client.listTools();

      expect(tools[0]?.description).toBe("my_tool");
    });

    it("converts inputSchema to ToolParameterSchema", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "test",
          description: "Test tool",
          inputSchema: {
            type: "object",
            properties: {
              city: { type: "string", description: "City name" },
              count: { type: "number" },
            },
            required: ["city"],
            additionalProperties: true,
          },
        },
      ];
      const session = createMockSession(mcpTools);
      const client = new MCPClient(session);

      const tools = await client.listTools();
      const params = tools[0]?.parameters;

      expect(params?.type).toBe("object");
      expect(params?.properties.city).toEqual({
        type: "string",
        description: "City name",
      });
      expect(params?.properties.count).toEqual({ type: "number" });
      expect(params?.required).toEqual(["city"]);
      expect(params?.additionalProperties).toBe(false); // Always false in Mirascope
    });

    it("preserves $defs in schema for complex nested types", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "process",
          description: "Process data",
          inputSchema: {
            type: "object",
            properties: {
              data: { $ref: "#/$defs/DataType" },
            },
            required: ["data"],
            $defs: {
              DataType: {
                type: "object",
                properties: {
                  value: { type: "string" },
                },
              },
            },
          },
        },
      ];
      const session = createMockSession(mcpTools);
      const client = new MCPClient(session);

      const tools = await client.listTools();
      const params = tools[0]?.parameters;

      expect(params?.$defs).toBeDefined();
      expect(params?.$defs?.DataType).toEqual({
        type: "object",
        properties: {
          value: { type: "string" },
        },
      });
    });

    it("handles empty inputSchema", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "no_args",
          description: "Tool with no arguments",
          inputSchema: {},
        },
      ];
      const session = createMockSession(mcpTools);
      const client = new MCPClient(session);

      const tools = await client.listTools();
      const params = tools[0]?.parameters;

      expect(params?.properties).toEqual({});
      expect(params?.required).toEqual([]);
    });

    it("sets strict to false and validator to undefined", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "test",
          description: "Test",
          inputSchema: { properties: {} },
        },
      ];
      const session = createMockSession(mcpTools);
      const client = new MCPClient(session);

      const tools = await client.listTools();

      expect(tools[0]?.strict).toBe(false);
      expect(tools[0]?.validator).toBeUndefined();
    });
  });

  describe("tool execution", () => {
    it("executes tool and returns successful ToolOutput", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "greet",
          description: "Greet",
          inputSchema: { properties: { name: { type: "string" } } },
        },
      ];
      const callResult: MCPCallToolResult = {
        content: [{ type: "text", text: "Hello, Alice!" }],
      };
      const session = createMockSession(mcpTools, callResult);
      const client = new MCPClient(session);

      const tools = await client.listTools();
      const toolCall = createToolCall("greet", { name: "Alice" });
      const output = await tools[0]!.execute(toolCall);

      expect(output.type).toBe("tool_output");
      expect(output.id).toBe("test-id");
      expect(output.name).toBe("greet");
      expect(output.error).toBeNull();
      expect(output.result).toEqual([
        {
          type: "text",
          text: "Hello, Alice!",
          data: null,
          mimeType: null,
          annotations: null,
          meta: null,
        },
      ]);
      expect(session.callTool).toHaveBeenCalledWith("greet", { name: "Alice" });
    });

    it("returns error ToolOutput when session.callTool throws", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "failing_tool",
          description: "Fails",
          inputSchema: { properties: {} },
        },
      ];
      const session = createMockSession(mcpTools);
      (session.callTool as ReturnType<typeof vi.fn>).mockRejectedValue(
        new Error("Connection closed"),
      );
      const client = new MCPClient(session);

      const tools = await client.listTools();
      const toolCall = createToolCall("failing_tool", {});
      const output = await tools[0]!.execute(toolCall);

      expect(output.error).toBeInstanceOf(ToolExecutionError);
      expect(output.result).toBe("Connection closed");
    });

    it("returns error ToolOutput when JSON.parse fails", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "test",
          description: "Test",
          inputSchema: { properties: {} },
        },
      ];
      const session = createMockSession(mcpTools);
      const client = new MCPClient(session);

      const tools = await client.listTools();
      const badToolCall: ToolCall = {
        type: "tool_call",
        id: "bad-id",
        name: "test",
        args: "not valid json",
      };
      const output = await tools[0]!.execute(badToolCall);

      expect(output.error).toBeInstanceOf(ToolExecutionError);
      expect(output.result).toContain("Unexpected token");
    });

    it("handles non-Error thrown values", async () => {
      const mcpTools: MCPTool[] = [
        {
          name: "test",
          description: "Test",
          inputSchema: { properties: {} },
        },
      ];
      const session = createMockSession(mcpTools);
      (session.callTool as ReturnType<typeof vi.fn>).mockRejectedValue(
        "string error",
      );
      const client = new MCPClient(session);

      const tools = await client.listTools();
      const toolCall = createToolCall("test", {});
      const output = await tools[0]!.execute(toolCall);

      expect(output.error).toBeInstanceOf(ToolExecutionError);
      expect(output.result).toBe("string error");
    });
  });
});
