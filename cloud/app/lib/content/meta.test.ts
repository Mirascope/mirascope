import { describe, it, expect, vi, beforeEach } from "vitest";
import { blogPostContentLoader, getAllBlogMeta } from "./meta";
import type { MDXImporter } from "./meta";
import type { LoaderFnContext, AnyRoute } from "@tanstack/react-router";
import { createProcessedMDX } from "./mdx-compile";

// Mock the virtual module
vi.mock("virtual:content-meta", () => ({
  blogPosts: [
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
}));

// Test MDX content fixture
const testMDXContent = "# Test Content\n\nThis is test content.";

// Create a test MDX importer that returns compiled MDX for known slugs
function createTestImporter(
  slugToContent: Record<
    string,
    { content: string; frontmatter: Record<string, unknown> }
  >,
): MDXImporter {
  return (slug) => {
    const entry = slugToContent[slug];
    if (!entry) {
      return Promise.resolve(undefined);
    }
    return Promise.resolve({
      mdx: createProcessedMDX(entry.content, entry.frontmatter),
    });
  };
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
    const context = createMockContext("non-existent-post");
    const result = await blogPostContentLoader(context);

    // Should return undefined because it's not in the allow list
    expect(result).toBeUndefined();
  });

  it("should successfully load a valid blog post", async () => {
    const testImporter = createTestImporter({
      "test-post": {
        content: testMDXContent,
        frontmatter: {
          title: "Test Post",
          description: "A test blog post",
          date: "2025-01-01",
          author: "Test Author",
        },
      },
    });

    const context = createMockContext("test-post");
    const result = await blogPostContentLoader(context, testImporter);

    expect(result).toBeDefined();
    expect(result?.meta.slug).toBe("test-post");
    expect(result?.meta.title).toBe("Test Post");
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx).toBeDefined();
    expect(result?.mdx.content).toBe(testMDXContent);
  });

  describe("appsec path traversal attacks", () => {
    it("should reject path traversal with ../", async () => {
      const context = createMockContext("../../../etc/passwd");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with ..\\", async () => {
      const context = createMockContext("..\\..\\..\\windows\\system32");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with encoded ../", async () => {
      const context = createMockContext(
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
      );
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with mixed slashes", async () => {
      const context = createMockContext("..\\../etc/passwd");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should reject absolute paths", async () => {
      const context = createMockContext("/etc/passwd");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with forward slashes", async () => {
      const context = createMockContext("blog/../etc/passwd");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with backslashes", async () => {
      const context = createMockContext("blog\\..\\etc\\passwd");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec invalid characters", () => {
    it("should reject slugs with null bytes", async () => {
      const context = createMockContext("test-post\0");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should reject slugs with special shell characters", async () => {
      const maliciousSlugs = [
        "test-post; rm -rf /",
        "test-post | cat /etc/passwd",
        "test-post && cat /etc/passwd",
        "test-post $(cat /etc/passwd)",
        "test-post `cat /etc/passwd`",
      ];

      for (const slug of maliciousSlugs) {
        const context = createMockContext(slug);
        const result = await blogPostContentLoader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should reject slugs with unicode characters that could be dangerous", async () => {
      const context = createMockContext("test-post\u202e");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec allow list validation", () => {
    it("should reject slugs not in the allow list", async () => {
      const invalidSlugs = [
        "random-slug",
        "prompt-testing", // not in our mock allow list
        "fake-post",
        "",
      ];

      for (const slug of invalidSlugs) {
        const context = createMockContext(slug);
        const result = await blogPostContentLoader(context);
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
      const context = createMockContext("");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should handle very long slug", async () => {
      const longSlug = "a".repeat(1000);
      const context = createMockContext(longSlug);
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });

    it("should handle slug with only special characters", async () => {
      const context = createMockContext("!!!@@@###$$$");
      const result = await blogPostContentLoader(context);

      expect(result).toBeUndefined();
    });
  });
});
