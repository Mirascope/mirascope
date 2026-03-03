/**
 * Pure functions for robots.txt generation from sitemap data
 */

/**
 * Parse sitemap XML and extract URLs that don't have a changefreq tag.
 * URLs without changefreq are considered low-priority for crawling.
 * The root path "/" is excluded as changefreq doesn't apply globally.
 */
export function parseSitemapForUrlsWithoutChangefreq(
  sitemapXml: string,
): string[] {
  const urlMatches = sitemapXml.match(/<url>[\s\S]*?<\/url>/g) ?? [];

  return (
    urlMatches
      .filter((urlBlock) => !/<changefreq>.*?<\/changefreq>/i.test(urlBlock))
      .map((urlBlock) => urlBlock.match(/<loc>(.*?)<\/loc>/)?.[1])
      .filter((loc): loc is string => loc !== undefined)
      .map((loc) => new URL(loc).pathname)
      // exclude root path
      .filter((pathname) => pathname !== "/")
  );
}

/**
 * Generate robots.txt content from a list of disallow paths
 */
export function generateRobotsTxt(
  disallowPaths: string[],
  siteUrl: string,
  sitemapUrl: string,
): string {
  const baseRules = `# robots.txt for ${siteUrl}
User-agent: *
Allow: /
`;

  const disallowRules = disallowPaths.map((p) => `Disallow: ${p}`).join("\n");

  return `${baseRules}${disallowRules ? `${disallowRules}\n` : ""}\nSitemap: ${sitemapUrl}`;
}
