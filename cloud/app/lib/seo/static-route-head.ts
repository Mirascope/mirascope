/**
 * Static Route Metadata Utilities
 *
 * Provides functions for working with static route metadata.
 * Used by route definitions and social card generation.
 *
 * To add or update route metadata, edit static-routes.ts
 */

// NOTE: Must use relative path instead of @/app alias because this file
// is imported by vite.config.ts during Vite's config processing phase, before
// the alias resolution is set up. Using the alias would cause module resolution errors.
import type { FileRouteTypes } from "../../routeTree.gen";
import { createPageHead, type HeadResult } from "./head";
import { STATIC_ROUTE_REGISTRY, type StaticRouteMeta } from "./static-routes";

// Re-export for consumers
export type { StaticRouteMeta };

// Valid route IDs from the generated route tree
type ValidRouteId = FileRouteTypes["id"];

/**
 * Creates a build-time and type-safe static route head definition.
 *
 * Use with TanStack Router's `createFileRoute`:
 *
 * @example
 * ```typescript
 * export const Route = createFileRoute("/")({
 *   head: createStaticRouteHead("/"),
 *   component: HomePage,
 * });
 * ```
 *
 * @throws Error if the route is not registered in STATIC_ROUTE_REGISTRY
 */
export function createStaticRouteHead(route: ValidRouteId): () => HeadResult {
  const meta = STATIC_ROUTE_REGISTRY[route];
  if (!meta) {
    throw new Error(
      `[static-routes] Route "${route}" is not registered in STATIC_ROUTE_REGISTRY`,
    );
  }

  return () =>
    createPageHead({
      route,
      title: meta.title,
      description: meta.description,
    });
}

/**
 * Lookup a static route's title by route path.
 *
 * Used by social-cards.ts to get titles for static pages.
 * Logs a warning if no match is found.
 *
 * @param route - The route path to lookup
 * @returns The title if found, null otherwise
 */
export function getStaticRouteTitle(route: string): string | null {
  const meta = STATIC_ROUTE_REGISTRY[route as ValidRouteId];
  if (meta) {
    return meta.title;
  }

  console.warn(`[static-routes] No metadata found for route: ${route}`);
  return null;
}

/**
 * Get all registered static routes.
 *
 * Used by social-cards.ts to iterate over static routes for card generation.
 *
 * @returns Array of route paths
 */
export function getStaticRoutes(): string[] {
  return Object.keys(STATIC_ROUTE_REGISTRY);
}
