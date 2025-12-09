// Shared logic for identifying hidden routes
// Used by both client-side components and build scripts

// Patterns for hidden routes (not included in sitemap or SEO metadata)
export const EXCLUDE_DEV = /^\/dev(\/.*)?$/;
export const MIRASCOPE_V2 = /^\/docs\/mirascope\/v2.*/;
export const HIDDEN_ROUTE_PATTERNS = [EXCLUDE_DEV, MIRASCOPE_V2];

/**
 * Check if a route should be hidden from search engines and sitemaps
 */
export function isHiddenRoute(route: string): boolean {
  return HIDDEN_ROUTE_PATTERNS.some((pattern) => pattern.test(route));
}
