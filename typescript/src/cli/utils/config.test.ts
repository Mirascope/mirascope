import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { loadConfig } from "@/cli/utils/config";

const mockFileExists = vi.fn();
const mockFileJson = vi.fn();

vi.stubGlobal("Bun", {
  file: vi.fn(() => ({
    exists: mockFileExists,
    json: mockFileJson,
  })),
});

const originalCwd = process.cwd;

describe("loadConfig", () => {
  beforeEach(() => {
    process.cwd = vi.fn().mockReturnValue("/test/project");
  });

  afterEach(() => {
    vi.clearAllMocks();
    process.cwd = originalCwd;
  });

  it("returns null when config file does not exist", async () => {
    mockFileExists.mockResolvedValue(false);

    const result = await loadConfig();

    expect(result).toBeNull();
    expect(Bun.file).toHaveBeenCalledWith("/test/project/mirascope.json");
  });

  it("returns parsed config when file exists", async () => {
    const mockConfig = {
      $schema: "https://mirascope.com/registry/schema/config.json",
      language: "typescript",
      registry: "https://mirascope.com/registry",
      paths: {
        tools: "ai/tools",
        agents: "ai/agents",
      },
    };
    mockFileExists.mockResolvedValue(true);
    mockFileJson.mockResolvedValue(mockConfig);

    const result = await loadConfig();

    expect(result).toEqual(mockConfig);
  });

  it("returns null when JSON parsing fails", async () => {
    mockFileExists.mockResolvedValue(true);
    mockFileJson.mockRejectedValue(new Error("Invalid JSON"));

    const result = await loadConfig();

    expect(result).toBeNull();
  });

  it("uses correct config path from current directory", async () => {
    process.cwd = vi.fn().mockReturnValue("/different/path");
    mockFileExists.mockResolvedValue(false);

    await loadConfig();

    expect(Bun.file).toHaveBeenCalledWith("/different/path/mirascope.json");
  });
});
