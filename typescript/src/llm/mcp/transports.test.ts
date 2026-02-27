/**
 * Tests for MCP transport implementations.
 */

import { describe, expect, it, vi } from "vitest";

import type { MCPClientSession } from "./types";

import { MCPClient } from "./mcp-client";
import { using, type MCPResource } from "./transports";

// Helper to create a mock MCPClient
function createMockClient(): MCPClient {
  const session: MCPClientSession = {
    initialize: vi.fn().mockResolvedValue(undefined),
    listTools: vi.fn().mockResolvedValue({ tools: [] }),
    callTool: vi.fn().mockResolvedValue({ content: [] }),
  };
  return new MCPClient(session);
}

// Helper to create a mock MCPResource
function createMockResource(client?: MCPClient): MCPResource {
  return {
    client: client ?? createMockClient(),
    close: vi.fn().mockResolvedValue(undefined),
  };
}

describe("using", () => {
  it("executes the callback with the client", async () => {
    const mockClient = createMockClient();
    const mockResource = createMockResource(mockClient);
    const callback = vi.fn().mockResolvedValue("result");

    const result = await using(Promise.resolve(mockResource), callback);

    expect(callback).toHaveBeenCalledWith(mockClient);
    expect(result).toBe("result");
  });

  it("closes the resource after successful callback", async () => {
    const mockResource = createMockResource();
    const callback = vi.fn().mockResolvedValue("done");

    await using(Promise.resolve(mockResource), callback);

    expect(mockResource.close).toHaveBeenCalled();
  });

  it("closes the resource even if callback throws", async () => {
    const mockResource = createMockResource();
    const error = new Error("callback failed");
    const callback = vi.fn().mockRejectedValue(error);

    await expect(
      using(Promise.resolve(mockResource), callback),
    ).rejects.toThrow("callback failed");
    expect(mockResource.close).toHaveBeenCalled();
  });

  it("propagates the callback return value", async () => {
    const mockResource = createMockResource();
    const tools = [{ name: "tool1" }, { name: "tool2" }];
    const callback = vi.fn().mockResolvedValue(tools);

    const result = await using(Promise.resolve(mockResource), callback);

    expect(result).toBe(tools);
  });

  it("handles async callbacks correctly", async () => {
    const mockResource = createMockResource();
    const callback = vi.fn(async () => {
      await new Promise((resolve) => setTimeout(resolve, 10));
      return "async result";
    });

    const result = await using(Promise.resolve(mockResource), callback);

    expect(result).toBe("async result");
    expect(mockResource.close).toHaveBeenCalled();
  });

  it("handles resource creation failure", async () => {
    const error = new Error("failed to create resource");

    await expect(using(Promise.reject(error), vi.fn())).rejects.toThrow(
      "failed to create resource",
    );
  });
});

describe("MCPResource interface", () => {
  it("has client and close properties", () => {
    const resource = createMockResource();

    expect(resource.client).toBeInstanceOf(MCPClient);
    expect(typeof resource.close).toBe("function");
  });
});
