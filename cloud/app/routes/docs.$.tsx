import { createFileRoute, redirect } from "@tanstack/react-router";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  getAllDocsMeta,
  DOCS_MODULE_MAP,
} from "@/app/lib/content/virtual-module";
import DocsPage from "@/app/components/docs-page";

/**
 * Legacy path redirects for restructured documentation.
 * Maps old paths to new paths.
 */
const LEGACY_REDIRECTS: Record<string, string> = {
  // LLM docs moved under learn/
  llm: "learn/llm",
  // Ops docs moved under learn/
  ops: "learn/ops",
};

/**
 * Check if a path starts with a legacy prefix and needs redirection.
 */
function getLegacyRedirect(splatPath: string): string | null {
  // Check each legacy prefix
  for (const [oldPrefix, newPrefix] of Object.entries(LEGACY_REDIRECTS)) {
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
