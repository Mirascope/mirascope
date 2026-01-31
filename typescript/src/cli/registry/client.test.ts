import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { RegistryClient } from "@/cli/registry/client";

const mockFetch = vi.fn();

describe("RegistryClient", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", mockFetch);
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.unstubAllGlobals();
  });

  describe("constructor", () => {
    it("uses default base URL", () => {
      const client = new RegistryClient();
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ items: [] }),
      });

      client.fetchIndex();

      expect(mockFetch).toHaveBeenCalledWith(
        "https://mirascope.com/registry/r/index.json",
      );
    });

    it("accepts custom base URL", () => {
      const client = new RegistryClient("https://custom.registry.com");
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ items: [] }),
      });

      client.fetchIndex();

      expect(mockFetch).toHaveBeenCalledWith(
        "https://custom.registry.com/r/index.json",
      );
    });

    it("strips trailing slash from base URL", () => {
      const client = new RegistryClient("https://custom.registry.com/");
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ items: [] }),
      });

      client.fetchIndex();

      expect(mockFetch).toHaveBeenCalledWith(
        "https://custom.registry.com/r/index.json",
      );
    });
  });

  describe("fetchIndex", () => {
    it("returns parsed index on success", async () => {
      const mockIndex = {
        name: "mirascope-registry",
        version: "1.0.0",
        homepage: "https://mirascope.com",
        items: [{ name: "calculator", type: "tool", path: "tools/calculator" }],
      };
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockIndex),
      });

      const client = new RegistryClient();
      const result = await client.fetchIndex();

      expect(result).toEqual(mockIndex);
    });

    it("returns null on 404 response", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
      });

      const client = new RegistryClient();
      const result = await client.fetchIndex();

      expect(result).toBeNull();
    });

    it("throws error on non-404 HTTP error", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 500,
      });

      const client = new RegistryClient();

      await expect(client.fetchIndex()).rejects.toThrow("HTTP 500");
    });
  });

  describe("fetchItem", () => {
    it("fetches item with default language", async () => {
      const mockItem = {
        name: "calculator",
        type: "tool",
        files: [
          {
            path: "calculator.ts",
            target: "tools/calculator.ts",
            content: "// code",
          },
        ],
        dependencies: { pip: [], npm: ["zod"] },
      };
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockItem),
      });

      const client = new RegistryClient();
      const result = await client.fetchItem("calculator");

      expect(mockFetch).toHaveBeenCalledWith(
        "https://mirascope.com/registry/r/calculator.typescript.json",
      );
      expect(result).toEqual(mockItem);
    });

    it("fetches item with specified language", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ name: "calculator" }),
      });

      const client = new RegistryClient();
      await client.fetchItem("calculator", "python");

      expect(mockFetch).toHaveBeenCalledWith(
        "https://mirascope.com/registry/r/calculator.python.json",
      );
    });

    it("handles namespaced items with @ prefix", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ name: "calculator" }),
      });

      const client = new RegistryClient();
      await client.fetchItem("@mirascope/calculator");

      expect(mockFetch).toHaveBeenCalledWith(
        "https://mirascope.com/registry/r/calculator.typescript.json",
      );
    });

    it("handles deeply nested namespaced items", async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ name: "tool" }),
      });

      const client = new RegistryClient();
      await client.fetchItem("@org/sub/tool");

      expect(mockFetch).toHaveBeenCalledWith(
        "https://mirascope.com/registry/r/tool.typescript.json",
      );
    });

    it("returns null on 404 response", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 404,
      });

      const client = new RegistryClient();
      const result = await client.fetchItem("nonexistent");

      expect(result).toBeNull();
    });

    it("throws error on non-404 HTTP error", async () => {
      mockFetch.mockResolvedValue({
        ok: false,
        status: 503,
      });

      const client = new RegistryClient();

      await expect(client.fetchItem("calculator")).rejects.toThrow("HTTP 503");
    });
  });
});
