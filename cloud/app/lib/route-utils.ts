/**
 * Utility to detect whether a pathname belongs to the cloud app
 * (i.e., an org-slug-based route) vs. a static/public route.
 *
 * TanStack Router's file-based routing prioritizes static routes over
 * dynamic $orgSlug, so static segments listed here will never accidentally
 * match the dynamic route.
 */

/**
 * First path segments that are NOT org slugs.
 *
 * This must include every top-level static route, server redirect, and
 * reserved slug so that `isCloudAppRoute` correctly returns false for them.
 * Keeping this in sync with RESERVED_ORG_SLUGS in db/slug.ts ensures that
 * no reserved slug is misidentified as a cloud app route.
 */
const STATIC_SEGMENTS = new Set([
  // TanStack Router static routes
  "blog",
  "dev",
  "docs",
  "organizations",
  "pricing",
  "privacy",
  "api",
  "auth",
  "invitations",
  "terms",
  "router",
  "login",
  "onboarding",
  "cloud",
  "agents",
  // Server-level redirects
  "discord-invite",
  "slack-invite",
  "post",
  "integrations",
  // Infrastructure
  "claws",
  "staging",
  "www",
  "internal",
  "app",
  "admin",
  "mail",
  "cdn",
  "static",
  "assets",
  "status",
  "health",
  "graphql",
  "webhooks",
  "metrics",
  // Auth / account flows
  "signup",
  "register",
  "logout",
  "callback",
  "oauth",
  "sso",
  "account",
  "settings",
  "profile",
  "verify",
  "reset-password",
  "confirm",
  // Marketing / static pages
  "about",
  "careers",
  "jobs",
  "contact",
  "support",
  "help",
  "press",
  "changelog",
  "features",
  "enterprise",
  "teams",
  "home",
  "security",
  // Legal
  "legal",
  "cookies",
  "dmca",
  "compliance",
  "acceptable-use",
  // Product routes
  "dashboard",
  "console",
  "explore",
  "search",
  "marketplace",
  "billing",
  "checkout",
  "plans",
  "notifications",
  "new",
  "create",
  "feed",
  // Abuse prevention
  "administrator",
  "moderator",
  "system",
  "root",
  "info",
  "noreply",
  "abuse",
  "postmaster",
  "webmaster",
  "mirascope",
  "official",
  "team",
  "staff",
  "engineering",
  // Edge-case strings
  "null",
  "undefined",
  "true",
  "false",
  "test",
  "demo",
  "example",
  "localhost",
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
