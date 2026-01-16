import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  BLOG_MODULE_MAP,
  DOCS_MODULE_MAP,
  POLICY_MODULE_MAP,
  getAllBlogMeta,
  getAllDocsMeta,
  getAllPolicyMeta,
  type VirtualModuleExport,
} from "@/app/lib/content/virtual-module";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import type { PreprocessedMDX } from "@/app/lib/mdx/types";
import type {
  BlogContent,
  Content,
  ContentMeta,
  DocContent,
} from "@/app/lib/content/types";

// Mock TanStack Router
vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn((path: string) => (options: unknown) => ({
    path,
    options,
  })),
  redirect: vi.fn((config: unknown) => {
    const error = new Error("Redirect");
    (error as unknown as { redirect: unknown }).redirect = config;
    throw error;
  }),
  useLoaderData: vi.fn(),
}));

// Mock NotFound component
vi.mock("@/app/components/not-found", () => ({
  NotFound: () => null,
}));

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
      title: "Test Doc",
      description: "A test doc",
      path: "docs/v1/learn/test-doc",
      routePath: "/docs/v1/learn/test-doc",
      slug: "test-doc",
      type: "docs" as const,
      searchWeight: 1.0,
      sectionPath: "docs>v1>learn",
    },
    {
      title: "Another Doc",
      description: "Another test doc",
      path: "docs/v1/learn/another-doc",
      routePath: "/docs/v1/learn/another-doc",
      slug: "another-doc",
      type: "docs" as const,
      searchWeight: 1.0,
      sectionPath: "docs>v1>learn",
    },
    {
      title: "Index Page",
      description: "Index page",
      path: "docs/v1/index",
      routePath: "/docs/v1",
      slug: "index",
      type: "docs" as const,
      searchWeight: 1.0,
      sectionPath: "docs>v1",
    },
    {
      title: "Non-Versioned Doc",
      description: "A non-versioned doc",
      path: "docs/learn/non-versioned-doc",
      routePath: "/docs/learn/non-versioned-doc",
      slug: "non-versioned-doc",
      type: "docs" as const,
      searchWeight: 1.0,
      sectionPath: "docs>learn",
    },
    {
      title: "Non-Versioned Index",
      description: "Non-versioned index page",
      path: "docs/index",
      routePath: "/docs",
      slug: "index",
      type: "docs" as const,
      searchWeight: 1.0,
      sectionPath: "docs",
    },
  ],
  policyMetadata: [],
}));

// Test MDX content fixture
const testMDXContent = "# Test Content\n\nThis is test content.";

/**
 * Helper function to create a test module map.
 */
function createTestModuleMap(): Map<
  string,
  () => Promise<VirtualModuleExport>
> {
  return new Map<string, () => Promise<VirtualModuleExport>>();
}

/**
 * Helper to get the loader from a route config created by createContentRouteConfig.
 */

function getLoader<TMeta extends ContentMeta>(
  routeConfig: ReturnType<typeof createContentRouteConfig<TMeta>>,
) {
  return routeConfig.loader;
}

/**
 * Helper to create a mock loader context.
 */
function createMockContext(params: Record<string, string | undefined>) {
  return {
    params,
    abortController: new AbortController(),
    preload: false,
    deps: {},
    context: {},
    location: {} as unknown,
    navigate: async () => {},
    parentMatchPromise: Promise.resolve({} as unknown),
    cause: "enter" as const,
    route: {} as unknown,
  };
}

// Dummy component for testing - accepts base Content type for flexibility
const DummyComponent = ({ content }: { content: Content }) => {
  void content;
  return null;
};

describe("createContentRouteConfig - blog", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should return undefined for non-existent blog post (fails allow list check)", async () => {
    const route = createContentRouteConfig("/blog/$slug", {
      getMeta: getAllBlogMeta,
      moduleMap: BLOG_MODULE_MAP,
      prefix: "blog",
      component: DummyComponent,
    });
    const loader = getLoader(route);
    const context = createMockContext({ slug: "non-existent-post" });
    const result = await loader(context);

    expect(result).toBeUndefined();
  });

  it("should successfully load a valid blog post", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("test-post", () =>
      Promise.resolve({
        default: {
          content: testMDXContent,
          frontmatter: {
            title: "Test Post",
            description: "A test blog post",
            date: "2025-01-01",
            author: "Test Author",
          },
          tableOfContents: [],
        } satisfies PreprocessedMDX,
      }),
    );

    const route = createContentRouteConfig("/blog/$slug", {
      getMeta: getAllBlogMeta,
      moduleMap: BLOG_MODULE_MAP,
      prefix: "blog",
      component: DummyComponent,
      _testModuleMap: customModuleMap,
    });
    const loader = getLoader(route);
    const context = createMockContext({ slug: "test-post" });
    const result = (await loader(context)) as BlogContent | undefined;

    expect(result).toBeDefined();
    expect(result?.meta.slug).toBe("test-post");
    expect(result?.meta.title).toBe("Test Post");
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx).toBeDefined();
    expect(result?.mdx.content).toBe(testMDXContent);
    expect(result?.mdx.code).toBeDefined();
    expect(typeof result?.mdx.code).toBe("string");
  });

  describe("appsec path traversal attacks", () => {
    it("should reject path traversal with ../", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "../../../etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with ..\\", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({
        slug: "..\\..\\..\\windows\\system32",
      });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with encoded ../", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({
        slug: "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
      });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with double-encoded ../", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({
        slug: "%252e%252e%252f%252e%252e%252fetc%252fpasswd",
      });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with mixed slashes", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "..\\../etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject absolute paths", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "/etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with forward slashes", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "blog/../etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with backslashes", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "blog\\..\\etc\\passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec invalid characters", () => {
    it("should reject slugs with null bytes", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "test-post\0" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject slugs with special shell characters", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const maliciousSlugs = [
        "test-post; rm -rf /",
        "test-post | cat /etc/passwd",
        "test-post && cat /etc/passwd",
        "test-post $(cat /etc/passwd)",
        "test-post `cat /etc/passwd`",
      ];

      for (const slug of maliciousSlugs) {
        const context = createMockContext({ slug });
        const result = await loader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should reject slugs with unicode characters that could be dangerous", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "test-post\u202e" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec allow list validation", () => {
    it("should reject slugs not in the allow list", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const invalidSlugs = ["random-slug", "prompt-testing", "fake-post", ""];

      for (const slug of invalidSlugs) {
        const context = createMockContext({ slug });
        const result = await loader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should verify allow list is properly constructed", () => {
      const meta = getAllBlogMeta();
      const validSlugSet = new Set(meta.map((post) => post.slug));

      expect(validSlugSet.has("test-post")).toBe(true);
      expect(validSlugSet.has("another-post")).toBe(true);
      expect(validSlugSet.size).toBe(2);
    });
  });

  describe("edge cases", () => {
    it("should handle empty slug", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle very long slug", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const longSlug = "a".repeat(1000);
      const context = createMockContext({ slug: longSlug });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle slug with only special characters", async () => {
      const route = createContentRouteConfig("/blog/$slug", {
        getMeta: getAllBlogMeta,
        moduleMap: BLOG_MODULE_MAP,
        prefix: "blog",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ slug: "!!!@@@###$$$" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });
});

describe("createContentRouteConfig - docs", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should return undefined for non-existent doc (fails allow list check)", async () => {
    const route = createContentRouteConfig("/docs/v1/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      version: "v1",
      component: DummyComponent,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: "learn/non-existent-doc" });
    const result = await loader(context);

    expect(result).toBeUndefined();
  });

  it("should successfully load a valid doc", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("v1/learn/test-doc", () =>
      Promise.resolve({
        default: {
          content: testMDXContent,
          frontmatter: {
            title: "Test Doc",
            description: "A test doc",
          },
          tableOfContents: [],
        } satisfies PreprocessedMDX,
      }),
    );

    const route = createContentRouteConfig("/docs/v1/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      version: "v1",
      component: DummyComponent,
      _testModuleMap: customModuleMap,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: "learn/test-doc" });
    const result = (await loader(context)) as DocContent | undefined;

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Test Doc");
  });

  it("should handle index page (empty _splat)", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("v1/index", () =>
      Promise.resolve({
        default: {
          content: testMDXContent,
          frontmatter: {
            title: "Index Page",
            description: "Index page",
          },
          tableOfContents: [],
        } satisfies PreprocessedMDX,
      }),
    );

    const route = createContentRouteConfig("/docs/v1/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      version: "v1",
      component: DummyComponent,
      _testModuleMap: customModuleMap,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: undefined });
    const result = (await loader(context)) as DocContent | undefined;

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Index Page");
  });

  it("should handle different versions correctly", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("v2/learn/test-doc", () =>
      Promise.resolve({
        default: {
          content: testMDXContent,
          frontmatter: {
            title: "V2 Doc",
            description: "V2 doc",
          },
          tableOfContents: [],
        } satisfies PreprocessedMDX,
      }),
    );

    // Create a loader with v2 version - our mock metadata only has v1 routes
    const route = createContentRouteConfig("/docs/v2/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      version: "v2",
      component: DummyComponent,
      _testModuleMap: customModuleMap,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: "learn/test-doc" });
    const result = await loader(context);

    // Should fail because our mock docsMetadata only has v1 routes
    expect(result).toBeUndefined();
  });

  it("should successfully load a non-versioned doc", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("learn/non-versioned-doc", () =>
      Promise.resolve({
        default: {
          content: testMDXContent,
          frontmatter: {
            title: "Non-Versioned Doc",
            description: "A non-versioned doc",
          },
          tableOfContents: [],
        } satisfies PreprocessedMDX,
      }),
    );

    // Loader without version parameter
    const route = createContentRouteConfig("/docs/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      component: DummyComponent,
      _testModuleMap: customModuleMap,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: "learn/non-versioned-doc" });
    const result = (await loader(context)) as DocContent | undefined;

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Non-Versioned Doc");
  });

  it("should handle non-versioned index page (empty _splat)", async () => {
    const customModuleMap = createTestModuleMap();
    customModuleMap.set("index", () =>
      Promise.resolve({
        default: {
          content: testMDXContent,
          frontmatter: {
            title: "Non-Versioned Index",
            description: "Non-versioned index page",
          },
          tableOfContents: [],
        } satisfies PreprocessedMDX,
      }),
    );

    // Loader without version parameter
    const route = createContentRouteConfig("/docs/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      component: DummyComponent,
      _testModuleMap: customModuleMap,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: undefined });
    const result = (await loader(context)) as DocContent | undefined;

    expect(result).toBeDefined();
    expect(result?.content).toBe(testMDXContent);
    expect(result?.mdx.frontmatter?.title).toBe("Non-Versioned Index");
  });

  it("should not load versioned docs when version is not specified", async () => {
    // Try to access v1 doc without specifying version
    const route = createContentRouteConfig("/docs/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      component: DummyComponent,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: "learn/test-doc" });
    const result = await loader(context);

    // Should fail because path won't match (docs/learn/test-doc vs docs/v1/learn/test-doc)
    expect(result).toBeUndefined();
  });

  it("should not load non-versioned docs when version is specified", async () => {
    // Try to access non-versioned doc with v1 version specified
    const route = createContentRouteConfig("/docs/v1/$", {
      getMeta: getAllDocsMeta,
      moduleMap: DOCS_MODULE_MAP,
      prefix: "docs",
      version: "v1",
      component: DummyComponent,
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: "learn/non-versioned-doc" });
    const result = await loader(context);

    // Should fail because path won't match (docs/v1/learn/non-versioned-doc vs docs/learn/non-versioned-doc)
    expect(result).toBeUndefined();
  });

  describe("appsec path traversal attacks", () => {
    it("should reject path traversal with ../", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "../../../etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with ..\\", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({
        _splat: "..\\..\\..\\windows\\system32",
      });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with encoded ../", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({
        _splat: "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
      });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with double-encoded ../", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({
        _splat: "%252e%252e%252f%252e%252e%252fetc%252fpasswd",
      });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject path traversal with mixed slashes", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "..\\../etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject absolute paths", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "/etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with forward slashes in _splat", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "learn/../etc/passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject paths with backslashes in _splat", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "learn\\..\\etc\\passwd" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec invalid characters", () => {
    it("should reject _splat with null bytes", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "learn/test-doc\0" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should reject _splat with special shell characters", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const maliciousSplats = [
        "learn/test-doc; rm -rf /",
        "learn/test-doc | cat /etc/passwd",
        "learn/test-doc && cat /etc/passwd",
        "learn/test-doc $(cat /etc/passwd)",
        "learn/test-doc `cat /etc/passwd`",
      ];

      for (const splat of maliciousSplats) {
        const context = createMockContext({ _splat: splat });
        const result = await loader(context);
        expect(result).toBeUndefined();
      }
    });

    it("should reject _splat with unicode characters that could be dangerous", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "learn/test-doc\u202e" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });
  });

  describe("appsec allow list validation", () => {
    it("should reject _splat not in the allow list", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      // Note: empty string "" is NOT invalid - it triggers index page fallback
      const invalidSplats = [
        "random/path",
        "learn/fake-doc",
        "v1/learn/test-doc", // includes version prefix (shouldn't)
      ];

      for (const splat of invalidSplats) {
        const context = createMockContext({ _splat: splat });
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
    it("should handle very long _splat", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const longSplat = "a".repeat(1000);
      const context = createMockContext({ _splat: longSplat });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle _splat with only special characters", async () => {
      const route = createContentRouteConfig("/docs/v1/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v1",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "!!!@@@###$$$" });
      const result = await loader(context);

      expect(result).toBeUndefined();
    });

    it("should handle version mismatch", async () => {
      // Try to access v1 doc with v2 loader
      const route = createContentRouteConfig("/docs/v2/$", {
        getMeta: getAllDocsMeta,
        moduleMap: DOCS_MODULE_MAP,
        prefix: "docs",
        version: "v2",
        component: DummyComponent,
      });
      const loader = getLoader(route);
      const context = createMockContext({ _splat: "learn/test-doc" });
      const result = await loader(context);

      // Should fail because path won't match
      expect(result).toBeUndefined();
    });
  });
});

describe("createContentRouteConfig - redirectOnEmpty", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("should redirect when _splat is empty and redirectOnEmpty is set", async () => {
    const route = createContentRouteConfig("/terms/$", {
      getMeta: getAllPolicyMeta,
      moduleMap: POLICY_MODULE_MAP,
      prefix: "policy",
      subdirectory: "terms",
      component: DummyComponent,
      redirectOnEmptySplat: { to: "/terms/$", params: { _splat: "use" } },
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: undefined });

    await expect(loader(context)).rejects.toThrow("Redirect");
  });

  it("should not redirect when _splat has a value", async () => {
    const route = createContentRouteConfig("/terms/$", {
      getMeta: getAllPolicyMeta,
      moduleMap: POLICY_MODULE_MAP,
      prefix: "policy",
      subdirectory: "terms",
      component: DummyComponent,
      redirectOnEmptySplat: { to: "/terms/$", params: { _splat: "use" } },
    });
    const loader = getLoader(route);
    const context = createMockContext({ _splat: "service" });

    // Should not throw, just return undefined (no matching metadata in mock)
    const result = await loader(context);
    expect(result).toBeUndefined();
  });
});
