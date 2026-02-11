import * as fs from "node:fs";
import * as path from "node:path";
import { describe, expect, it } from "vitest";

import { RESERVED_ORG_SLUGS } from "@/db/slug";

import { ADDITIONAL_STATIC_SEGMENTS, isCloudAppRoute } from "./route-utils";

/**
 * Derive top-level static route segments from the file-based route directory.
 *
 * TanStack Router file-based routing uses the `routes/` directory. Each
 * top-level file or directory (excluding `$orgSlug`, `__root`, and `index`)
 * corresponds to a static route segment.
 */
function getStaticRouteSegments(): Set<string> {
  const routesDir = path.resolve(__dirname, "../routes");
  const entries = fs.readdirSync(routesDir);
  const segments = new Set<string>();

  for (const entry of entries) {
    // Skip dynamic params, root layout, and index
    if (
      entry.startsWith("$") ||
      entry.startsWith("__") ||
      entry === "index.tsx"
    ) {
      continue;
    }

    // Extract the first segment: "blog.index.tsx" -> "blog", "api.v2.$.tsx" -> "api"
    const segment = entry.split(".")[0];
    if (segment) {
      segments.add(segment);
    }
  }

  return segments;
}

describe("route-utils static segment coverage", () => {
  const combinedSet = new Set([
    ...RESERVED_ORG_SLUGS,
    ...ADDITIONAL_STATIC_SEGMENTS,
  ]);
  const routeSegments = getStaticRouteSegments();

  it("every TanStack Router static route segment is in the combined set", () => {
    const missing: string[] = [];
    for (const segment of routeSegments) {
      if (!combinedSet.has(segment)) {
        missing.push(segment);
      }
    }
    expect(
      missing,
      `Static route segments missing from RESERVED_ORG_SLUGS or ADDITIONAL_STATIC_SEGMENTS: ${missing.join(", ")}`,
    ).toEqual([]);
  });

  it("isCloudAppRoute returns false for all static route segments", () => {
    for (const segment of routeSegments) {
      expect(
        isCloudAppRoute(`/${segment}`),
        `/${segment} should not be a cloud app route`,
      ).toBe(false);
    }
  });

  it("isCloudAppRoute returns true for org-slug-like paths", () => {
    expect(isCloudAppRoute("/my-org")).toBe(true);
    expect(isCloudAppRoute("/my-org/claws")).toBe(true);
  });

  it("isCloudAppRoute returns false for root", () => {
    expect(isCloudAppRoute("/")).toBe(false);
  });
});
