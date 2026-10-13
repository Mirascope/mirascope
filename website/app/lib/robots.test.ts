import { describe, it, expect } from "vitest";

import {
  parseSitemapForUrlsWithoutChangefreq,
  generateRobotsTxt,
} from "./robots";

describe("parseSitemapForUrlsWithoutChangefreq", () => {
  it("returns empty array for empty sitemap", () => {
    expect(parseSitemapForUrlsWithoutChangefreq("")).toEqual([]);
  });

  it("returns empty array for sitemap with no url blocks", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual([]);
  });

  it("extracts paths from URLs without changefreq", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page1</loc>
  </url>
  <url>
    <loc>https://example.com/page2</loc>
  </url>
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual([
      "/page1",
      "/page2",
    ]);
  });

  it("excludes URLs that have changefreq", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/static</loc>
  </url>
  <url>
    <loc>https://example.com/dynamic</loc>
    <changefreq>weekly</changefreq>
  </url>
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual(["/static"]);
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
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual(["/no-freq"]);
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
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual(["/none"]);
  });

  it("excludes root path /", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/</loc>
  </url>
  <url>
    <loc>https://example.com/page</loc>
  </url>
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual(["/page"]);
  });

  it("handles nested paths", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/docs/getting-started</loc>
  </url>
  <url>
    <loc>https://example.com/blog/2024/post</loc>
  </url>
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual([
      "/docs/getting-started",
      "/blog/2024/post",
    ]);
  });

  it("throws on invalid URL in loc", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>not-a-valid-url</loc>
  </url>
</urlset>`;
    expect(() => parseSitemapForUrlsWithoutChangefreq(sitemap)).toThrow();
  });

  it("handles url blocks with other tags", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/with-priority</loc>
    <priority>0.8</priority>
    <lastmod>2024-01-01</lastmod>
  </url>
  <url>
    <loc>https://example.com/with-freq</loc>
    <priority>0.5</priority>
    <changefreq>weekly</changefreq>
  </url>
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual([
      "/with-priority",
    ]);
  });

  it("handles multiline url blocks", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <loc>https://example.com/multiline</loc>
    <priority>0.5</priority>
  </url>
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual([
      "/multiline",
    ]);
  });

  it("skips url blocks without loc", () => {
    const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://example.com/valid</loc>
  </url>
</urlset>`;
    expect(parseSitemapForUrlsWithoutChangefreq(sitemap)).toEqual(["/valid"]);
  });
});

describe("generateRobotsTxt", () => {
  const siteUrl = "https://example.com";
  const sitemapUrl = "https://example.com/sitemap.xml";

  it("generates robots.txt with no disallow paths", () => {
    const result = generateRobotsTxt([], siteUrl, sitemapUrl);
    expect(result).toBe(`# robots.txt for https://example.com
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml`);
  });

  it("generates robots.txt with single disallow path", () => {
    const result = generateRobotsTxt(["/private"], siteUrl, sitemapUrl);
    expect(result).toBe(`# robots.txt for https://example.com
User-agent: *
Allow: /
Disallow: /private

Sitemap: https://example.com/sitemap.xml`);
  });

  it("generates robots.txt with multiple disallow paths", () => {
    const result = generateRobotsTxt(
      ["/private", "/admin", "/internal"],
      siteUrl,
      sitemapUrl,
    );
    expect(result).toBe(`# robots.txt for https://example.com
User-agent: *
Allow: /
Disallow: /private
Disallow: /admin
Disallow: /internal

Sitemap: https://example.com/sitemap.xml`);
  });

  it("uses provided sitemap URL", () => {
    const result = generateRobotsTxt(
      [],
      "https://mirascope.com",
      "https://mirascope.com/sitemap.xml",
    );
    expect(result).toContain("Sitemap: https://mirascope.com/sitemap.xml");
  });
});
