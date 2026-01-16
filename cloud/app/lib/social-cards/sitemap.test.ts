import { describe, it, expect } from "vitest";
import { parseSitemapForIndexedUrls, routeToFilename } from "./sitemap";

describe("parseSitemapForIndexedUrls", () => {
  it("returns empty array for empty sitemap", () => {
    expect(parseSitemapForIndexedUrls("")).toEqual([]);
  });

  it("returns empty array for sitemap with no url blocks", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual([]);
  });

  it("extracts paths from URLs with changefreq", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
    <changefreq>daily</changefreq>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual(["/page1", "/page2"]);
  });

  it("excludes URLs without changefreq", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/indexed</loc>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>https://example.com/not-indexed</loc>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual(["/indexed"]);
  });

  it("handles changefreq with different values", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/daily</loc>
    <changefreq>daily</changefreq>
  </url>
  <url>
    <loc>https://example.com/monthly</loc>
    <changefreq>monthly</changefreq>
  </url>
  <url>
    <loc>https://example.com/never</loc>
    <changefreq>never</changefreq>
  </url>
  <url>
    <loc>https://example.com/no-freq</loc>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual([
      "/daily",
      "/monthly",
      "/never",
    ]);
  });

  it("is case-insensitive for changefreq tag", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/upper</loc>
    <CHANGEFREQ>weekly</CHANGEFREQ>
  </url>
  <url>
    <loc>https://example.com/mixed</loc>
    <ChangeFreq>weekly</ChangeFreq>
  </url>
  <url>
    <loc>https://example.com/none</loc>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual(["/upper", "/mixed"]);
  });

  it("includes root path / when it has changefreq", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/</loc>
    <changefreq>daily</changefreq>
  </url>
  <url>
    <loc>https://example.com/page</loc>
    <changefreq>weekly</changefreq>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual(["/", "/page"]);
  });

  it("handles nested paths", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/docs/getting-started</loc>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>https://example.com/blog/2024/post</loc>
    <changefreq>monthly</changefreq>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual([
      "/docs/getting-started",
      "/blog/2024/post",
    ]);
  });

  it("throws on invalid URL in loc", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>not-a-valid-url</loc>
    <changefreq>weekly</changefreq>
  </url>
</urlset>`;
    expect(() => parseSitemapForIndexedUrls(sitemap)).toThrow();
  });

  it("handles url blocks with other tags", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/with-priority</loc>
    <priority>0.8</priority>
    <lastmod>2024-01-01</lastmod>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>https://example.com/without-freq</loc>
    <priority>0.5</priority>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual(["/with-priority"]);
  });

  it("skips url blocks without loc", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <priority>0.5</priority>
    <changefreq>weekly</changefreq>
  </url>
  <url>
    <loc>https://example.com/valid</loc>
    <changefreq>weekly</changefreq>
  </url>
</urlset>`;
    expect(parseSitemapForIndexedUrls(sitemap)).toEqual(["/valid"]);
  });
});

describe("routeToFilename", () => {
  it("converts simple path to filename", () => {
    expect(routeToFilename("/blog")).toBe("blog.webp");
  });

  it("converts nested path to hyphenated filename", () => {
    expect(routeToFilename("/blog/my-post")).toBe("blog-my-post.webp");
  });

  it("handles deeply nested paths", () => {
    expect(routeToFilename("/docs/v1/learn/intro")).toBe(
      "docs-v1-learn-intro.webp",
    );
  });

  it("handles root path", () => {
    expect(routeToFilename("/")).toBe("index.webp");
  });

  it("handles trailing slashes", () => {
    expect(routeToFilename("/blog/")).toBe("blog.webp");
  });

  it("handles path with multiple trailing slashes", () => {
    expect(routeToFilename("/blog//")).toBe("blog.webp");
  });

  it("preserves hyphens in path segments", () => {
    expect(routeToFilename("/blog/my-awesome-post")).toBe(
      "blog-my-awesome-post.webp",
    );
  });

  it("handles single segment paths", () => {
    expect(routeToFilename("/pricing")).toBe("pricing.webp");
  });
});
