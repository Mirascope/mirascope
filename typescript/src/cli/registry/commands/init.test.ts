import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { initCommand } from "@/cli/registry/commands/init";

const mockFileExists = vi.fn();
const mockBunWrite = vi.fn();

vi.stubGlobal("Bun", {
  file: vi.fn(() => ({
    exists: mockFileExists,
  })),
  write: mockBunWrite,
});

const originalCwd = process.cwd;
const mockConsoleLog = vi.spyOn(console, "log").mockImplementation(() => {});
const mockConsoleError = vi
  .spyOn(console, "error")
  .mockImplementation(() => {});
const mockProcessExit = vi.fn<(code?: number) => never>();

describe("initCommand", () => {
  beforeEach(() => {
    vi.stubGlobal("process", {
      ...process,
      exit: mockProcessExit,
      cwd: vi.fn().mockReturnValue("/test/project"),
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal("process", {
      ...process,
      cwd: originalCwd,
    });
  });

  it("returns early and logs message when config already exists", async () => {
    mockFileExists.mockResolvedValue(true);

    await initCommand();

    expect(mockConsoleLog).toHaveBeenCalledWith(
      "Configuration already exists at /test/project/mirascope.json",
    );
    expect(mockBunWrite).not.toHaveBeenCalled();
  });

  it("creates config file when it does not exist", async () => {
    mockFileExists.mockResolvedValue(false);
    mockBunWrite.mockResolvedValue(undefined);

    await initCommand();

    expect(mockBunWrite).toHaveBeenCalledTimes(1);

    const [path, content] = mockBunWrite.mock.calls[0]!;
    expect(path).toBe("/test/project/mirascope.json");

    const writtenConfig = JSON.parse(content.trim());
    expect(writtenConfig).toEqual({
      $schema: "https://mirascope.com/registry/schema/config.json",
      language: "typescript",
      registry: "https://mirascope.com/registry",
      paths: {
        tools: "ai/tools",
        agents: "ai/agents",
        prompts: "ai/prompts",
        integrations: "ai/integrations",
      },
    });
  });

  it("logs success message after creating config", async () => {
    mockFileExists.mockResolvedValue(false);
    mockBunWrite.mockResolvedValue(undefined);

    await initCommand();

    expect(mockConsoleLog).toHaveBeenCalledWith(
      "Created /test/project/mirascope.json",
    );
    expect(mockConsoleLog).toHaveBeenCalledWith(
      "\nYou can now use `mirascope registry add <item>` to add registry items.",
    );
  });

  it("exits with 1 and logs error when write fails", async () => {
    mockFileExists.mockResolvedValue(false);
    mockBunWrite.mockRejectedValue(new Error("Permission denied"));

    await initCommand();

    expect(mockProcessExit).toHaveBeenCalledWith(1);
    expect(mockConsoleError).toHaveBeenCalledWith(
      "Error: Failed to create config file: Error: Permission denied",
    );
  });

  it("uses correct path from process.cwd()", async () => {
    process.cwd = vi.fn().mockReturnValue("/different/directory");
    mockFileExists.mockResolvedValue(false);
    mockBunWrite.mockResolvedValue(undefined);

    await initCommand();

    expect(Bun.file).toHaveBeenCalledWith(
      "/different/directory/mirascope.json",
    );
    expect(mockBunWrite).toHaveBeenCalledWith(
      "/different/directory/mirascope.json",
      expect.any(String),
    );
  });
});
