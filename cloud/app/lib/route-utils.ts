/**
 * Utility to detect whether a pathname belongs to the cloud app
 * (i.e., an org-slug-based route) vs. a static/public route.
 *
 * TanStack Router's file-based routing prioritizes static routes over
 * dynamic $orgSlug, so static segments listed here will never accidentally
 * match the dynamic route.
 */

import { RESERVED_ORG_SLUGS } from "@/db/slug";

/**
 * TanStack Router top-level static route segments that are real file-based
 * routes but are NOT already listed in RESERVED_ORG_SLUGS.
 *
 * Currently RESERVED_ORG_SLUGS covers all known static routes, so this set
 * exists only as a forward-looking safety net. If a new top-level route is
 * added that isn't a reserved slug, add it here.
 */
export const ADDITIONAL_STATIC_SEGMENTS: ReadonlySet<string> = new Set([
  // All current TanStack Router static routes are already in RESERVED_ORG_SLUGS.
  // Add any future route segments here that shouldn't be treated as org slugs.
]);

/**
 * Combined set of first path segments that are NOT org slugs.
 *
 * Union of RESERVED_ORG_SLUGS (the single source of truth for slug
 * reservation) and any additional static route segments.
 */
const STATIC_SEGMENTS: ReadonlySet<string> = new Set([
  ...RESERVED_ORG_SLUGS,
  ...ADDITIONAL_STATIC_SEGMENTS,
]);

/**
 * Returns true when the pathname is a cloud app route (org-slug-based).
 * Returns false for the landing page ("/") and all static/public routes.
 */
export function isCloudAppRoute(pathname: string): boolean {
  if (pathname === "/") return false;
  const firstSegment = pathname.split("/")[1];
  if (!firstSegment) return false;
  return !STATIC_SEGMENTS.has(firstSegment);
}

/**
 * Segments that use the application shell (no footer, cloud-style layout).
 * These are reserved slugs that are still "app" routes, not marketing pages.
 */
const APPLICATION_SEGMENTS: ReadonlySet<string> = new Set([
  "settings",
  "organizations",
  "onboarding",
  "invitations",
]);

/**
 * Returns true for any route that should use the application layout shell:
 * org-slug cloud routes, settings, organizations, onboarding, etc.
 *
 * Use this for layout decisions (footer visibility, wrapper classes).
 * Use `isCloudAppRoute` when you specifically need org-slug detection.
 */
export function isApplicationRoute(pathname: string): boolean {
  if (isCloudAppRoute(pathname)) return true;
  const firstSegment = pathname.split("/")[1];
  if (!firstSegment) return false;
  return APPLICATION_SEGMENTS.has(firstSegment);
}
