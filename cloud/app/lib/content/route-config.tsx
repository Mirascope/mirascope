import type React from "react";
import { redirect, useLoaderData } from "@tanstack/react-router";
import type { Content, ContentMeta } from "@/app/lib/content/types";
import { NotFound } from "@/app/components/not-found";
import type { ModuleMap } from "./virtual-module";

/* ========== CONTENT ROUTE OPTIONS =========== */

/**
 * Options for creating a content route.
 */
export interface ContentRouteOptions<TMeta extends ContentMeta> {
  /** Function to get all metadata for this content type */
  getMeta: () => TMeta[];
  /** Module map for this content type */
  moduleMap: ModuleMap;
  /** Prefix for metadata paths (e.g., "blog", "docs", "policy") */
  prefix: string;
  /** Version segment for versioned content (e.g., "v1") */
  version?: string;
  /** Subdirectory within the content type (e.g., "terms" for policy/terms/) */
  subdirectory?: string;
  /** Fixed path for single-file content (e.g., "privacy" for policy/privacy) */
  fixedPath?: string;
  /** The page component to render when content is loaded */
  component: React.ComponentType<{ content: Content<TMeta> }>;
  /** Title to show while loading (defaults to "Loading...") */
  loadingTitle?: string;
  /** Redirect configuration for empty splat routes */
  redirectOnEmptySplat?: { to: string; params: Record<string, string> };
  /** Custom module map for testing */
  _testModuleMap?: ModuleMap;
}

/* ========== CONTENT ROUTE FACTORY =========== */

/**
 * Create route configuration for a content route.
 *
 * Use with TanStack Router's `createFileRoute`:
 *
 * @example
 * ```typescript
 * // terms.$.tsx - Subdirectory with redirect on empty splat
 * export const Route = createFileRoute("/terms/$")(
 *   createContentRouteConfig("/terms/$", {
 *     getMeta: getAllPolicyMeta,
 *     moduleMap: POLICY_MODULE_MAP,
 *     prefix: "policy",
 *     subdirectory: "terms",
 *     component: PolicyPage,
 *     redirectOnEmptySplat: { to: "/terms/$", params: { _splat: "use" } },
 *   })
 * );
 * ```
 */
export function createContentRouteConfig<TMeta extends ContentMeta>(
  path: string,
  options: ContentRouteOptions<TMeta>,
) {
  const moduleMap = options._testModuleMap ?? options.moduleMap;

  // Create the component that will render the content
  const contentComponent = createContentComponent(options.component, path);

  return {
    ssr: false as const,

    head: (ctx: { loaderData?: Content<TMeta> | undefined }) => {
      const meta = ctx.loaderData?.meta;
      if (!meta) {
        return {
          meta: [
            { title: options.loadingTitle ?? "Loading..." },
            { name: "description", content: "Loading content" },
          ],
        };
      }
      return {
        meta: [
          { title: `${meta.title} | Mirascope` },
          { name: "description", content: meta.description },
        ],
      };
    },

    loader: async (context: {
      params: Record<string, string | undefined>;
    }): Promise<Content<TMeta> | undefined> => {
      // Handle redirectOnEmpty for splat routes
      if (
        options.redirectOnEmptySplat &&
        !(context.params as { _splat?: string })._splat
      ) {
        // eslint-disable-next-line @typescript-eslint/only-throw-error
        throw redirect({
          to: options.redirectOnEmptySplat.to,
          params: options.redirectOnEmptySplat.params,
          replace: true,
        });
      }

      // Build metadata path from route params and options
      const metaPath = buildMetaPath(context.params, options);

      // Find metadata (with universal /index fallback)
      const metas = options.getMeta();
      let meta = metas.find((m) => m.path === metaPath);
      if (!meta) {
        meta = metas.find((m) => m.path === `${metaPath}/index`);
      }

      if (!meta) {
        return undefined;
      }

      // Get module key by stripping the content type prefix
      const moduleKey = meta.path.startsWith(`${options.prefix}/`)
        ? meta.path.slice(options.prefix.length + 1)
        : meta.path;

      const moduleLoader = moduleMap.get(moduleKey);
      if (!moduleLoader) {
        return undefined;
      }

      const module = await moduleLoader();
      return {
        meta,
        content: module.mdx.content,
        mdx: module.mdx,
      } as Content<TMeta>;
    },

    component: contentComponent,
  };
}

/* ========== INTERNAL HELPERS =========== */

/**
 * Build the metadata path from route params and content options.
 */
function buildMetaPath<TMeta extends ContentMeta>(
  params: Record<string, string | undefined>,
  options: ContentRouteOptions<TMeta>,
): string {
  // For fixed paths (like privacy), ignore params
  if (options.fixedPath) {
    let path = options.prefix;
    if (options.subdirectory) {
      path += `/${options.subdirectory}`;
    }
    return `${path}/${options.fixedPath}`;
  }

  // Extract path suffix from params
  const pathSuffix = params._splat ?? params.slug ?? "";

  // Build the full metadata path
  let metaPath = options.prefix;
  if (options.version) {
    metaPath += `/${options.version}`;
  }
  if (options.subdirectory) {
    metaPath += `/${options.subdirectory}`;
  }
  if (pathSuffix) {
    metaPath += `/${pathSuffix}`;
  }

  return metaPath;
}

/**
 * Create a component that loads content and renders the page component.
 */
function createContentComponent<TMeta extends ContentMeta>(
  PageComponent: React.ComponentType<{ content: Content<TMeta> }>,
  path: string,
) {
  return function ContentRouteComponent() {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const content: Content<TMeta> = useLoaderData({ from: path as any });
    if (!content) {
      return <NotFound />;
    }
    return <PageComponent content={content} />;
  };
}
