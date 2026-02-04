import { afterEach, describe, expect, it, vi } from "vitest";

import { runList } from "@/cli/commands/list";

const mockFetchIndex = vi.fn();

vi.mock("@/cli/registry/client", () => ({
  RegistryClient: vi.fn().mockImplementation(() => ({
    fetchIndex: mockFetchIndex,
  })),
}));

const mockConsoleLog = vi.spyOn(console, "log").mockImplementation(() => {});
const mockConsoleError = vi
  .spyOn(console, "error")
  .mockImplementation(() => {});

describe("runList", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("returns 1 and logs error when fetch fails", async () => {
    mockFetchIndex.mockRejectedValue(new Error("Network error"));

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
    });

    expect(result).toBe(1);
    expect(mockConsoleError).toHaveBeenCalledWith(
      "Error: Failed to fetch registry index: Error: Network error",
    );
  });

  it("returns 1 when index is null", async () => {
    mockFetchIndex.mockResolvedValue(null);

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
    });

    expect(result).toBe(1);
    expect(mockConsoleError).toHaveBeenCalledWith(
      "Error: Could not fetch registry index.",
    );
  });

  it("logs message when no items found", async () => {
    mockFetchIndex.mockResolvedValue({ items: [] });

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
    });

    expect(result).toBe(0);
    expect(mockConsoleLog).toHaveBeenCalledWith("No items found in registry.");
  });

  it("logs message when no items match type filter", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [{ name: "calculator", type: "tool" }],
    });

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
      itemType: "agent",
    });

    expect(result).toBe(0);
    expect(mockConsoleLog).toHaveBeenCalledWith(
      "No items found with type 'agent'.",
    );
  });

  it("lists items grouped by type", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [
        { name: "calculator", type: "tool", description: "A calculator tool" },
        { name: "web-search", type: "tool", description: "Web search" },
        { name: "analyst", type: "agent", description: "An analyst agent" },
      ],
    });

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
    });

    expect(result).toBe(0);
    expect(mockConsoleLog).toHaveBeenCalledWith(
      "Available items from https://mirascope.com/registry:\n",
    );
    expect(mockConsoleLog).toHaveBeenCalledWith("Agents:");
    expect(mockConsoleLog).toHaveBeenCalledWith("Tools:");
    expect(mockConsoleLog).toHaveBeenCalledWith(
      "Use `mirascope registry add <name>` to install.",
    );
  });

  it("filters items by type", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [
        { name: "calculator", type: "tool" },
        { name: "analyst", type: "agent" },
      ],
    });

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
      itemType: "tool",
    });

    expect(result).toBe(0);
    // Should only show tools
    expect(mockConsoleLog).toHaveBeenCalledWith("Tools:");
  });

  it("handles items with missing type", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [{ name: "unknown-item" }],
    });

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
    });

    expect(result).toBe(0);
    expect(mockConsoleLog).toHaveBeenCalledWith("Others:");
  });

  it("handles items with missing name and description", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [{ type: "tool" }],
    });

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
    });

    expect(result).toBe(0);
    expect(mockConsoleLog).toHaveBeenCalledWith("Tools:");
    // Should use "unknown" for missing name and empty string for missing description
    expect(mockConsoleLog).toHaveBeenCalledWith(
      expect.stringContaining("unknown"),
    );
  });

  it("handles empty items array in index", async () => {
    mockFetchIndex.mockResolvedValue({ items: undefined });

    const result = await runList({
      registryUrl: "https://mirascope.com/registry",
    });

    expect(result).toBe(0);
    expect(mockConsoleLog).toHaveBeenCalledWith("No items found in registry.");
  });
});
