import { describe, expect, it, vi } from "vitest";

import type { ToolCall } from "@/llm/content/tool-call";

import { createContext, type Context } from "@/llm/context";
import { ToolNotFoundError } from "@/llm/exceptions";
import { defineTool, defineContextTool } from "@/llm/tools/define-tool";
import { ProviderTool } from "@/llm/tools/provider-tool";
import { FORMAT_TOOL_NAME } from "@/llm/tools/tool-schema";
import {
  Toolkit,
  ContextToolkit,
  createToolkit,
  createContextToolkit,
  normalizeTools,
  normalizeContextTools,
} from "@/llm/tools/toolkit";
import { WebSearchTool } from "@/llm/tools/web-search-tool";

// Helper to create a mock ToolCall
function createToolCall(name: string, args: Record<string, unknown>): ToolCall {
  return {
    type: "tool_call",
    id: `id-${name}`,
    name,
    args: JSON.stringify(args),
  };
}

describe("Toolkit", () => {
  const getWeather = defineTool<{ city: string }>({
    name: "get_weather",
    description: "Get weather",
    tool: ({ city }) => ({ temp: 72, city }),
  });

  const searchWeb = defineTool<{ query: string }>({
    name: "search_web",
    description: "Search the web",
    tool: ({ query }) => [`Result for: ${query}`],
  });

  it("creates toolkit with tools", () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    expect(toolkit.tools).toHaveLength(2);
    expect(toolkit.toolMap.has("get_weather")).toBe(true);
    expect(toolkit.toolMap.has("search_web")).toBe(true);
  });

  it("returns tools array", () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    const tools = toolkit.tools;
    expect(tools).toContain(getWeather);
    expect(tools).toContain(searchWeb);
  });

  it("returns schemas array", () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    const schemas = toolkit.schemas;
    expect(schemas).toHaveLength(2);
    expect(schemas[0]?.name).toBe("get_weather");
    expect(schemas[1]?.name).toBe("search_web");
  });

  it("gets tool by tool call", () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);

    expect(toolkit.get(createToolCall("get_weather", {}))).toBe(getWeather);
    expect(toolkit.get(createToolCall("search_web", {}))).toBe(searchWeb);
    expect(toolkit.get(createToolCall("nonexistent", {}))).toBeUndefined();
  });

  it("executes tool call", async () => {
    const toolkit = new Toolkit([getWeather, searchWeb]);
    const toolCall = createToolCall("get_weather", { city: "NYC" });

    const output = await toolkit.execute(toolCall);

    expect(output.result).toEqual({ temp: 72, city: "NYC" });
    expect(output.error).toBeNull();
  });

  it("returns error for unknown tool", async () => {
    const toolkit = new Toolkit([getWeather]);
    const toolCall = createToolCall("unknown_tool", {});

    const output = await toolkit.execute(toolCall);

    expect(output.error).toBeInstanceOf(ToolNotFoundError);
    expect((output.error as ToolNotFoundError).toolName).toBe("unknown_tool");
  });

  it("handles empty toolkit", () => {
    const toolkit = new Toolkit([]);

    expect(toolkit.tools).toHaveLength(0);
    expect(toolkit.schemas).toHaveLength(0);
  });
});

describe("ContextToolkit", () => {
  interface TestDeps {
    db: { search: (q: string) => string[] };
    api: { fetch: (url: string) => Promise<string> };
  }

  const searchDb = defineContextTool<{ query: string }, TestDeps>({
    name: "search_db",
    description: "Search database",
    tool: (ctx, { query }) => ctx.deps.db.search(query),
  });

  const fetchUrl = defineContextTool<{ url: string }, TestDeps>({
    name: "fetch_url",
    description: "Fetch URL",
    tool: async (ctx, { url }) => ctx.deps.api.fetch(url),
  });

  const createMockContext = (): Context<TestDeps> =>
    createContext<TestDeps>({
      db: { search: vi.fn((q: string) => [`db: ${q}`]) },
      api: {
        fetch: vi.fn((url: string) => Promise.resolve(`fetched: ${url}`)),
      },
    });

  it("creates context toolkit with tools", () => {
    const toolkit = new ContextToolkit<TestDeps>([searchDb, fetchUrl]);

    expect(toolkit.tools).toHaveLength(2);
    expect(toolkit.toolMap.has("search_db")).toBe(true);
    expect(toolkit.toolMap.has("fetch_url")).toBe(true);
  });

  it("returns schemas array", () => {
    const toolkit = new ContextToolkit<TestDeps>([searchDb, fetchUrl]);

    const schemas = toolkit.schemas;
    expect(schemas).toHaveLength(2);
    expect(schemas.map((s) => s.name)).toContain("search_db");
    expect(schemas.map((s) => s.name)).toContain("fetch_url");
  });

  it("gets tool by tool call", () => {
    const toolkit = new ContextToolkit<TestDeps>([searchDb]);

    expect(toolkit.get(createToolCall("search_db", {}))).toBe(searchDb);
    expect(toolkit.get(createToolCall("nonexistent", {}))).toBeUndefined();
  });

  it("executes tool call with context", async () => {
    const ctx = createMockContext();
    const toolkit = new ContextToolkit<TestDeps>([searchDb]);
    const toolCall = createToolCall("search_db", { query: "test" });

    const output = await toolkit.execute(ctx, toolCall);

    expect(output.result).toEqual(["db: test"]);
    expect(output.error).toBeNull();
    expect(ctx.deps.db.search).toHaveBeenCalledWith("test");
  });

  it("returns error for unknown tool", async () => {
    const ctx = createMockContext();
    const toolkit = new ContextToolkit<TestDeps>([searchDb]);
    const toolCall = createToolCall("unknown", {});

    const output = await toolkit.execute(ctx, toolCall);

    expect(output.error).toBeInstanceOf(ToolNotFoundError);
  });

  it("executes multiple tool calls in parallel", async () => {
    const ctx = createMockContext();
    const toolkit = new ContextToolkit<TestDeps>([searchDb, fetchUrl]);

    const toolCalls = [
      createToolCall("search_db", { query: "hello" }),
      createToolCall("fetch_url", { url: "https://example.com" }),
    ];

    const outputs = await toolkit.executeAll(ctx, toolCalls);

    expect(outputs).toHaveLength(2);
    expect(outputs[0]?.result).toEqual(["db: hello"]);
    expect(outputs[1]?.result).toBe("fetched: https://example.com");
  });
});

describe("createToolkit", () => {
  it("creates toolkit from tools array", () => {
    const tool = defineTool<{ x: string }>({
      name: "test",
      description: "Test",
      tool: () => null,
    });

    const toolkit = createToolkit([tool]);

    expect(toolkit).toBeInstanceOf(Toolkit);
    expect(toolkit.toolMap.has("test")).toBe(true);
  });
});

describe("createContextToolkit", () => {
  it("creates context toolkit from tools array", () => {
    interface Deps {
      value: number;
    }
    const tool = defineContextTool<{ x: string }, Deps>({
      name: "test",
      description: "Test",
      tool: (ctx) => ctx.deps.value,
    });

    const toolkit = createContextToolkit<Deps>([tool]);

    expect(toolkit).toBeInstanceOf(ContextToolkit);
    expect(toolkit.toolMap.has("test")).toBe(true);
  });
});

describe("ContextToolkit with mixed tools", () => {
  interface TestDeps {
    multiplier: number;
  }

  // Regular tool - no context needed
  const addNumbers = defineTool<{ a: number; b: number }>({
    name: "add_numbers",
    description: "Add two numbers",
    tool: ({ a, b }) => a + b,
  });

  // Context tool - needs context for multiplier
  const multiplyWithContext = defineContextTool<{ value: number }, TestDeps>({
    name: "multiply_with_context",
    description: "Multiply by context multiplier",
    tool: (ctx, { value }) => value * ctx.deps.multiplier,
  });

  const createMockContext = (multiplier: number): Context<TestDeps> =>
    createContext<TestDeps>({ multiplier });

  it("accepts both regular and context tools", () => {
    // This is the key Python-like pattern: ContextToolkit accepts Tool | ContextTool
    const toolkit = new ContextToolkit<TestDeps>([
      addNumbers,
      multiplyWithContext,
    ]);

    expect(toolkit.tools).toHaveLength(2);
    expect(toolkit.toolMap.has("add_numbers")).toBe(true);
    expect(toolkit.toolMap.has("multiply_with_context")).toBe(true);
  });

  it("executes regular tool without passing context to it", async () => {
    const ctx = createMockContext(10);
    const toolkit = new ContextToolkit<TestDeps>([addNumbers]);
    const toolCall = createToolCall("add_numbers", { a: 5, b: 3 });

    const output = await toolkit.execute(ctx, toolCall);

    // Regular tool should work - context is NOT passed to it
    expect(output.result).toBe(8);
    expect(output.error).toBeNull();
  });

  it("executes context tool with context", async () => {
    const ctx = createMockContext(10);
    const toolkit = new ContextToolkit<TestDeps>([multiplyWithContext]);
    const toolCall = createToolCall("multiply_with_context", { value: 5 });

    const output = await toolkit.execute(ctx, toolCall);

    // Context tool should receive context
    expect(output.result).toBe(50); // 5 * 10
    expect(output.error).toBeNull();
  });

  it("polymorphically dispatches mixed tools correctly", async () => {
    const ctx = createMockContext(3);
    const toolkit = new ContextToolkit<TestDeps>([
      addNumbers,
      multiplyWithContext,
    ]);

    // Execute regular tool
    const addCall = createToolCall("add_numbers", { a: 10, b: 20 });
    const addOutput = await toolkit.execute(ctx, addCall);
    expect(addOutput.result).toBe(30);

    // Execute context tool
    const multiplyCall = createToolCall("multiply_with_context", { value: 7 });
    const multiplyOutput = await toolkit.execute(ctx, multiplyCall);
    expect(multiplyOutput.result).toBe(21); // 7 * 3
  });

  it("executeAll works with mixed tools", async () => {
    const ctx = createMockContext(2);
    const toolkit = new ContextToolkit<TestDeps>([
      addNumbers,
      multiplyWithContext,
    ]);

    const toolCalls = [
      createToolCall("add_numbers", { a: 1, b: 2 }),
      createToolCall("multiply_with_context", { value: 10 }),
    ];

    const outputs = await toolkit.executeAll(ctx, toolCalls);

    expect(outputs).toHaveLength(2);
    expect(outputs[0]?.result).toBe(3); // 1 + 2
    expect(outputs[1]?.result).toBe(20); // 10 * 2
  });

  it("returns schemas for mixed tools", () => {
    const toolkit = new ContextToolkit<TestDeps>([
      addNumbers,
      multiplyWithContext,
    ]);

    const schemas = toolkit.schemas;
    expect(schemas).toHaveLength(2);
    expect(schemas.map((s) => s.name)).toContain("add_numbers");
    expect(schemas.map((s) => s.name)).toContain("multiply_with_context");
  });
});

describe("FORMAT_TOOL_NAME", () => {
  it("has the expected value", () => {
    expect(FORMAT_TOOL_NAME).toBe("__mirascope_formatted_output_tool__");
  });
});

describe("Duplicate name validation", () => {
  it("Toolkit throws on duplicate tool names", () => {
    const tool1 = defineTool<{ x: string }>({
      name: "duplicate_name",
      description: "First tool",
      tool: () => "first",
    });
    const tool2 = defineTool<{ x: string }>({
      name: "duplicate_name",
      description: "Second tool",
      tool: () => "second",
    });

    expect(() => new Toolkit([tool1, tool2])).toThrow(
      "Multiple tools with name: duplicate_name",
    );
  });

  it("ContextToolkit throws on duplicate tool names", () => {
    interface Deps {
      value: number;
    }
    const tool1 = defineContextTool<{ x: string }, Deps>({
      name: "duplicate_name",
      description: "First tool",
      tool: () => "first",
    });
    const tool2 = defineContextTool<{ x: string }, Deps>({
      name: "duplicate_name",
      description: "Second tool",
      tool: () => "second",
    });

    expect(() => new ContextToolkit<Deps>([tool1, tool2])).toThrow(
      "Multiple tools with name: duplicate_name",
    );
  });
});

describe("Toolkit with null/undefined", () => {
  it("accepts null and creates empty toolkit", () => {
    const toolkit = new Toolkit(null);

    expect(toolkit.tools).toHaveLength(0);
    expect(toolkit.schemas).toHaveLength(0);
  });

  it("accepts undefined and creates empty toolkit", () => {
    const toolkit = new Toolkit(undefined);

    expect(toolkit.tools).toHaveLength(0);
    expect(toolkit.schemas).toHaveLength(0);
  });
});

describe("ContextToolkit with null/undefined", () => {
  it("accepts null and creates empty toolkit", () => {
    const toolkit = new ContextToolkit(null);

    expect(toolkit.tools).toHaveLength(0);
    expect(toolkit.schemas).toHaveLength(0);
  });

  it("accepts undefined and creates empty toolkit", () => {
    const toolkit = new ContextToolkit(undefined);

    expect(toolkit.tools).toHaveLength(0);
    expect(toolkit.schemas).toHaveLength(0);
  });
});

describe("normalizeTools", () => {
  const tool = defineTool<{ x: string }>({
    name: "test_tool",
    description: "Test",
    tool: () => "result",
  });

  it("returns empty toolkit for null", () => {
    const toolkit = normalizeTools(null);

    expect(toolkit).toBeInstanceOf(Toolkit);
    expect(toolkit.tools).toHaveLength(0);
  });

  it("returns empty toolkit for undefined", () => {
    const toolkit = normalizeTools(undefined);

    expect(toolkit).toBeInstanceOf(Toolkit);
    expect(toolkit.tools).toHaveLength(0);
  });

  it("passes through existing Toolkit", () => {
    const original = new Toolkit([tool]);
    const result = normalizeTools(original);

    expect(result).toBe(original); // Same reference
    expect(result.tools).toHaveLength(1);
  });

  it("wraps array in new Toolkit", () => {
    const result = normalizeTools([tool]);

    expect(result).toBeInstanceOf(Toolkit);
    expect(result.tools).toHaveLength(1);
    expect(result.toolMap.has("test_tool")).toBe(true);
  });
});

describe("normalizeContextTools", () => {
  interface TestDeps {
    value: number;
  }

  const tool = defineContextTool<{ x: string }, TestDeps>({
    name: "test_context_tool",
    description: "Test",
    tool: (ctx) => ctx.deps.value,
  });

  it("returns empty ContextToolkit for null", () => {
    const toolkit = normalizeContextTools<TestDeps>(null);

    expect(toolkit).toBeInstanceOf(ContextToolkit);
    expect(toolkit.tools).toHaveLength(0);
  });

  it("returns empty ContextToolkit for undefined", () => {
    const toolkit = normalizeContextTools<TestDeps>(undefined);

    expect(toolkit).toBeInstanceOf(ContextToolkit);
    expect(toolkit.tools).toHaveLength(0);
  });

  it("passes through existing ContextToolkit", () => {
    const original = new ContextToolkit<TestDeps>([tool]);
    const result = normalizeContextTools<TestDeps>(original);

    expect(result).toBe(original); // Same reference
    expect(result.tools).toHaveLength(1);
  });

  it("wraps array in new ContextToolkit", () => {
    const result = normalizeContextTools<TestDeps>([tool]);

    expect(result).toBeInstanceOf(ContextToolkit);
    expect(result.tools).toHaveLength(1);
    expect(result.toolMap.has("test_context_tool")).toBe(true);
  });
});

describe("Toolkit with provider tools", () => {
  const regularTool = defineTool<{ x: string }>({
    name: "regular_tool",
    description: "A regular tool",
    tool: ({ x }) => `result: ${x}`,
  });

  it("accepts provider tools alongside regular tools", () => {
    const providerTool = new ProviderTool("custom_provider");
    const webSearch = new WebSearchTool();

    const toolkit = new Toolkit([regularTool, providerTool, webSearch]);

    expect(toolkit.tools).toHaveLength(3);
    // schemas only includes regular tools, not provider tools
    expect(toolkit.schemas).toHaveLength(1);
    expect(toolkit.providerTools).toHaveLength(2);
  });

  it("returns only regular tools in schemas", () => {
    const webSearch = new WebSearchTool();
    const toolkit = new Toolkit([regularTool, webSearch]);

    expect(toolkit.schemas).toHaveLength(1);
    expect(toolkit.schemas[0]?.name).toBe("regular_tool");
  });

  it("returns only provider tools in providerTools", () => {
    const webSearch = new WebSearchTool();
    const customProvider = new ProviderTool("custom");
    const toolkit = new Toolkit([regularTool, webSearch, customProvider]);

    expect(toolkit.providerTools).toHaveLength(2);
    expect(toolkit.providerTools.map((t) => t.name)).toContain("web_search");
    expect(toolkit.providerTools.map((t) => t.name)).toContain("custom");
  });

  it("throws on duplicate provider tool names", () => {
    const tool1 = new ProviderTool("duplicate");
    const tool2 = new ProviderTool("duplicate");

    expect(() => new Toolkit([tool1, tool2])).toThrow(
      "Multiple provider tools with name: duplicate",
    );
  });

  it("allows same name for regular and provider tools", () => {
    // This matches Python behavior where tools_dict and provider_tools_dict are separate
    const regularWithSameName = defineTool<{ x: string }>({
      name: "same_name",
      description: "Regular tool",
      tool: () => "regular",
    });
    const providerWithSameName = new ProviderTool("same_name");

    const toolkit = new Toolkit([regularWithSameName, providerWithSameName]);

    expect(toolkit.tools).toHaveLength(2);
    expect(toolkit.schemas).toHaveLength(1);
    expect(toolkit.providerTools).toHaveLength(1);
  });

  it("get() only finds regular tools, not provider tools", () => {
    const webSearch = new WebSearchTool();
    const toolkit = new Toolkit([regularTool, webSearch]);

    expect(toolkit.get(createToolCall("regular_tool", {}))).toBe(regularTool);
    expect(toolkit.get(createToolCall("web_search", {}))).toBeUndefined();
  });

  it("toolMap.has() only checks regular tools, not provider tools", () => {
    const webSearch = new WebSearchTool();
    const toolkit = new Toolkit([regularTool, webSearch]);

    expect(toolkit.toolMap.has("regular_tool")).toBe(true);
    expect(toolkit.toolMap.has("web_search")).toBe(false);
  });
});

describe("ContextToolkit with provider tools", () => {
  interface TestDeps {
    value: number;
  }

  const contextTool = defineContextTool<{ x: string }, TestDeps>({
    name: "context_tool",
    description: "A context tool",
    tool: (ctx, { x }) => `result: ${x}, value: ${ctx.deps.value}`,
  });

  it("accepts provider tools alongside context tools", () => {
    const webSearch = new WebSearchTool();

    const toolkit = new ContextToolkit<TestDeps>([contextTool, webSearch]);

    expect(toolkit.tools).toHaveLength(2);
    expect(toolkit.schemas).toHaveLength(1);
    expect(toolkit.providerTools).toHaveLength(1);
  });

  it("returns only context tools in schemas", () => {
    const webSearch = new WebSearchTool();
    const toolkit = new ContextToolkit<TestDeps>([contextTool, webSearch]);

    expect(toolkit.schemas).toHaveLength(1);
    expect(toolkit.schemas[0]?.name).toBe("context_tool");
  });

  it("throws on duplicate provider tool names", () => {
    const tool1 = new ProviderTool("duplicate");
    const tool2 = new ProviderTool("duplicate");

    expect(() => new ContextToolkit<TestDeps>([tool1, tool2])).toThrow(
      "Multiple provider tools with name: duplicate",
    );
  });

  it("get() only finds context tools, not provider tools", () => {
    const webSearch = new WebSearchTool();
    const toolkit = new ContextToolkit<TestDeps>([contextTool, webSearch]);

    expect(toolkit.get(createToolCall("context_tool", {}))).toBe(contextTool);
    expect(toolkit.get(createToolCall("web_search", {}))).toBeUndefined();
  });
});
