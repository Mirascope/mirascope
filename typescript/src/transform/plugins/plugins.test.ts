/**
 * Tests for build system plugins.
 */

import * as esbuild from "esbuild";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { describe, it, expect, beforeAll, afterAll } from "vitest";

import { mirascope as esbuildPlugin } from "./esbuild";
import { mirascope as vitePlugin } from "./vite";

describe("esbuildPlugin", () => {
  it("creates plugin with correct name", () => {
    const plugin = esbuildPlugin();

    expect(plugin.name).toBe("mirascope");
    expect(typeof plugin.setup).toBe("function");
  });

  it("accepts custom filter pattern", () => {
    const plugin = esbuildPlugin({
      filter: /\.mts$/,
    });

    expect(plugin.name).toBe("mirascope");
  });

  it("accepts custom tsconfig path", () => {
    const plugin = esbuildPlugin({
      tsconfig: "./custom-tsconfig.json",
    });

    expect(plugin.name).toBe("mirascope");
  });

  it("accepts custom compiler options", () => {
    const plugin = esbuildPlugin({
      compilerOptions: {
        strict: true,
      },
    });

    expect(plugin.name).toBe("mirascope");
  });
});

describe("vitePlugin", () => {
  it("returns array with pre-config and typescript plugins", () => {
    const plugins = vitePlugin();

    expect(plugins).toHaveLength(2);
    expect(plugins[0]!.name).toBe("mirascope:pre");
    expect(plugins[0]!.enforce).toBe("pre");
  });

  it("accepts custom include/exclude patterns", () => {
    const plugins = vitePlugin({
      include: /\.mts$/,
      exclude: /test/,
    });

    expect(plugins).toHaveLength(2);
  });

  it("accepts custom typescript options", () => {
    const plugins = vitePlugin({
      typescript: {
        declaration: true,
      },
    });

    expect(plugins).toHaveLength(2);
  });

  it("pre-config plugin returns esbuild config", () => {
    const plugins = vitePlugin();
    const prePlugin = plugins[0]!;

    // The config hook should return esbuild settings
    const configFn = prePlugin.config as () => { esbuild: object };
    const config = configFn();

    expect(config).toHaveProperty("esbuild");
    expect(config.esbuild).toHaveProperty("include");
    expect(config.esbuild).toHaveProperty("exclude");
  });

  it("accepts additional transformers", () => {
    // Mock transformer - use a simple function that returns the source file as-is
    const mockTransformer = () => (sf: import("typescript").SourceFile) => sf;

    const plugins = vitePlugin({
      additionalTransformers: {
        before: [mockTransformer],
        after: [mockTransformer],
      },
    });

    expect(plugins).toHaveLength(2);
  });
});

describe("esbuild error handling", () => {
  it("throws on invalid tsconfig.json", async () => {
    const tempDir = await fs.mkdtemp(
      path.join(os.tmpdir(), "mirascope-invalid-"),
    );

    // Create an invalid tsconfig.json
    await fs.writeFile(path.join(tempDir, "tsconfig.json"), "{ invalid json }");

    // Create a test file
    await fs.writeFile(path.join(tempDir, "test.ts"), "export const x = 1;");

    const plugin = esbuildPlugin({
      tsconfig: path.join(tempDir, "tsconfig.json"),
    });

    await expect(
      esbuild.build({
        entryPoints: [path.join(tempDir, "test.ts")],
        bundle: false,
        write: false,
        plugins: [plugin],
      }),
    ).rejects.toThrow("Error reading tsconfig.json");

    await fs.rm(tempDir, { recursive: true });
  });
});

describe("esbuild integration", () => {
  let tempDir: string;

  beforeAll(async () => {
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "mirascope-test-"));

    // Create test file with defineTool
    await fs.writeFile(
      path.join(tempDir, "tool.ts"),
      `
export interface ToolArgs {
  city: string;
  units?: string;
}

export const defineTool = <T>(opts: {
  name: string;
  description: string;
  tool: (args: T) => unknown;
  __schema?: object;
}) => opts;

export const getWeather = defineTool<ToolArgs>({
  name: 'get_weather',
  description: 'Get weather for a city',
  tool: ({ city }) => ({ temp: 72, city }),
});
      `.trim(),
    );

    // Create minimal tsconfig
    await fs.writeFile(
      path.join(tempDir, "tsconfig.json"),
      JSON.stringify({
        compilerOptions: {
          target: "ES2022",
          module: "ESNext",
          moduleResolution: "bundler",
          strict: true,
        },
      }),
    );
  });

  afterAll(async () => {
    await fs.rm(tempDir, { recursive: true });
  });

  it("transforms defineTool calls and injects __schema", async () => {
    const result = await esbuild.build({
      entryPoints: [path.join(tempDir, "tool.ts")],
      bundle: false,
      write: false,
      plugins: [
        esbuildPlugin({ tsconfig: path.join(tempDir, "tsconfig.json") }),
      ],
    });

    const output = result.outputFiles[0]!.text;
    expect(output).toContain("__schema");
    expect(output).toContain("type:");
    expect(output).toContain("object");
    expect(output).toContain("city");
    expect(output).toContain("properties");
  });

  it("skips files without defineTool calls", async () => {
    // Create a file without defineTool
    await fs.writeFile(
      path.join(tempDir, "no-tool.ts"),
      `
export const hello = () => 'world';
      `.trim(),
    );

    const result = await esbuild.build({
      entryPoints: [path.join(tempDir, "no-tool.ts")],
      bundle: false,
      write: false,
      plugins: [
        esbuildPlugin({ tsconfig: path.join(tempDir, "tsconfig.json") }),
      ],
    });

    const output = result.outputFiles[0]!.text;
    expect(output).not.toContain("__schema");
    expect(output).toContain("hello");
  });

  it("skips tsx files without defineTool calls", async () => {
    // Create a tsx file without defineTool
    await fs.writeFile(
      path.join(tempDir, "no-tool.tsx"),
      `
export const Component = () => <div>Hello</div>;
      `.trim(),
    );

    const result = await esbuild.build({
      entryPoints: [path.join(tempDir, "no-tool.tsx")],
      bundle: false,
      write: false,
      jsx: "transform",
      plugins: [
        esbuildPlugin({ tsconfig: path.join(tempDir, "tsconfig.json") }),
      ],
    });

    const output = result.outputFiles[0]!.text;
    expect(output).not.toContain("__schema");
    expect(output).toContain("Component");
  });

  it("handles missing tsconfig gracefully", async () => {
    const result = await esbuild.build({
      entryPoints: [path.join(tempDir, "tool.ts")],
      bundle: false,
      write: false,
      plugins: [
        esbuildPlugin({ tsconfig: path.join(tempDir, "nonexistent.json") }),
      ],
    });

    // Should still work with default config
    const output = result.outputFiles[0]!.text;
    expect(output).toContain("__schema");
  });

  it("handles tsx files", async () => {
    // Create a tsx file with defineTool
    // Note: In TSX, generics need trailing comma to disambiguate from JSX
    await fs.writeFile(
      path.join(tempDir, "component.tsx"),
      `
export const defineTool = <T,>(opts: {
  name: string;
  description: string;
  tool: (args: T) => unknown;
  __schema?: object;
}) => opts;

export const searchTool = defineTool<{ query: string }>({
  name: 'search',
  description: 'Search for something',
  tool: ({ query }) => ({ results: [query] }),
});

export const Component = () => <div>Hello</div>;
      `.trim(),
    );

    const result = await esbuild.build({
      entryPoints: [path.join(tempDir, "component.tsx")],
      bundle: false,
      write: false,
      jsx: "transform",
      plugins: [
        esbuildPlugin({ tsconfig: path.join(tempDir, "tsconfig.json") }),
      ],
    });

    const output = result.outputFiles[0]!.text;
    expect(output).toContain("__schema");
    expect(output).toContain("query");
  });
});
