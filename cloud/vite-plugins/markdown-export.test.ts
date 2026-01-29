/**
 * Tests for the markdown export Vite plugin.
 *
 * These tests verify that:
 * 1. The MarkdownExporter generates correct markdown files
 * 2. The dev server middleware serves markdown dynamically
 * 3. Markdown content has proper frontmatter and absolute URLs
 * 4. E2E: Dev server serves markdown files via HTTP
 */

import { type ChildProcess, spawn } from "node:child_process";
import fs from "node:fs/promises";
import path from "node:path";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

import ContentProcessor from "../app/lib/content/content-processor";
import { MarkdownExporter, viteMarkdownExport } from "./markdown-export";

// Test content directory
const contentDir = path.resolve(process.cwd(), "../content");

// Create a shared ContentProcessor for tests
const processor = new ContentProcessor({
  contentDir,
  verbose: false,
});

describe("MarkdownExporter", () => {
  beforeAll(async () => {
    // Process content before running tests
    await processor.processAllContent();
  });

  it("should generate markdown with frontmatter for a docs page", async () => {
    const outputDir = path.join(
      process.cwd(),
      "../.test-output/markdown-export",
    );

    // Clean up any previous test output
    await fs.rm(outputDir, { recursive: true, force: true });
    await fs.mkdir(outputDir, { recursive: true });

    const exporter = new MarkdownExporter({
      processor,
      outputDir,
      verbose: false,
    });

    const results = await exporter.generate();

    // Should have processed some content
    expect(results.success).toBeGreaterThan(0);
    expect(results.failed).toBe(0);

    // Check that contributing.md was generated
    const contributingPath = path.join(outputDir, "docs/contributing.md");
    const contributingExists = await fs
      .access(contributingPath)
      .then(() => true)
      .catch(() => false);
    expect(contributingExists).toBe(true);

    // Read and validate the content
    const content = await fs.readFile(contributingPath, "utf-8");

    // Should have YAML frontmatter
    expect(content).toMatch(/^---\n/);
    expect(content).toContain('title: "Contributing"');
    expect(content).toContain('description: "How to contribute to Mirascope"');
    expect(content).toContain('url: "https://mirascope.com/docs/contributing"');
    expect(content).toMatch(/---\n\n/);

    // Should contain the actual content
    expect(content).toContain("# Contributing");
    expect(content).toContain(
      "Thank you for your interest in contributing to Mirascope!",
    );

    // Should convert relative links to absolute URLs
    expect(content).toContain("https://mirascope.com/discord-invite");

    // Clean up
    await fs.rm(outputDir, { recursive: true, force: true });
  });

  it("should require a processor instance", () => {
    expect(
      () =>
        new MarkdownExporter({
          processor: undefined as unknown as ContentProcessor,
          outputDir: "/tmp",
        }),
    ).toThrow("processor option is required");
  });
});

describe("viteMarkdownExport plugin", () => {
  beforeAll(async () => {
    // Process content before running tests
    await processor.processAllContent();
  });

  it("should create a valid Vite plugin", () => {
    const plugin = viteMarkdownExport({ processor });

    expect(plugin.name).toBe("vite-plugin-markdown-export");
    expect(plugin.enforce).toBe("post");
    expect(plugin.configureServer).toBeDefined();
    expect(plugin.buildApp).toBeDefined();
  });

  it("should handle middleware for .md requests", async () => {
    const plugin = viteMarkdownExport({ processor, verbose: false });

    // Create a mock server middlewares array
    type MiddlewareFunction = (
      req: { url?: string; headers: { host: string } },
      res: {
        setHeader: (key: string, value: string) => void;
        statusCode: number;
        end: (content: string) => void;
      },
      next: (error?: unknown) => void,
    ) => Promise<void>;

    const middlewares: MiddlewareFunction[] = [];
    const mockServer = {
      middlewares: {
        use: (fn: MiddlewareFunction) => {
          middlewares.push(fn);
        },
      },
    };

    // Call configureServer to register middleware
    if (plugin.configureServer) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (plugin.configureServer as (server: unknown) => void)(mockServer);
    }

    expect(middlewares.length).toBe(1);

    // Test that middleware serves markdown for .md URLs
    let responseContent = "";
    let responseContentType = "";
    let nextCalled = false;

    const mockReq = {
      url: "/docs/contributing.md",
      headers: { host: "localhost:3000" },
    };

    const mockRes = {
      setHeader: (key: string, value: string) => {
        if (key === "Content-Type") {
          responseContentType = value;
        }
      },
      statusCode: 0,
      end: (content: string) => {
        responseContent = content;
      },
    };

    const mockNext = () => {
      nextCalled = true;
    };

    await middlewares[0](mockReq, mockRes, mockNext);

    // Should have served markdown content
    expect(nextCalled).toBe(false);
    expect(mockRes.statusCode).toBe(200);
    expect(responseContentType).toBe("text/markdown; charset=utf-8");
    expect(responseContent).toContain("---");
    expect(responseContent).toContain('title: "Contributing"');
    expect(responseContent).toContain("# Contributing");
  });

  it("should call next for non-.md URLs", async () => {
    const plugin = viteMarkdownExport({ processor, verbose: false });

    type MiddlewareFunction = (
      req: { url?: string; headers: { host: string } },
      res: unknown,
      next: () => void,
    ) => Promise<void>;

    const middlewares: MiddlewareFunction[] = [];
    const mockServer = {
      middlewares: {
        use: (fn: MiddlewareFunction) => {
          middlewares.push(fn);
        },
      },
    };

    if (plugin.configureServer) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (plugin.configureServer as (server: unknown) => void)(mockServer);
    }

    let nextCalled = false;

    await middlewares[0](
      { url: "/docs/contributing", headers: { host: "localhost:3000" } },
      {},
      () => {
        nextCalled = true;
      },
    );

    expect(nextCalled).toBe(true);
  });

  it("should call next for non-existent routes", async () => {
    const plugin = viteMarkdownExport({ processor, verbose: false });

    type MiddlewareFunction = (
      req: { url?: string; headers: { host: string } },
      res: unknown,
      next: () => void,
    ) => Promise<void>;

    const middlewares: MiddlewareFunction[] = [];
    const mockServer = {
      middlewares: {
        use: (fn: MiddlewareFunction) => {
          middlewares.push(fn);
        },
      },
    };

    if (plugin.configureServer) {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      (plugin.configureServer as (server: unknown) => void)(mockServer);
    }

    let nextCalled = false;

    await middlewares[0](
      { url: "/nonexistent/page.md", headers: { host: "localhost:3000" } },
      {},
      () => {
        nextCalled = true;
      },
    );

    expect(nextCalled).toBe(true);
  });
});

describe("Markdown content transformation", () => {
  beforeAll(async () => {
    await processor.processAllContent();
  });

  it("should convert relative links to absolute URLs", async () => {
    const outputDir = path.join(
      process.cwd(),
      "../.test-output/markdown-export-links",
    );

    await fs.rm(outputDir, { recursive: true, force: true });
    await fs.mkdir(outputDir, { recursive: true });

    const exporter = new MarkdownExporter({
      processor,
      outputDir,
      verbose: false,
    });

    await exporter.generate();

    // Check a file that has relative links
    const contributingPath = path.join(outputDir, "docs/contributing.md");
    const content = await fs.readFile(contributingPath, "utf-8");

    // The contributing page links to /discord-invite
    // Should be converted to absolute URL
    expect(content).not.toContain("](/discord-invite)");
    expect(content).toContain("](https://mirascope.com/discord-invite)");

    await fs.rm(outputDir, { recursive: true, force: true });
  });
});

/**
 * E2E test that actually starts the dev server and makes HTTP requests.
 *
 * This test:
 * 1. Spawns the Vite dev server as a child process
 * 2. Waits for the server to be ready
 * 3. Makes HTTP requests to fetch markdown files
 * 4. Validates the response content and headers
 * 5. Cleans up by killing the server process
 */
describe("E2E: Dev server markdown serving", () => {
  let serverProcess: ChildProcess | null = null;
  const PORT = 3099; // Use a unique port to avoid conflicts
  const BASE_URL = `http://localhost:${PORT}`;

  /**
   * Wait for the server to be ready by polling the health endpoint.
   */
  async function waitForServer(
    maxAttempts = 30,
    delayMs = 1000,
  ): Promise<void> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(`${BASE_URL}/`);
        if (response.ok || response.status === 200) {
          return;
        }
      } catch {
        // Server not ready yet, continue polling
      }
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
    throw new Error(
      `Server did not become ready after ${maxAttempts} attempts`,
    );
  }

  beforeAll(async () => {
    // Start the dev server
    serverProcess = spawn("bun", ["run", "dev", "--port", String(PORT)], {
      cwd: process.cwd(),
      env: {
        ...process.env,
        CLOUDFLARE_ENV: "local",
        NODE_ENV: "development",
      },
      stdio: ["ignore", "pipe", "pipe"],
      detached: false,
    });

    // Log server output for debugging
    serverProcess.stdout?.on("data", (data: Buffer) => {
      const output = data.toString();
      if (process.env.DEBUG) {
        console.log(`[dev-server stdout] ${output}`);
      }
    });

    serverProcess.stderr?.on("data", (data: Buffer) => {
      const output = data.toString();
      if (process.env.DEBUG) {
        console.error(`[dev-server stderr] ${output}`);
      }
    });

    // Wait for server to be ready
    await waitForServer();
  }, 60000); // 60s timeout for server startup

  afterAll(async () => {
    // Kill the server process
    if (serverProcess) {
      serverProcess.kill("SIGTERM");
      // Wait a bit for graceful shutdown
      await new Promise((resolve) => setTimeout(resolve, 1000));
      // Force kill if still running
      if (!serverProcess.killed) {
        serverProcess.kill("SIGKILL");
      }
      serverProcess = null;
    }
  });

  it("should serve markdown for a docs page via HTTP", async () => {
    const response = await fetch(`${BASE_URL}/docs/contributing.md`);

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe(
      "text/markdown; charset=utf-8",
    );

    const content = await response.text();

    // Verify frontmatter
    expect(content).toMatch(/^---\n/);
    expect(content).toContain('title: "Contributing"');
    expect(content).toContain('description: "How to contribute to Mirascope"');
    expect(content).toContain('url: "https://mirascope.com/docs/contributing"');

    // Verify content
    expect(content).toContain("# Contributing");
    expect(content).toContain(
      "Thank you for your interest in contributing to Mirascope!",
    );

    // Verify absolute URLs
    expect(content).toContain("https://mirascope.com/discord-invite");
    expect(content).not.toContain("](/discord-invite)");
  });

  it("should serve markdown for a blog page via HTTP", async () => {
    // First, get a list of blog posts from the content processor
    const blogProcessor = new ContentProcessor({
      contentDir: path.resolve(process.cwd(), "../content"),
      verbose: false,
    });
    await blogProcessor.processAllContent();
    const metadata = blogProcessor.getMetadata();

    // Skip if no blog posts
    if (metadata.blog.length === 0) {
      return;
    }

    const firstBlogPost = metadata.blog[0];
    const response = await fetch(`${BASE_URL}${firstBlogPost.route}.md`);

    expect(response.status).toBe(200);
    expect(response.headers.get("content-type")).toBe(
      "text/markdown; charset=utf-8",
    );

    const content = await response.text();

    // Verify frontmatter exists
    expect(content).toMatch(/^---\n/);
    expect(content).toContain(`title: "${firstBlogPost.title}"`);
    expect(content).toContain(
      `url: "https://mirascope.com${firstBlogPost.route}"`,
    );
  });

  it("should return 404 for non-existent markdown routes", async () => {
    const response = await fetch(`${BASE_URL}/nonexistent/page.md`);

    // The middleware calls next() for non-existent routes,
    // so Vite will handle it and likely return a 404 or the SPA fallback
    expect(response.status).not.toBe(200);
  });

  it("should not intercept non-.md requests", async () => {
    const response = await fetch(`${BASE_URL}/docs/contributing`);

    // Should return HTML, not markdown
    const contentType = response.headers.get("content-type") ?? "";
    expect(contentType).not.toContain("text/markdown");
  });
});
