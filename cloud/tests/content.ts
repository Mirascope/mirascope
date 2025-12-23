import { Effect, Layer, Option } from "effect";
import { FileSystem, Path, Error as PlatformError } from "@effect/platform";
import { it as vitestIt, describe, expect } from "@effect/vitest";

// Re-export describe and expect for convenience
export { describe, expect };

// =============================================================================
// Mock FileSystem Builder
// =============================================================================

/**
 * Result type for mock file operations
 */
type MockResult<T> = T | Error;

/**
 * Builder for creating mock FileSystem layers with predefined file contents.
 *
 * Allows setting up a virtual filesystem for testing Effect-based code
 * that uses the FileSystem service.
 *
 * @example
 * ```ts
 * const mockFs = new MockFileSystem()
 *   .addFile("/path/to/file.mdx", "# Hello World")
 *   .addDirectory("/path/to/empty-dir")
 *   .build();
 *
 * const result = yield* someEffectUsingFileSystem
 *   .pipe(Effect.provide(mockFs));
 * ```
 *
 * @example Testing error scenarios
 * ```ts
 * const mockFs = new MockFileSystem()
 *   .setReadError("/path/to/file.txt", new Error("Permission denied"))
 *   .build();
 *
 * const result = yield* readFile("/path/to/file.txt")
 *   .pipe(Effect.flip); // Converts failure to success for assertion
 *
 * expect(result).toBeInstanceOf(ContentError);
 * ```
 */
export class MockFileSystem {
  private files: Map<string, MockResult<string>> = new Map();
  private directories: Set<string> = new Set();
  private readErrors: Map<string, Error> = new Map();
  private writeErrors: Map<string, Error> = new Map();
  private statErrors: Map<string, Error> = new Map();

  /**
   * Add a file with content to the mock filesystem
   */
  addFile(filePath: string, content: string): this {
    this.files.set(filePath, content);
    // Also add parent directories
    this.addParentDirectories(filePath);
    return this;
  }

  /**
   * Add an empty directory to the mock filesystem
   */
  addDirectory(dirPath: string): this {
    this.directories.add(dirPath);
    this.addParentDirectories(dirPath);
    return this;
  }

  /**
   * Set a read error for a specific file
   */
  setReadError(filePath: string, error: Error): this {
    this.readErrors.set(filePath, error);
    return this;
  }

  /**
   * Set a write error for a specific file
   */
  setWriteError(filePath: string, error: Error): this {
    this.writeErrors.set(filePath, error);
    return this;
  }

  /**
   * Set a stat error for a specific path
   */
  setStatError(path: string, error: Error): this {
    this.statErrors.set(path, error);
    return this;
  }

  /**
   * Add parent directories for a given path
   */
  private addParentDirectories(filePath: string): void {
    const parts = filePath.split("/").filter(Boolean);
    let current = "";
    for (let i = 0; i < parts.length - 1; i++) {
      current += "/" + parts[i];
      this.directories.add(current);
    }
  }

  /**
   * Get directory entries for a path
   */
  private getDirectoryEntries(dirPath: string): string[] {
    const entries: Set<string> = new Set();
    const normalizedDir = dirPath.endsWith("/") ? dirPath : dirPath + "/";

    // Check files
    for (const filePath of this.files.keys()) {
      if (filePath.startsWith(normalizedDir)) {
        const remaining = filePath.slice(normalizedDir.length);
        const firstPart = remaining.split("/")[0];
        if (firstPart) {
          entries.add(firstPart);
        }
      }
    }

    // Check directories
    for (const dir of this.directories) {
      if (dir.startsWith(normalizedDir) && dir !== dirPath) {
        const remaining = dir.slice(normalizedDir.length);
        const firstPart = remaining.split("/")[0];
        if (firstPart) {
          entries.add(firstPart);
        }
      }
    }

    return Array.from(entries);
  }

  /**
   * Check if a path exists
   */
  private pathExists(path: string): boolean {
    return this.files.has(path) || this.directories.has(path);
  }

  /**
   * Check if a path is a file
   */
  private isFile(path: string): boolean {
    return this.files.has(path);
  }

  /**
   * Check if a path is a directory
   */
  private isDirectory(path: string): boolean {
    return this.directories.has(path);
  }

  /**
   * Build the mock FileSystem layer
   */
  build(): Layer.Layer<FileSystem.FileSystem | Path.Path> {
    const mockFileSystem: FileSystem.FileSystem = {
      readFileString: (path: string) => {
        if (this.readErrors.has(path)) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "Unknown",
              module: "FileSystem",
              method: "readFileString",
              pathOrDescriptor: path,
              description: this.readErrors.get(path)!.message,
            }),
          );
        }

        const content = this.files.get(path);
        if (content === undefined) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "NotFound",
              module: "FileSystem",
              method: "readFileString",
              pathOrDescriptor: path,
              description: `File not found: ${path}`,
            }),
          );
        }

        if (content instanceof Error) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "Unknown",
              module: "FileSystem",
              method: "readFileString",
              pathOrDescriptor: path,
              description: content.message,
            }),
          );
        }

        return Effect.succeed(content);
      },

      writeFileString: (path: string, content: string) => {
        if (this.writeErrors.has(path)) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "Unknown",
              module: "FileSystem",
              method: "writeFileString",
              pathOrDescriptor: path,
              description: this.writeErrors.get(path)!.message,
            }),
          );
        }

        this.files.set(path, content);
        this.addParentDirectories(path);
        return Effect.succeed(undefined);
      },

      exists: (path: string) => {
        return Effect.succeed(this.pathExists(path));
      },

      stat: (path: string) => {
        if (this.statErrors.has(path)) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "Unknown",
              module: "FileSystem",
              method: "stat",
              pathOrDescriptor: path,
              description: this.statErrors.get(path)!.message,
            }),
          );
        }

        if (!this.pathExists(path)) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "NotFound",
              module: "FileSystem",
              method: "stat",
              pathOrDescriptor: path,
              description: `Path not found: ${path}`,
            }),
          );
        }

        const type = this.isFile(path) ? "File" : "Directory";
        return Effect.succeed({
          type,
          mtime: Option.some(new Date()),
          atime: Option.some(new Date()),
          birthtime: Option.some(new Date()),
          dev: 0,
          ino: Option.some(0),
          mode: 0o644,
          nlink: Option.some(1),
          uid: Option.some(0),
          gid: Option.some(0),
          rdev: Option.some(0),
          size: this.isFile(path)
            ? FileSystem.Size(BigInt((this.files.get(path) as string).length))
            : FileSystem.Size(BigInt(0)),
          blksize: Option.some(FileSystem.Size(BigInt(4096))),
          blocks: Option.some(1),
        } as FileSystem.File.Info);
      },

      readDirectory: (path: string) => {
        if (!this.isDirectory(path)) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "NotFound",
              module: "FileSystem",
              method: "readDirectory",
              pathOrDescriptor: path,
              description: `Directory not found: ${path}`,
            }),
          );
        }

        return Effect.succeed(this.getDirectoryEntries(path));
      },

      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      makeDirectory: (path: string, _opts?: { recursive?: boolean }) => {
        this.directories.add(path);
        this.addParentDirectories(path);
        return Effect.succeed(undefined);
      },

      // Stub implementations for other FileSystem methods
      /* v8 ignore start */
      access: () => Effect.succeed(undefined),
      chmod: () => Effect.succeed(undefined),
      chown: () => Effect.succeed(undefined),
      copy: () => Effect.succeed(undefined),
      copyFile: () => Effect.succeed(undefined),
      link: () => Effect.succeed(undefined),
      makeTempDirectory: () => Effect.succeed("/tmp/mock"),
      makeTempDirectoryScoped: () => Effect.succeed("/tmp/mock"),
      makeTempFile: () => Effect.succeed("/tmp/mock-file"),
      makeTempFileScoped: () => Effect.succeed("/tmp/mock-file"),
      open: () =>
        Effect.fail(
          new PlatformError.SystemError({
            reason: "Unknown",
            module: "FileSystem",
            method: "open",
            pathOrDescriptor: "mock",
            description: "Not implemented in mock",
          }),
        ),
      readFile: (path: string) => {
        const content = this.files.get(path);
        if (content === undefined || content instanceof Error) {
          return Effect.fail(
            new PlatformError.SystemError({
              reason: "NotFound",
              module: "FileSystem",
              method: "readFile",
              pathOrDescriptor: path,
              description: `File not found: ${path}`,
            }),
          );
        }
        return Effect.succeed(new TextEncoder().encode(content));
      },
      readLink: () => Effect.succeed(""),
      realPath: (path: string) => Effect.succeed(path),
      remove: (path: string) => {
        this.files.delete(path);
        this.directories.delete(path);
        return Effect.succeed(undefined);
      },
      rename: () => Effect.succeed(undefined),
      sink: () =>
        Effect.fail(
          new PlatformError.SystemError({
            reason: "Unknown",
            module: "FileSystem",
            method: "sink",
            pathOrDescriptor: "mock",
            description: "Not implemented in mock",
          }),
        ),
      stream: () =>
        Effect.fail(
          new PlatformError.SystemError({
            reason: "Unknown",
            module: "FileSystem",
            method: "stream",
            pathOrDescriptor: "mock",
            description: "Not implemented in mock",
          }),
        ),
      symlink: () => Effect.succeed(undefined),
      truncate: () => Effect.succeed(undefined),
      utimes: () => Effect.succeed(undefined),
      watch: () =>
        Effect.fail(
          new PlatformError.SystemError({
            reason: "Unknown",
            module: "FileSystem",
            method: "watch",
            pathOrDescriptor: "mock",
            description: "Not implemented in mock",
          }),
        ),
      writeFile: (path: string, data: Uint8Array) => {
        this.files.set(path, new TextDecoder().decode(data));
        return Effect.succeed(undefined);
      },
      /* v8 ignore stop */
    } as FileSystem.FileSystem;

    // Create a simple Path implementation
    // We use `as unknown as Path.Path` to bypass TypeId requirements
    // since this is just for testing purposes
    const mockPath = {
      [Path.TypeId]: Path.TypeId,
      sep: "/",
      basename: (filePath: string, suffix?: string) => {
        const base = filePath.split("/").pop() || "";
        if (suffix && base.endsWith(suffix)) {
          return base.slice(0, -suffix.length);
        }
        return base;
      },
      dirname: (filePath: string) => {
        const parts = filePath.split("/");
        parts.pop();
        return parts.join("/") || "/";
      },
      extname: (filePath: string) => {
        const base = filePath.split("/").pop() || "";
        const dotIndex = base.lastIndexOf(".");
        return dotIndex > 0 ? base.slice(dotIndex) : "";
      },
      format: (pathObject: Partial<Path.Path.Parsed>) => {
        return `${pathObject.dir || ""}/${pathObject.base || pathObject.name || ""}${pathObject.ext || ""}`;
      },
      fromFileUrl: (url: URL) => Effect.succeed(url.pathname),
      isAbsolute: (filePath: string) => filePath.startsWith("/"),
      join: (...paths: readonly string[]) =>
        paths.join("/").replace(/\/+/g, "/"),
      normalize: (filePath: string) => filePath.replace(/\/+/g, "/"),
      parse: (filePath: string) => ({
        root: filePath.startsWith("/") ? "/" : "",
        dir: filePath.split("/").slice(0, -1).join("/"),
        base: filePath.split("/").pop() || "",
        ext: (() => {
          const base = filePath.split("/").pop() || "";
          const dotIndex = base.lastIndexOf(".");
          return dotIndex > 0 ? base.slice(dotIndex) : "";
        })(),
        name: filePath.split("/").pop()?.split(".")[0] || "",
      }),
      relative: (from: string, to: string) => to.replace(from, ""),
      resolve: (...paths: readonly string[]) =>
        paths.join("/").replace(/\/+/g, "/"),
      toFileUrl: (filePath: string) =>
        Effect.succeed(new URL(`file://${filePath}`)),
      toNamespacedPath: (filePath: string) => filePath,
    } as Path.Path;

    return Layer.succeed(FileSystem.FileSystem, mockFileSystem).pipe(
      Layer.merge(Layer.succeed(Path.Path, mockPath)),
    );
  }

  /**
   * Get the current file contents (useful for assertions after writes)
   */
  getFile(path: string): string | undefined {
    const content = this.files.get(path);
    return content instanceof Error ? undefined : content;
  }

  /**
   * Get all files (useful for debugging)
   */
  getAllFiles(): Map<string, MockResult<string>> {
    return new Map(this.files);
  }
}

// =============================================================================
// Test Utilities with Automatic Layer Provision
// =============================================================================

/**
 * Services that are automatically provided to all `it.effect` tests.
 */
export type TestContentServices = FileSystem.FileSystem | Path.Path;

/**
 * Type for effect test functions that accept TestContentServices as dependencies.
 */
type ContentEffectTestFn = <A, E>(
  name: string,
  fn: () => Effect.Effect<A, E, TestContentServices>,
  timeout?: number,
) => void;

/**
 * Creates a test `it` wrapper that provides a mock FileSystem layer.
 *
 * @param mockFs - The MockFileSystem instance to use for tests
 * @returns A wrapped `it` with `it.effect` that provides the mock FileSystem
 *
 * @example
 * ```ts
 * const mockFs = new MockFileSystem()
 *   .addFile("/test/file.mdx", "# Test");
 *
 * const { it } = createContentTestUtils(mockFs);
 *
 * it.effect("reads a file", () =>
 *   Effect.gen(function* () {
 *     const fs = yield* FileSystem.FileSystem;
 *     const content = yield* fs.readFileString("/test/file.mdx");
 *     expect(content).toBe("# Test");
 *   })
 * );
 * ```
 */
export function createContentTestUtils(mockFs: MockFileSystem) {
  const mockLayer = mockFs.build();

  const wrapEffectTest =
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    (original: any): ContentEffectTestFn =>
      (name, fn, timeout) => {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call, @typescript-eslint/no-unsafe-return
        return original(
          name,
          () => fn().pipe(Effect.provide(mockLayer)),
          timeout,
        );
      };

  return {
    it: Object.assign(
      // Base callable function for regular tests
      ((name: string, fn: () => void) => vitestIt(name, fn)) as typeof vitestIt,
      {
        // Spread all properties from vitestIt (skip, only, etc.)
        ...vitestIt,
        // Override effect with our wrapped version
        effect: Object.assign(wrapEffectTest(vitestIt.effect), {
          skip: wrapEffectTest(vitestIt.effect.skip),
          only: wrapEffectTest(vitestIt.effect.only),
          fails: wrapEffectTest(vitestIt.effect.fails),
          skipIf: (condition: unknown) =>
            wrapEffectTest(vitestIt.effect.skipIf(condition)),
          runIf: (condition: unknown) =>
            wrapEffectTest(vitestIt.effect.runIf(condition)),
        }),
      },
    ),
    mockFs,
    mockLayer,
  };
}
