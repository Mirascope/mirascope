/* eslint-disable @typescript-eslint/no-unsafe-assignment */
/* eslint-disable @typescript-eslint/no-unsafe-member-access */
import { describe, it, expect } from "vitest";
import {
  canonicalizePath,
  routeToImagePath,
  generateOpenGraphMeta,
  generateTwitterMeta,
  generateArticleMeta,
  generateArticleJsonLd,
  createPageHead,
  type HeadMetaEntry,
} from "./head";

const BASE_URL = "https://mirascope.com";

/* ========== HELPER FUNCTION TESTS =========== */

describe("canonicalizePath", () => {
  it("removes trailing slash", () => {
    expect(canonicalizePath("/blog/")).toBe("/blog");
    expect(canonicalizePath("/docs/v1/")).toBe("/docs/v1");
  });

  it("preserves root path", () => {
    expect(canonicalizePath("/")).toBe("/");
  });

  it("handles paths without trailing slash", () => {
    expect(canonicalizePath("/blog")).toBe("/blog");
    expect(canonicalizePath("/docs/v1/intro")).toBe("/docs/v1/intro");
  });

  it("handles empty string", () => {
    expect(canonicalizePath("")).toBe("");
  });
});

describe("routeToImagePath", () => {
  it("converts /blog/my-post to /social-cards/blog-my-post.webp", () => {
    expect(routeToImagePath("/blog/my-post")).toBe(
      "/social-cards/blog-my-post.webp",
    );
  });

  it("handles root path", () => {
    expect(routeToImagePath("/")).toBe("/social-cards/index.webp");
  });

  it("handles nested paths", () => {
    expect(routeToImagePath("/docs/v1/learn/intro")).toBe(
      "/social-cards/docs-v1-learn-intro.webp",
    );
  });

  it("handles trailing slashes", () => {
    expect(routeToImagePath("/blog/")).toBe("/social-cards/blog.webp");
  });

  it("handles single segment", () => {
    expect(routeToImagePath("/pricing")).toBe("/social-cards/pricing.webp");
  });
});

describe("generateOpenGraphMeta", () => {
  it("generates all OG tags", () => {
    const result = generateOpenGraphMeta({
      type: "website",
      url: "https://mirascope.com/blog",
      title: "Blog | Mirascope",
      description: "Latest updates",
      image: "https://mirascope.com/social-cards/blog.webp",
    });

    expect(result).toHaveLength(5);
    expect(result).toContainEqual({ property: "og:type", content: "website" });
    expect(result).toContainEqual({
      property: "og:url",
      content: "https://mirascope.com/blog",
    });
    expect(result).toContainEqual({
      property: "og:title",
      content: "Blog | Mirascope",
    });
    expect(result).toContainEqual({
      property: "og:description",
      content: "Latest updates",
    });
    expect(result).toContainEqual({
      property: "og:image",
      content: "https://mirascope.com/social-cards/blog.webp",
    });
  });

  it("supports article type", () => {
    const result = generateOpenGraphMeta({
      type: "article",
      url: "https://mirascope.com/blog/post",
      title: "Post | Mirascope",
      description: "A blog post",
      image: "https://mirascope.com/social-cards/blog-post.webp",
    });

    expect(result).toContainEqual({ property: "og:type", content: "article" });
  });
});

describe("generateTwitterMeta", () => {
  it("generates all Twitter tags", () => {
    const result = generateTwitterMeta({
      url: "https://mirascope.com/blog",
      title: "Blog | Mirascope",
      description: "Latest updates",
      image: "https://mirascope.com/social-cards/blog.webp",
    });

    expect(result).toHaveLength(5);
    expect(result).toContainEqual({
      name: "twitter:card",
      content: "summary_large_image",
    });
    expect(result).toContainEqual({
      name: "twitter:url",
      content: "https://mirascope.com/blog",
    });
    expect(result).toContainEqual({
      name: "twitter:title",
      content: "Blog | Mirascope",
    });
    expect(result).toContainEqual({
      name: "twitter:image",
      content: "https://mirascope.com/social-cards/blog.webp",
    });
    expect(result).toContainEqual({
      name: "twitter:description",
      content: "Latest updates",
    });
  });
});

describe("generateArticleMeta", () => {
  it("generates all article tags when all fields provided", () => {
    const result = generateArticleMeta({
      publishedTime: "2025-01-01",
      modifiedTime: "2025-01-10",
      author: "John Doe",
    });

    expect(result).toHaveLength(3);
    expect(result).toContainEqual({
      property: "article:published_time",
      content: "2025-01-01",
    });
    expect(result).toContainEqual({
      property: "article:modified_time",
      content: "2025-01-10",
    });
    expect(result).toContainEqual({
      property: "article:author",
      content: "John Doe",
    });
  });

  it("generates only provided fields", () => {
    const result = generateArticleMeta({
      publishedTime: "2025-01-01",
    });

    expect(result).toHaveLength(1);
    expect(result).toContainEqual({
      property: "article:published_time",
      content: "2025-01-01",
    });
  });

  it("returns empty array when no fields provided", () => {
    const result = generateArticleMeta({});
    expect(result).toHaveLength(0);
  });
});

describe("generateArticleJsonLd", () => {
  it("generates valid JSON-LD with all fields", () => {
    const result = generateArticleJsonLd({
      title: "My Blog Post",
      description: "A great article",
      url: "https://mirascope.com/blog/my-post",
      image: "https://mirascope.com/social-cards/blog-my-post.webp",
      article: {
        publishedTime: "2025-01-01",
        modifiedTime: "2025-01-10",
        author: "John Doe",
      },
    });

    const parsed = JSON.parse(result);
    expect(parsed["@context"]).toBe("https://schema.org");
    expect(parsed["@type"]).toBe("Article");
    expect(parsed.headline).toBe("My Blog Post");
    expect(parsed.description).toBe("A great article");
    expect(parsed.url).toBe("https://mirascope.com/blog/my-post");
    expect(parsed.image).toBe(
      "https://mirascope.com/social-cards/blog-my-post.webp",
    );
    expect(parsed.datePublished).toBe("2025-01-01");
    expect(parsed.dateModified).toBe("2025-01-10");
    expect(parsed.author).toEqual({ "@type": "Person", name: "John Doe" });
    expect(parsed.publisher).toEqual({
      "@type": "Organization",
      name: "Mirascope",
      logo: {
        "@type": "ImageObject",
        url: `${BASE_URL}/assets/branding/mirascope-logo.svg`,
      },
    });
  });

  it("omits optional fields when not provided", () => {
    const result = generateArticleJsonLd({
      title: "My Blog Post",
      description: "A great article",
      url: "https://mirascope.com/blog/my-post",
      image: "https://mirascope.com/social-cards/blog-my-post.webp",
      article: {},
    });

    const parsed = JSON.parse(result);
    expect(parsed.datePublished).toBeUndefined();
    expect(parsed.dateModified).toBeUndefined();
    expect(parsed.author).toBeUndefined();
  });
});

/* ========== createPageHead TEST MATRIX =========== */

describe("createPageHead", () => {
  // Helper to find meta by name or property
  const findMeta = (
    metas: HeadMetaEntry[],
    key: string,
    type: "name" | "property" = "name",
  ) => {
    return metas.find(
      (m) => type in m && (m as Record<string, string>)[type] === key,
    );
  };

  const findTitle = (metas: HeadMetaEntry[]) => {
    return metas.find((m) => "title" in m) as { title: string } | undefined;
  };

  describe("Test Case 1: Minimal (title + description)", () => {
    it("generates basic SEO metadata", () => {
      const result = createPageHead({
        route: "/blog",
        title: "Blog",
        description: "Latest news and updates",
      });

      // Title format
      expect(findTitle(result.meta)?.title).toBe("Blog | Mirascope");

      // Description
      expect(findMeta(result.meta, "description")).toEqual({
        name: "description",
        content: "Latest news and updates",
      });

      // Canonical URL
      expect(result.links).toContainEqual({
        rel: "canonical",
        href: `${BASE_URL}/blog`,
      });

      // OG tags present
      expect(findMeta(result.meta, "og:type", "property")).toEqual({
        property: "og:type",
        content: "website",
      });
      expect(findMeta(result.meta, "og:url", "property")).toEqual({
        property: "og:url",
        content: `${BASE_URL}/blog`,
      });
      expect(findMeta(result.meta, "og:title", "property")).toEqual({
        property: "og:title",
        content: "Blog | Mirascope",
      });
      expect(findMeta(result.meta, "og:image", "property")).toEqual({
        property: "og:image",
        content: `${BASE_URL}/social-cards/blog.webp`,
      });

      // Twitter tags present
      expect(findMeta(result.meta, "twitter:card")).toEqual({
        name: "twitter:card",
        content: "summary_large_image",
      });

      // No scripts (not an article)
      expect(result.scripts).toBeUndefined();
    });
  });

  describe("Test Case 2: Website type explicit", () => {
    it("generates website OG type", () => {
      const result = createPageHead({
        route: "/pricing",
        title: "Pricing",
        description: "Our pricing plans",
        ogType: "website",
      });

      expect(findMeta(result.meta, "og:type", "property")).toEqual({
        property: "og:type",
        content: "website",
      });
      expect(result.scripts).toBeUndefined();
    });
  });

  describe("Test Case 3: Article (blog post) with full metadata", () => {
    it("generates article metadata with JSON-LD", () => {
      const result = createPageHead({
        route: "/blog/my-post",
        title: "My Blog Post",
        description: "A great article about something",
        ogType: "article",
        article: {
          publishedTime: "2025-01-01",
          modifiedTime: "2025-01-10",
          author: "John Doe",
        },
      });

      // OG type is article
      expect(findMeta(result.meta, "og:type", "property")).toEqual({
        property: "og:type",
        content: "article",
      });

      // Article meta tags
      expect(
        findMeta(result.meta, "article:published_time", "property"),
      ).toEqual({
        property: "article:published_time",
        content: "2025-01-01",
      });
      expect(
        findMeta(result.meta, "article:modified_time", "property"),
      ).toEqual({
        property: "article:modified_time",
        content: "2025-01-10",
      });
      expect(findMeta(result.meta, "article:author", "property")).toEqual({
        property: "article:author",
        content: "John Doe",
      });

      // JSON-LD script
      expect(result.scripts).toHaveLength(1);
      expect(result.scripts![0].type).toBe("application/ld+json");
      const jsonLd = JSON.parse(result.scripts![0].children);
      expect(jsonLd["@type"]).toBe("Article");
      expect(jsonLd.headline).toBe("My Blog Post");
      expect(jsonLd.datePublished).toBe("2025-01-01");
      expect(jsonLd.author.name).toBe("John Doe");
    });
  });

  describe("Test Case 4: Article with partial metadata", () => {
    it("generates article with only provided fields", () => {
      const result = createPageHead({
        route: "/blog/partial-post",
        title: "Partial Post",
        description: "A post with minimal article data",
        ogType: "article",
        article: {
          publishedTime: "2025-01-15",
        },
      });

      // Article meta tags - only published time
      expect(
        findMeta(result.meta, "article:published_time", "property"),
      ).toEqual({
        property: "article:published_time",
        content: "2025-01-15",
      });
      expect(
        findMeta(result.meta, "article:modified_time", "property"),
      ).toBeUndefined();
      expect(
        findMeta(result.meta, "article:author", "property"),
      ).toBeUndefined();

      // JSON-LD should still be generated
      expect(result.scripts).toHaveLength(1);
      const jsonLd = JSON.parse(result.scripts![0].children);
      expect(jsonLd.datePublished).toBe("2025-01-15");
      expect(jsonLd.dateModified).toBeUndefined();
      expect(jsonLd.author).toBeUndefined();
    });
  });

  describe("Test Case 5: Custom image path", () => {
    it("uses custom image path", () => {
      const result = createPageHead({
        route: "/docs/intro",
        title: "Introduction",
        description: "Getting started guide",
        image: "/custom-images/docs-intro.webp",
      });

      expect(findMeta(result.meta, "og:image", "property")).toEqual({
        property: "og:image",
        content: `${BASE_URL}/custom-images/docs-intro.webp`,
      });
      expect(findMeta(result.meta, "twitter:image")).toEqual({
        name: "twitter:image",
        content: `${BASE_URL}/custom-images/docs-intro.webp`,
      });
    });
  });

  describe("Test Case 6: External image URL", () => {
    it("preserves external image URLs", () => {
      const externalUrl = "https://cdn.example.com/images/og-image.png";
      const result = createPageHead({
        route: "/special-page",
        title: "Special Page",
        description: "A page with external image",
        image: externalUrl,
      });

      expect(findMeta(result.meta, "og:image", "property")).toEqual({
        property: "og:image",
        content: externalUrl,
      });
      expect(findMeta(result.meta, "twitter:image")).toEqual({
        name: "twitter:image",
        content: externalUrl,
      });
    });
  });

  describe("Test Case 7: Empty description", () => {
    it("handles empty description", () => {
      const result = createPageHead({
        route: "/empty-desc",
        title: "Page",
        description: "",
      });

      expect(findMeta(result.meta, "description")).toEqual({
        name: "description",
        content: "",
      });
      expect(findMeta(result.meta, "og:description", "property")).toEqual({
        property: "og:description",
        content: "",
      });
    });
  });

  describe("Canonical URL handling", () => {
    it("removes trailing slash from canonical URL", () => {
      const result = createPageHead({
        route: "/blog/",
        title: "Blog",
        description: "Latest news",
      });

      expect(result.links).toContainEqual({
        rel: "canonical",
        href: `${BASE_URL}/blog`,
      });
    });

    it("preserves root path", () => {
      const result = createPageHead({
        route: "/",
        title: "Home",
        description: "Welcome",
      });

      expect(result.links).toContainEqual({
        rel: "canonical",
        href: `${BASE_URL}/`,
      });
    });
  });

  describe("Article without article data", () => {
    it("does not generate JSON-LD when ogType is article but no article data", () => {
      const result = createPageHead({
        route: "/blog/no-data",
        title: "No Data Post",
        description: "A post without article metadata",
        ogType: "article",
      });

      // OG type should still be article
      expect(findMeta(result.meta, "og:type", "property")).toEqual({
        property: "og:type",
        content: "article",
      });

      // But no JSON-LD since article data is missing
      expect(result.scripts).toBeUndefined();
    });
  });
});
