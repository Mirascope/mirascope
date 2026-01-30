import { describe, expect, it } from "vitest";

import { ProviderTool, isProviderTool } from "@/llm/tools/provider-tool";

describe("ProviderTool", () => {
  it("creates a provider tool with a name", () => {
    const tool = new ProviderTool("my_tool");

    expect(tool.name).toBe("my_tool");
  });

  it("name is readonly", () => {
    const tool = new ProviderTool("test");

    // TypeScript would error on: tool.name = 'other';
    expect(tool.name).toBe("test");
  });
});

describe("isProviderTool", () => {
  it("returns true for ProviderTool instances", () => {
    const tool = new ProviderTool("test");

    expect(isProviderTool(tool)).toBe(true);
  });

  it("returns false for non-ProviderTool values", () => {
    expect(isProviderTool(null)).toBe(false);
    expect(isProviderTool(undefined)).toBe(false);
    expect(isProviderTool({})).toBe(false);
    expect(isProviderTool({ name: "test" })).toBe(false);
    expect(isProviderTool("string")).toBe(false);
    expect(isProviderTool(123)).toBe(false);
  });
});
