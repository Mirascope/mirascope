/**
 * Tests for MCP error classes.
 */

import { describe, expect, it } from "vitest";

import { MirascopeError } from "@/llm/exceptions";

import {
  MCPError,
  MCPNotInstalledError,
  MCPConnectionError,
  MCPToolError,
} from "./errors";

describe("MCPError", () => {
  it("extends MirascopeError", () => {
    const error = new MCPError("test message");

    expect(error).toBeInstanceOf(MirascopeError);
    expect(error).toBeInstanceOf(Error);
  });

  it("stores the message", () => {
    const error = new MCPError("test message");

    expect(error.message).toBe("test message");
  });

  it("has correct name", () => {
    const error = new MCPError("test");

    expect(error.name).toBe("MCPError");
  });
});

describe("MCPNotInstalledError", () => {
  it("extends MCPError", () => {
    const error = new MCPNotInstalledError();

    expect(error).toBeInstanceOf(MCPError);
    expect(error).toBeInstanceOf(MirascopeError);
  });

  it("has helpful installation message", () => {
    const error = new MCPNotInstalledError();

    expect(error.message).toContain("@modelcontextprotocol/sdk");
    expect(error.message).toContain("npm install");
  });

  it("has correct name", () => {
    const error = new MCPNotInstalledError();

    expect(error.name).toBe("MCPNotInstalledError");
  });
});

describe("MCPConnectionError", () => {
  it("extends MCPError", () => {
    const error = new MCPConnectionError("connection failed");

    expect(error).toBeInstanceOf(MCPError);
    expect(error).toBeInstanceOf(MirascopeError);
  });

  it("stores the message", () => {
    const error = new MCPConnectionError("connection failed");

    expect(error.message).toBe("connection failed");
  });

  it("stores optional originalError", () => {
    const original = new Error("underlying error");
    const error = new MCPConnectionError("connection failed", original);

    expect(error.originalError).toBe(original);
    expect(error.cause).toBe(original);
  });

  it("handles missing originalError", () => {
    const error = new MCPConnectionError("connection failed");

    expect(error.originalError).toBeUndefined();
    expect(error.cause).toBeUndefined();
  });

  it("has correct name", () => {
    const error = new MCPConnectionError("test");

    expect(error.name).toBe("MCPConnectionError");
  });
});

describe("MCPToolError", () => {
  it("extends MCPError", () => {
    const error = new MCPToolError("my_tool", "execution failed");

    expect(error).toBeInstanceOf(MCPError);
    expect(error).toBeInstanceOf(MirascopeError);
  });

  it("includes tool name in message", () => {
    const error = new MCPToolError("greet", "API timeout");

    expect(error.message).toBe("MCP tool 'greet' failed: API timeout");
  });

  it("stores the tool name", () => {
    const error = new MCPToolError("my_tool", "failed");

    expect(error.toolName).toBe("my_tool");
  });

  it("stores optional originalError", () => {
    const original = new Error("network error");
    const error = new MCPToolError("my_tool", "failed", original);

    expect(error.originalError).toBe(original);
    expect(error.cause).toBe(original);
  });

  it("handles missing originalError", () => {
    const error = new MCPToolError("my_tool", "failed");

    expect(error.originalError).toBeUndefined();
    expect(error.cause).toBeUndefined();
  });

  it("has correct name", () => {
    const error = new MCPToolError("test", "msg");

    expect(error.name).toBe("MCPToolError");
  });
});
