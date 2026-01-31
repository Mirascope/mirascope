import { afterEach, describe, expect, it, vi } from "vitest";

import { ensureDirectory, writeFile } from "@/cli/utils/file-ops";

vi.mock("fs/promises", () => ({
  mkdir: vi.fn().mockResolvedValue(undefined),
}));

const mockBunWrite = vi.fn().mockResolvedValue(undefined);

vi.stubGlobal("Bun", {
  write: mockBunWrite,
});

describe("writeFile", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("creates parent directories and writes the file", async () => {
    const { mkdir } = await import("fs/promises");

    await writeFile("/path/to/file.txt", "file content");

    expect(mkdir).toHaveBeenCalledWith("/path/to", { recursive: true });
    expect(mockBunWrite).toHaveBeenCalledWith(
      "/path/to/file.txt",
      "file content",
    );
  });

  it("handles nested directory paths", async () => {
    const { mkdir } = await import("fs/promises");

    await writeFile("/deeply/nested/path/to/file.ts", "const x = 1;");

    expect(mkdir).toHaveBeenCalledWith("/deeply/nested/path/to", {
      recursive: true,
    });
    expect(mockBunWrite).toHaveBeenCalledWith(
      "/deeply/nested/path/to/file.ts",
      "const x = 1;",
    );
  });

  it("handles files in root directory", async () => {
    const { mkdir } = await import("fs/promises");

    await writeFile("/file.txt", "content");

    expect(mkdir).toHaveBeenCalledWith("/", { recursive: true });
    expect(mockBunWrite).toHaveBeenCalledWith("/file.txt", "content");
  });
});

describe("ensureDirectory", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("creates directory with recursive option", async () => {
    const { mkdir } = await import("fs/promises");

    await ensureDirectory("/path/to/dir");

    expect(mkdir).toHaveBeenCalledWith("/path/to/dir", { recursive: true });
  });

  it("handles nested paths", async () => {
    const { mkdir } = await import("fs/promises");

    await ensureDirectory("/deeply/nested/directory/path");

    expect(mkdir).toHaveBeenCalledWith("/deeply/nested/directory/path", {
      recursive: true,
    });
  });
});
