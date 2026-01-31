import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { listCommand } from "@/cli/registry/commands/list";

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
const mockProcessExit = vi.fn<(code?: number) => never>();

describe("listCommand", () => {
  beforeEach(() => {
    vi.stubGlobal("process", {
      ...process,
      exit: mockProcessExit,
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.unstubAllGlobals();
  });

  it("exits with 1 and logs error when fetch fails", async () => {
    mockFetchIndex.mockRejectedValue(new Error("Network error"));

    await listCommand(undefined, "https://mirascope.com/registry");

    expect(mockProcessExit).toHaveBeenCalledWith(1);
    expect(mockConsoleError).toHaveBeenCalledWith(
      "Error: Failed to fetch registry index: Error: Network error",
    );
  });

  it("exits with 1 when index is null", async () => {
    mockFetchIndex.mockResolvedValue(null);

    await listCommand(undefined, "https://mirascope.com/registry");

    expect(mockProcessExit).toHaveBeenCalledWith(1);
    expect(mockConsoleError).toHaveBeenCalledWith(
      "Error: Could not fetch registry index.",
    );
  });

  it("logs message when no items found", async () => {
    mockFetchIndex.mockResolvedValue({ items: [] });

    await listCommand(undefined, "https://mirascope.com/registry");

    expect(mockConsoleLog).toHaveBeenCalledWith("No items found in registry.");
  });

  it("logs message when no items match type filter", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [{ name: "calculator", type: "tool" }],
    });

    await listCommand("agent", "https://mirascope.com/registry");

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

    await listCommand(undefined, "https://mirascope.com/registry");

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

    await listCommand("tool", "https://mirascope.com/registry");

    // Should only show tools
    expect(mockConsoleLog).toHaveBeenCalledWith("Tools:");
  });

  it("handles items with missing type", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [{ name: "unknown-item" }],
    });

    await listCommand(undefined, "https://mirascope.com/registry");

    expect(mockConsoleLog).toHaveBeenCalledWith("Others:");
  });

  it("handles items with missing name and description", async () => {
    mockFetchIndex.mockResolvedValue({
      items: [{ type: "tool" }],
    });

    await listCommand(undefined, "https://mirascope.com/registry");

    expect(mockConsoleLog).toHaveBeenCalledWith("Tools:");
    // Should use "unknown" for missing name and empty string for missing description
    expect(mockConsoleLog).toHaveBeenCalledWith(
      expect.stringContaining("unknown"),
    );
  });

  it("handles empty items array in index", async () => {
    mockFetchIndex.mockResolvedValue({ items: undefined });

    await listCommand(undefined, "https://mirascope.com/registry");

    expect(mockConsoleLog).toHaveBeenCalledWith("No items found in registry.");
  });
});
