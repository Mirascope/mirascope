import { describe, it, expect, vi, beforeEach } from "vitest";
import type { LoaderFnContext, AnyRoute } from "@tanstack/react-router";
import {
  getAllBlogMeta,
  getAllDocsMeta,
} from "@/app/lib/content/virtual-module";
import {
  blogPostContentLoader,
  docsContentLoader,
} from "@/app/lib/content/content-loader";
import { createProcessedMDX } from "@/app/lib/content/mdx-compile";
import type { ProcessedMDX } from "@/app/lib/mdx/types";

// Mock the virtual module
vi.mock("virtual:content-meta", () => ({
  blogMetadata: [
    {
      slug: "test-post",
      title: "Test Post",
      description: "A test blog post",
      date: "2025-01-01",
      author: "Test Author",
      readTime: "5 min read",
      lastUpdated: "",
      path: "blog/test-post",
      type: "blog" as const,
      route: "/blog/test-post",
    },
    {
      slug: "another-post",
      title: "Another Post",
      description: "Another test blog post",
      date: "2025-01-02",
      author: "Test Author",
      readTime: "3 min read",
      lastUpdated: "",
      path: "blog/another-post",
      type: "blog" as const,
      route: "/blog/another-post",
    },
  ],
  docsMetadata: [
    {
      label: "Test Doc",
      path: "docs/v1/learn/test-doc",
      routePath: "/docs/v1/learn/test-doc",
      slug: "test-doc",
      type: "docs" as const,
      searchWeight: 1.0,
    },
    {
      label: "Another Doc",
      path: "docs/v1/learn/another-doc",
      routePath: "/docs/v1/learn/another-doc",
      slug: "another-doc",
      type: "docs" as const,
      searchWeight: 1.0,
    },
    {
      label: "Index Page",
      path: "docs/v1/index",
      routePath: "/docs/v1",
      slug: "index",
      type: "docs" as const,
      searchWeight: 1.0,
    },
    {
      label: "Non-Versioned Doc",
      path: "docs/learn/non-versioned-doc",
      routePath: "/docs/learn/non-versioned-doc",
      slug: "non-versioned-doc",
      type: "docs" as const,
      searchWeight: 1.0,
    },
    {
      label: "Non-Versioned Index",
      path: "docs/index",
      routePath: "/docs",
      slug: "index",
      type: "docs" as const,
      searchWeight: 1.0,
    },
  ],
}));

// Test MDX content fixture
const testMDXContent = "# Test Content\n\nThis is test content.";

/**
 * Helper function to create a test module map.
 * This avoids needing eslint-disable comments for 'any' types throughout the tests.
 */
function createTestModuleMap(): Map<
  string,
  () => Promise<{ mdx: ProcessedMDX }>
> {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  return new Map<string, () => Promise<{ mdx: any }>>();
}

describe("blogPostContentLoader", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function createMockContext(
    slug: string,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ): LoaderFnContext<any, AnyRoute, any, { slug: string }> {
    return {
      params: { slug },
      abortController: new AbortController(),
      preload: false,
      deps: {},
      context: {},
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
      location: {} as any,
      navigate: async () => {},
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
      parentMatchPromise: Promise.resolve({} as any),
      cause: "enter" as const,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
      route: {} as any,
    };
  }

  it("should return undefined for non-existent blog post (fails allow list check)", async () => {
    const loader = blogPostContentLoader();
    const context = createMockContext("non-existent-post");
    const result = await loader(context);

    // Should return undefined because it's not in the allow list
    expect(result).toBeUndefined();
  });

  it("should successfully load a valid blog post", async () => {
    // Set up a custom module map with test content
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("test-post", () =>
      Promise.resolve({
        mdx: createProcessedMDX(testMDXContent, {
          title: "Test Post",
          description: "A test blog post",
          date: "2025-01-01",
          author: "Test Author",
        }),
      }),
    );

    // Pass custom module map for testing
    const loader = blogPostContentLoader(customModuleMap);
    const context = createMockContext("test-post");
    const result = await loader(context);

    expect(result).toBeDefined();
    expect(result?.meta.slug).toBe("test-post");
    expect(result?.meta.title).toBe("Test Post");
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx).toBeDefined();
    expect(result?.mdx.content).toBe(testMDXContent);
  });

  describe("appsec path traversal attacks", () => {
    it("should reject path traversal with ../", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("../../../etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with ..\\", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("..\\..\\..\\windows\\system32");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with encoded ../", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext(
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
      );
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with double-encoded ../", async () => {
      const loader = blogPostContentLoader();
      // Double encoding: %25 = %, so %252e = %2e which decodes to .
      const context = createMockContext(
        "%252e%252e%252f%252e%252e%252fetc%252fpasswd",
      );
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with mixed slashes", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("..\\../etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject absolute paths", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("/etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with forward slashes", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("blog/../etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with backslashes", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("blog\\..\\etc\\passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec invalid characters", () => {
    it("should reject slugs with null bytes", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("test-post\0");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject slugs with special shell characters", async () => {
      const loader = blogPostContentLoader();
      const maliciousSlugs = [
        "test-post; rm -rf /",
        "test-post | cat /etc/passwd",
        "test-post && cat /etc/passwd",
        "test-post $(cat /etc/passwd)",
        "test-post `cat /etc/passwd`",
      ];

      for (const slug of maliciousSlugs) {
        const context = createMockContext(slug);
        const result = await loader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should reject slugs with unicode characters that could be dangerous", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("test-post\u202e");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec allow list validation", () => {
    it("should reject slugs not in the allow list", async () => {
      const loader = blogPostContentLoader();
      const invalidSlugs = [
        "random-slug",
        "prompt-testing", // not in our mock allow list
        "fake-post",
        "",
      ];

      for (const slug of invalidSlugs) {
        const context = createMockContext(slug);
        const result = await loader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should verify allow list is properly constructed", () => {
      const meta = getAllBlogMeta();
      const validSlugSet = new Set(meta.map((post) => post.slug));

      // Verify our mock data is in the set
      expect(validSlugSet.has("test-post")).toBe(true);
      expect(validSlugSet.has("another-post")).toBe(true);
      expect(validSlugSet.size).toBe(2);
    });
  });

  describe("edge cases", () => {
    it("should handle empty slug", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle very long slug", async () => {
      const loader = blogPostContentLoader();
      const longSlug = "a".repeat(1000);
      const context = createMockContext(longSlug);
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle slug with only special characters", async () => {
      const loader = blogPostContentLoader();
      const context = createMockContext("!!!@@@###$$$");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });
});

describe("docsContentLoader", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function createMockContext(
    splat: string | undefined,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ): LoaderFnContext<any, AnyRoute, any, { _splat?: string }> {
    return {
      params: { _splat: splat },
      abortController: new AbortController(),
      preload: false,
      deps: {},
      context: {},
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
      location: {} as any,
      navigate: async () => {},
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
      parentMatchPromise: Promise.resolve({} as any),
      cause: "enter" as const,
      // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-assignment
      route: {} as any,
    };
  }

  it("should return undefined for non-existent doc (fails allow list check)", async () => {
    const loader = docsContentLoader("v1");
    const context = createMockContext("learn/non-existent-doc");
    const result = await loader(context);

    // Should return undefined because it's not in the allow list
    expect(result).toBeUndefined();
  });

  it("should successfully load a valid doc", async () => {
    // Set up a custom module map with test content
    // Note: module map uses 'path' (v1/learn/test-doc), not 'routePath'
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("v1/learn/test-doc", () =>
      Promise.resolve({
        mdx: createProcessedMDX(testMDXContent, {
          title: "Test Doc",
          description: "A test doc",
        }),
      }),
    );

    // Pass custom module map for testing
    const loader = docsContentLoader("v1", customModuleMap);
    const context = createMockContext("learn/test-doc");
    const result = await loader(context);

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Test Doc");
  });

  it("should handle index page (empty _splat)", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("v1/index", () =>
      Promise.resolve({
        mdx: createProcessedMDX(testMDXContent, {
          title: "Index Page",
          description: "Index page",
        }),
      }),
    );

    const loader = docsContentLoader("v1", customModuleMap);
    const context = createMockContext(undefined);
    const result = await loader(context);

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Index Page");
  });

  it("should handle different versions correctly", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("v2/learn/test-doc", () =>
      Promise.resolve({
        mdx: createProcessedMDX(testMDXContent, {
          title: "V2 Doc",
          description: "V2 doc",
        }),
      }),
    );

    // Create a custom loader with v2 version
    // Note: This test verifies version parameter is used correctly in routePath construction
    const loader = docsContentLoader("v2", customModuleMap);
    const context = createMockContext("learn/test-doc");
    const result = await loader(context);

    // Should fail because our mock docInfos only have v1 routes
    // This verifies that version is correctly used in routePath matching
    expect(result).toBeUndefined();
  });

  it("should successfully load a non-versioned doc", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("learn/non-versioned-doc", () =>
      Promise.resolve({
        mdx: createProcessedMDX(testMDXContent, {
          title: "Non-Versioned Doc",
          description: "A non-versioned doc",
        }),
      }),
    );

    // Loader without version parameter
    const loader = docsContentLoader(undefined, customModuleMap);
    const context = createMockContext("learn/non-versioned-doc");
    const result = await loader(context);

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Non-Versioned Doc");
  });

  it("should handle non-versioned index page (empty _splat)", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("index", () =>
      Promise.resolve({
        mdx: createProcessedMDX(testMDXContent, {
          title: "Non-Versioned Index",
          description: "Non-versioned index page",
        }),
      }),
    );

    // Loader without version parameter
    const loader = docsContentLoader(undefined, customModuleMap);
    const context = createMockContext(undefined);
    const result = await loader(context);

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Non-Versioned Index");
  });

  it("should not load versioned docs when version is not specified", async () => {
    // Try to access v1 doc without specifying version
    const loader = docsContentLoader();
    const context = createMockContext("learn/test-doc");
    const result = await loader(context);

    // Should fail because routePath won't match (/docs/learn/test-doc vs /docs/v1/learn/test-doc)
    expect(result).toBeUndefined();
  });

  it("should not load non-versioned docs when version is specified", async () => {
    // Try to access non-versioned doc with v1 version specified
    const loader = docsContentLoader("v1");
    const context = createMockContext("learn/non-versioned-doc");
    const result = await loader(context);

    // Should fail because routePath won't match (/docs/v1/learn/non-versioned-doc vs /docs/learn/non-versioned-doc)
    expect(result).toBeUndefined();
  });

  describe("appsec path traversal attacks", () => {
    // Use empty module map to avoid loading real files during security tests
    const emptyModuleMap = createTestModuleMap();

    it("should reject path traversal with ../", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("../../../etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with ..\\", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("..\\..\\..\\windows\\system32");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with encoded ../", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext(
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
      );
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with double-encoded ../", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      // Double encoding: %25 = %, so %252e = %2e which decodes to .
      const context = createMockContext(
        "%252e%252e%252f%252e%252e%252fetc%252fpasswd",
      );
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with mixed slashes", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("..\\../etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject absolute paths", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("/etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with forward slashes in _splat", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("learn/../etc/passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with backslashes in _splat", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("learn\\..\\etc\\passwd");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec invalid characters", () => {
    // Use empty module map to avoid loading real files during security tests
    const emptyModuleMap = createTestModuleMap();

    it("should reject _splat with null bytes", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("learn/test-doc\0");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject _splat with special shell characters", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const maliciousSplats = [
        "learn/test-doc; rm -rf /",
        "learn/test-doc | cat /etc/passwd",
        "learn/test-doc && cat /etc/passwd",
        "learn/test-doc $(cat /etc/passwd)",
        "learn/test-doc `cat /etc/passwd`",
      ];

      for (const splat of maliciousSplats) {
        const context = createMockContext(splat);
        const result = await loader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should reject _splat with unicode characters that could be dangerous", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("learn/test-doc\u202e");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec allow list validation", () => {
    // Use empty module map to avoid loading real files during security tests
    const emptyModuleMap = createTestModuleMap();

    it("should reject _splat not in the allow list", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const invalidSplats = [
        "random/path",
        "learn/fake-doc", // not in our mock allow list
        "v1/learn/test-doc", // includes version prefix (shouldn't)
        "",
      ];

      for (const splat of invalidSplats) {
        const context = createMockContext(splat);
        const result = await loader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should verify allow list is properly constructed", () => {
      const docInfos = getAllDocsMeta();
      const validPathSet = new Set(docInfos.map((doc) => doc.path));

      // Verify our mock data is in the set (paths with "docs/" prefix)
      expect(validPathSet.has("docs/v1/learn/test-doc")).toBe(true);
      expect(validPathSet.has("docs/v1/learn/another-doc")).toBe(true);
      expect(validPathSet.has("docs/v1/index")).toBe(true);
      expect(validPathSet.has("docs/learn/non-versioned-doc")).toBe(true);
      expect(validPathSet.has("docs/index")).toBe(true);
      expect(validPathSet.size).toBe(5);
    });
  });

  describe("edge cases", () => {
    // Use empty module map to avoid loading real files during security tests
    const emptyModuleMap = createTestModuleMap();

    it("should handle very long _splat", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const longSplat = "a".repeat(1000);
      const context = createMockContext(longSplat);
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle _splat with only special characters", async () => {
      const loader = docsContentLoader("v1", emptyModuleMap);
      const context = createMockContext("!!!@@@###$$$");
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle version mismatch", async () => {
      // Try to access v1 doc with v2 loader
      const loader = docsContentLoader("v2", emptyModuleMap);
      const context = createMockContext("learn/test-doc");
      const result = await loader(context);

      // Should fail because routePath won't match
      expect(result).toBeUndefined();
    });
  });
});
