/**
 * Static Route Metadata Registry
 *
 * This file contains metadata for all static (non-content) routes.
 * Add new entries here when creating new static pages.
 *
 * Keys are TanStack Router route IDs from the generated route tree.
 * Only include non-content routes (not docs, blog posts, policy pages).
 */

// NOTE: Must use relative path instead of @/app alias because this file
// is imported by vite.config.ts during Vite's config processing phase, before
// the alias resolution is set up. Using the alias would cause module resolution errors.
import type { FileRouteTypes } from "../../routeTree.gen";

type ValidRouteId = FileRouteTypes["id"];

export interface StaticRouteMeta {
  title: string;
  description: string;
}

export const STATIC_ROUTE_REGISTRY: Partial<
  Record<ValidRouteId, StaticRouteMeta>
> = {
  "/": {
    title: "Home",
    description:
      "Deploy your own AI agents — Claws that listen, learn, create, and grow. Instant deployment, full observability, no code required.",
  },
  "/pricing": {
    title: "Pricing",
    description: "Pricing plans for Mirascope Cloud AI bots and observability",
  },
  "/blog/": {
    title: "Blog",
    description:
      "The latest news, updates, and insights about Mirascope and LLM application development.",
  },
  "/docs": {
    title: "Documentation",
    description: "Mirascope documentation and guides",
  },
};
