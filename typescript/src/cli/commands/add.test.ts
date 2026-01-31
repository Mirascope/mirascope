import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { runAdd } from "@/cli/commands/add";

const mockFetchItem = vi.fn();

vi.mock("@/cli/registry/client", () => ({
  RegistryClient: vi.fn().mockImplementation(() => ({
    fetchItem: mockFetchItem,
  })),
}));

const mockLoadConfig = vi.fn();

vi.mock("@/cli/utils/config", () => ({
  loadConfig: () => mockLoadConfig(),
}));

const mockWriteFile = vi.fn();

vi.mock("@/cli/utils/file-ops", () => ({
  writeFile: (...args: unknown[]) => mockWriteFile(...args),
}));

const mockFileExists = vi.fn();
const mockFileJson = vi.fn();

vi.stubGlobal("Bun", {
  file: vi.fn(() => ({
    exists: mockFileExists,
    json: mockFileJson,
  })),
});

const originalCwd = process.cwd;
const mockConsoleLog = vi.spyOn(console, "log").mockImplementation(() => {});
const mockConsoleError = vi
  .spyOn(console, "error")
  .mockImplementation(() => {});

describe("runAdd", () => {
  beforeEach(() => {
    process.cwd = vi.fn().mockReturnValue("/test/project");
    mockLoadConfig.mockResolvedValue(null);
  });

  afterEach(() => {
    vi.clearAllMocks();
    process.cwd = originalCwd;
  });

  describe("fetching from registry", () => {
    it("fetches and writes item from registry", async () => {
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "registry:tool",
        files: [
          {
            path: "calculator.ts",
            target: "tools/calculator.ts",
            content: "// calculator code",
          },
        ],
        dependencies: { pip: [], npm: ["zod"] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["calculator"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockConsoleLog).toHaveBeenCalledWith("Adding calculator...");
      expect(mockWriteFile).toHaveBeenCalledWith(
        "/test/project/tools/calculator.ts",
        "// calculator code",
      );
      expect(mockConsoleLog).toHaveBeenCalledWith(
        "  Created /test/project/tools/calculator.ts",
      );
    });

    it("returns 1 when registry fetch fails", async () => {
      mockFetchItem.mockRejectedValue(new Error("Network error"));

      const result = await runAdd({
        items: ["calculator"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(1);
      expect(mockConsoleError).toHaveBeenCalledWith(
        "Error: Failed to fetch 'calculator': Error: Network error",
      );
    });

    it("returns 1 when item not found in registry", async () => {
      mockFetchItem.mockResolvedValue(null);

      const result = await runAdd({
        items: ["nonexistent"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(1);
      expect(mockConsoleError).toHaveBeenCalledWith(
        "Error: Item 'nonexistent' not found in registry.",
      );
    });
  });

  describe("loading local files", () => {
    it("loads item from local JSON file with ./ prefix", async () => {
      mockFileExists.mockResolvedValueOnce(true); // Local file exists
      mockFileJson.mockResolvedValueOnce({
        name: "local-tool",
        type: "tool",
        files: [
          {
            path: "local.ts",
            target: "tools/local.ts",
            content: "// local content",
          },
        ],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValueOnce(false); // Target doesn't exist
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["./local-tool.json"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockFetchItem).not.toHaveBeenCalled();
    });

    it("loads item from local JSON file with / prefix", async () => {
      mockFileExists.mockResolvedValueOnce(true);
      mockFileJson.mockResolvedValueOnce({
        name: "abs-tool",
        type: "tool",
        files: [{ path: "tool.ts", target: "tool.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValueOnce(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["/absolute/path/tool.json"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockFetchItem).not.toHaveBeenCalled();
    });

    it("loads item from file ending with .json", async () => {
      mockFileExists.mockResolvedValueOnce(true);
      mockFileJson.mockResolvedValueOnce({
        name: "json-tool",
        type: "tool",
        files: [{ path: "tool.ts", target: "tool.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValueOnce(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["tool.json"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockFetchItem).not.toHaveBeenCalled();
    });

    it("returns 1 when local file not found", async () => {
      mockFileExists.mockResolvedValue(false);

      const result = await runAdd({
        items: ["./missing.json"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(1);
      expect(mockConsoleError).toHaveBeenCalledWith(
        "Error: Local file './missing.json' not found.",
      );
    });

    it("returns 1 when local JSON parsing fails", async () => {
      mockFileExists.mockResolvedValueOnce(true);
      mockFileJson.mockRejectedValueOnce(new Error("Invalid JSON"));

      const result = await runAdd({
        items: ["./invalid.json"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(1);
      expect(mockConsoleError).toHaveBeenCalledWith(
        "Error: Local file './invalid.json' not found.",
      );
    });
  });

  describe("file writing", () => {
    it("skips existing files without overwrite flag", async () => {
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "tool",
        files: [{ path: "calc.ts", target: "tools/calc.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(true);

      const result = await runAdd({
        items: ["calculator"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).not.toHaveBeenCalled();
      expect(mockConsoleError).toHaveBeenCalledWith(
        expect.stringContaining("already exists. Use --overwrite to replace."),
      );
    });

    it("overwrites existing files with overwrite flag", async () => {
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "tool",
        files: [
          { path: "calc.ts", target: "tools/calc.ts", content: "new code" },
        ],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(true);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["calculator"],
        overwrite: true,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).toHaveBeenCalled();
    });

    it("returns 1 when file write fails", async () => {
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "tool",
        files: [{ path: "calc.ts", target: "tools/calc.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockRejectedValue(new Error("Permission denied"));

      const result = await runAdd({
        items: ["calculator"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(1);
      expect(mockConsoleError).toHaveBeenCalledWith(
        expect.stringContaining("Failed to write"),
      );
    });

    it("uses custom path option", async () => {
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "tool",
        files: [{ path: "calc.ts", target: "tools/calc.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["calculator"],
        path: "/custom/path",
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).toHaveBeenCalledWith(
        "/custom/path/tools/calc.ts",
        "code",
      );
    });
  });

  describe("config-based paths", () => {
    it("uses configured paths for item types", async () => {
      mockLoadConfig.mockResolvedValue({
        paths: {
          tools: "src/ai/tools",
        },
      });
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "registry:tool",
        files: [{ path: "calc.ts", target: "tools/calc.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["calculator"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).toHaveBeenCalledWith(
        "/test/project/src/ai/tools/calc.ts",
        "code",
      );
    });

    it("handles single-part target paths with config", async () => {
      mockLoadConfig.mockResolvedValue({
        paths: {
          tools: "custom/tools",
        },
      });
      mockFetchItem.mockResolvedValue({
        name: "simple",
        type: "registry:tool",
        files: [{ path: "simple.ts", target: "simple.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["simple"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).toHaveBeenCalledWith(
        "/test/project/custom/tools/simple.ts",
        "code",
      );
    });
  });

  describe("dependencies", () => {
    it("prints npm dependencies to install", async () => {
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "tool",
        files: [{ path: "calc.ts", target: "calc.ts", content: "code" }],
        dependencies: { pip: [], npm: ["zod", "@mirascope/core"] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["calculator"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockConsoleLog).toHaveBeenCalledWith(
        "\nInstall required npm dependencies:",
      );
      expect(mockConsoleLog).toHaveBeenCalledWith(
        "  bun add zod @mirascope/core",
      );
    });

    it("does not print dependencies section when none required", async () => {
      mockFetchItem.mockResolvedValue({
        name: "calculator",
        type: "tool",
        files: [{ path: "calc.ts", target: "calc.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      await runAdd({
        items: ["calculator"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(mockConsoleLog).not.toHaveBeenCalledWith(
        "\nInstall required npm dependencies:",
      );
    });

    it("deduplicates dependencies across multiple items", async () => {
      mockFetchItem
        .mockResolvedValueOnce({
          name: "tool1",
          type: "tool",
          files: [{ path: "t1.ts", target: "t1.ts", content: "code" }],
          dependencies: { pip: [], npm: ["zod"] },
        })
        .mockResolvedValueOnce({
          name: "tool2",
          type: "tool",
          files: [{ path: "t2.ts", target: "t2.ts", content: "code" }],
          dependencies: { pip: [], npm: ["zod", "axios"] },
        });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      await runAdd({
        items: ["tool1", "tool2"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      // Should deduplicate zod
      expect(mockConsoleLog).toHaveBeenCalledWith("  bun add zod axios");
    });

    it("collects and deduplicates pip dependencies", async () => {
      mockFetchItem
        .mockResolvedValueOnce({
          name: "tool1",
          type: "tool",
          files: [{ path: "t1.ts", target: "t1.ts", content: "code" }],
          dependencies: { pip: ["requests"], npm: [] },
        })
        .mockResolvedValueOnce({
          name: "tool2",
          type: "tool",
          files: [{ path: "t2.ts", target: "t2.ts", content: "code" }],
          dependencies: { pip: ["requests", "httpx"], npm: [] },
        });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["tool1", "tool2"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      // Pip dependencies are collected but not printed (TypeScript CLI only shows npm)
      expect(result).toBe(0);
    });
  });

  describe("multiple items", () => {
    it("adds multiple items", async () => {
      mockFetchItem
        .mockResolvedValueOnce({
          name: "tool1",
          type: "tool",
          files: [{ path: "t1.ts", target: "t1.ts", content: "code1" }],
          dependencies: { pip: [], npm: [] },
        })
        .mockResolvedValueOnce({
          name: "tool2",
          type: "tool",
          files: [{ path: "t2.ts", target: "t2.ts", content: "code2" }],
          dependencies: { pip: [], npm: [] },
        });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["tool1", "tool2"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).toHaveBeenCalledTimes(2);
      expect(mockConsoleLog).toHaveBeenCalledWith(
        "\nSuccessfully added 2 file(s).",
      );
    });
  });

  describe("edge cases", () => {
    it("handles item with no files array", async () => {
      mockFetchItem.mockResolvedValue({
        name: "empty",
        type: "tool",
        dependencies: { pip: [], npm: [] },
      });

      const result = await runAdd({
        items: ["empty"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).not.toHaveBeenCalled();
    });

    it("handles item with no dependencies", async () => {
      mockFetchItem.mockResolvedValue({
        name: "nodeps",
        type: "tool",
        files: [{ path: "n.ts", target: "n.ts", content: "code" }],
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["nodeps"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
    });

    it("handles file with missing target (uses path)", async () => {
      mockFetchItem.mockResolvedValue({
        name: "notarget",
        type: "tool",
        files: [{ path: "tools/file.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["notarget"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).toHaveBeenCalledWith(
        "/test/project/tools/file.ts",
        "code",
      );
    });

    it("handles file with empty content", async () => {
      mockFetchItem.mockResolvedValue({
        name: "emptycontent",
        type: "tool",
        files: [{ path: "e.ts", target: "e.ts" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["emptycontent"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      expect(mockWriteFile).toHaveBeenCalledWith("/test/project/e.ts", "");
    });

    it("handles file with no target and no path (uses empty string)", async () => {
      mockFetchItem.mockResolvedValue({
        name: "nopath",
        type: "tool",
        files: [{ content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["nopath"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      // Target becomes empty string, path.join handles it
      expect(mockWriteFile).toHaveBeenCalledWith("/test/project", "code");
    });

    it("handles item with no type when config has paths", async () => {
      mockLoadConfig.mockResolvedValue({
        paths: {
          tools: "ai/tools",
        },
      });
      mockFetchItem.mockResolvedValue({
        name: "notype",
        files: [{ path: "file.ts", target: "tools/file.ts", content: "code" }],
        dependencies: { pip: [], npm: [] },
      });
      mockFileExists.mockResolvedValue(false);
      mockWriteFile.mockResolvedValue(undefined);

      const result = await runAdd({
        items: ["notype"],
        overwrite: false,
        registryUrl: "https://mirascope.com/registry",
      });

      expect(result).toBe(0);
      // With no type, "s" path lookup will not match, so original target is used
      expect(mockWriteFile).toHaveBeenCalledWith(
        "/test/project/tools/file.ts",
        "code",
      );
    });
  });
});
