import { createFileRoute, redirect } from "@tanstack/react-router";

import DocsPage from "@/app/components/docs-page";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  getAllDocsMeta,
  DOCS_MODULE_MAP,
} from "@/app/lib/content/virtual-module";

/**
 * Legacy path redirects for restructured documentation.
 * Maps old paths to new paths. These apply to paths that start with the prefix.
 */
const LEGACY_PREFIX_REDIRECTS: Record<string, string> = {
  // LLM docs moved under learn/
  llm: "learn/llm",
  // Ops docs moved under learn/
  ops: "learn/ops",
};

/**
 * Exact path redirects. Only redirect if the path matches exactly.
 */
const EXACT_REDIRECTS: Record<string, string> = {
  // API Reference root redirects to the first submodule
  api: "api/llm/calls",
  "api/llm": "api/llm/calls",
  "api/ops": "api/ops/configuration",
};

/**
 * Check if a path needs redirection (legacy prefix or exact match).
 */
function getLegacyRedirect(splatPath: string): string | null {
  // Check exact redirects first
  if (splatPath in EXACT_REDIRECTS) {
    return `/docs/${EXACT_REDIRECTS[splatPath]}`;
  }

  // Check legacy prefix redirects
  for (const [oldPrefix, newPrefix] of Object.entries(
    LEGACY_PREFIX_REDIRECTS,
  )) {
    if (splatPath === oldPrefix || splatPath.startsWith(`${oldPrefix}/`)) {
      // Replace the old prefix with the new prefix
      const newPath = splatPath.replace(oldPrefix, newPrefix);
      return `/docs/${newPath}`;
    }
  }
  return null;
}

const baseConfig = createContentRouteConfig("/docs/$", {
  getMeta: getAllDocsMeta,
  moduleMap: DOCS_MODULE_MAP,
  prefix: "docs",
  component: DocsPage,
});

export const Route = createFileRoute("/docs/$")({
  ...baseConfig,
  loader: async (context) => {
    const splatPath = (context.params as { _splat?: string })._splat ?? "";

    // Check for legacy redirects
    const redirectPath = getLegacyRedirect(splatPath);
    if (redirectPath) {
      // eslint-disable-next-line @typescript-eslint/only-throw-error
      throw redirect({
        to: redirectPath,
        replace: true,
      });
    }

    // Call the base loader
    return baseConfig.loader(context);
  },
});
