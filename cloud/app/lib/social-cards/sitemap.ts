/**
 * Sitemap parsing utilities for social card generation
 */

/**
 * Parse sitemap XML and extract URLs that have a changefreq tag.
 * URLs with changefreq are considered indexed/public pages that need social cards.
 *
 * @param sitemapXml - The raw sitemap XML content
 * @returns Array of URL paths (e.g., ["/blog/my-post", "/docs/intro"])
 */
export function parseSitemapForIndexedUrls(sitemapXml: string): string[] {
  const urlMatches = sitemapXml.match(/<url>[\s\S]*?<\/url>/g) ?? [];

  return urlMatches
    .filter((urlBlock) => /<changefreq>.*?<\/changefreq>/i.test(urlBlock))
    .map((urlBlock) => urlBlock.match(/<loc>(.*?)<\/loc>/)?.[1])
    .filter((loc): loc is string => loc !== undefined)
    .map((loc) => new URL(loc).pathname);
}

/**
 * Convert a route path to a social card filename.
 * Matches the logic in app/lib/seo/head.ts routeToImagePath()
 *
 * @param route - URL path (e.g., "/blog/my-post")
 * @returns Filename without directory (e.g., "blog-my-post.webp")
 */
export function routeToFilename(route: string): string {
  // Canonicalize path (remove all trailing slashes except for root)
  let cleanRoute = route;
  if (route !== "/") {
    cleanRoute = route.replace(/\/+$/, "");
  }

  // Remove leading slash and replace remaining slashes with dashes
  const filename = cleanRoute.replace(/^\//, "").replace(/\//g, "-") || "index";

  return `${filename}.webp`;
}
