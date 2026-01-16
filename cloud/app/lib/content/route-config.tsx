import type React from "react";
import { redirect, useLoaderData } from "@tanstack/react-router";
import type { ErrorComponentProps } from "@tanstack/react-router";
import type { BlogMeta, Content, ContentMeta } from "@/app/lib/content/types";
import { NotFound } from "@/app/components/not-found";
import { DefaultCatchBoundary } from "@/app/components/error/default-catch-boundary";
import LoadingContent from "@/app/components/blocks/loading-content";
import type { ModuleMap } from "./virtual-module";
import {
  createPageHead,
  canonicalizePath,
  routeToImagePath,
  generateOpenGraphMeta,
  generateTwitterMeta,
  generateArticleMeta,
  generateArticleJsonLd,
  type HeadMetaEntry,
  type HeadLinkEntry,
  type HeadScriptEntry,
  type HeadResult,
} from "@/app/lib/seo/head";
import { BASE_URL } from "@/app/lib/site";
import { compileMDXContent } from "./mdx-compile";

// Re-export types for consumers
export type { HeadMetaEntry, HeadLinkEntry, HeadScriptEntry, HeadResult };

// Re-export createPageHead for standalone usage
export { createPageHead };

/* ========== CONTENT ROUTE CONFIG =========== */

/**
 * Return type of createContentRouteConfig.
 * Defines the shape expected by TanStack Router's createFileRoute.
 */
export interface ContentRouteConfig<TMeta extends ContentMeta> {
  head: (ctx: {
    match: { pathname: string };
    loaderData?: Content<TMeta> | undefined;
  }) => HeadResult;
  loader: (context: {
    params: Record<string, string | undefined>;
  }) => Promise<Content<TMeta> | undefined>;
  component: () => React.JSX.Element;
  pendingComponent: () => React.JSX.Element;
  errorComponent: (props: ErrorComponentProps) => React.JSX.Element;
}

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
  /** Redirect configuration for empty splat routes */
  redirectOnEmptySplat?: { to: string; params: Record<string, string> };
  /** Custom module map for testing */
  _testModuleMap?: ModuleMap;

  /* ========== SEO OPTIONS =========== */

  /** Content type for Open Graph (defaults to "website") */
  ogType?: "website" | "article";
  /** Function to generate social card image path from meta */
  getImagePath?: (meta: TMeta) => string;
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
): ContentRouteConfig<TMeta> {
  const allMetas = options.getMeta();
  const moduleMap = options._testModuleMap ?? options.moduleMap;

  // Create the component that will render the content
  const contentComponent = createContentComponent(options.component, path);

  return {
    head: createContentHead<TMeta>({
      allMetas,
      ogType: options.ogType,
      getImagePath: options.getImagePath,
    }),

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
      let meta = allMetas.find((m) => m.path === metaPath);
      if (!meta) {
        meta = allMetas.find((m) => m.path === `${metaPath}/index`);
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

      const preprocessedMdx = (await moduleLoader()).default;
      const code = await compileMDXContent(preprocessedMdx.content);

      return {
        meta,
        content: preprocessedMdx.content,
        mdx: {
          frontmatter: preprocessedMdx.frontmatter,
          tableOfContents: preprocessedMdx.tableOfContents,
          content: preprocessedMdx.content, // Raw MDX for search/display
          code, // Compiled JSX for runtime evaluation
        },
      } satisfies Content<TMeta>;
    },

    component: contentComponent,
    // todo(sebastian): add the pending component
    pendingComponent: () => <LoadingContent />,
    // todo(sebastian): add the error component
    errorComponent: DefaultCatchBoundary,
  };
}

/* ========== INTERNAL HELPERS =========== */

/**
 * Type guard to check if metadata is BlogMeta (has article-specific fields).
 */
function isBlogMeta(meta: ContentMeta): meta is BlogMeta {
  return meta.type === "blog" && "author" in meta && "date" in meta;
}

/**
 * SEO options for createContentHead function.
 */
interface CreateContentHeadOptions<TMeta extends ContentMeta> {
  allMetas: TMeta[];
  ogType?: "website" | "article";
  getImagePath?: (meta: TMeta) => string;
}

/**
 * Create a head function for content routes that looks up metadata by route.
 *
 * This is a specialized wrapper around createPageHead that:
 * - Looks up content metadata by route path
 * - Auto-detects article type for blog posts
 * - Generates article JSON-LD for blog content
 */
function createContentHead<TMeta extends ContentMeta>(
  options: CreateContentHeadOptions<TMeta>,
) {
  const { allMetas, ogType = "website", getImagePath } = options;

  return (ctx: {
    match: { pathname: string };
    loaderData?: Content<TMeta> | undefined;
  }): HeadResult => {
    const route = ctx.match.pathname;
    const meta = allMetas.find((m) => m.route === route);

    if (!meta) {
      console.warn(`Content meta data not found for route: ${route}`);
      return { meta: [], links: [] };
    }

    // Build SEO values
    const pageTitle = `${meta.title} | Mirascope`;
    const canonicalPath = canonicalizePath(meta.route);
    const canonicalUrl = `${BASE_URL}${canonicalPath}`;

    // Compute image path - use custom function or auto-generate from route
    const imagePath = getImagePath
      ? getImagePath(meta)
      : routeToImagePath(meta.route);
    const ogImage = imagePath.startsWith("http")
      ? imagePath
      : `${BASE_URL}${imagePath}`;

    // Determine actual OG type based on content
    const actualOgType = isBlogMeta(meta) ? "article" : ogType;

    // Build meta tags array
    const metaTags: HeadMetaEntry[] = [
      { title: pageTitle },
      { name: "description", content: meta.description },
    ];

    // Add Open Graph tags
    metaTags.push(
      ...generateOpenGraphMeta({
        type: actualOgType,
        url: canonicalUrl,
        title: pageTitle,
        description: meta.description,
        image: ogImage,
      }),
    );

    // Add Twitter tags
    metaTags.push(
      ...generateTwitterMeta({
        url: canonicalUrl,
        title: pageTitle,
        description: meta.description,
        image: ogImage,
      }),
    );

    // Add article-specific meta tags for blog posts
    if (isBlogMeta(meta)) {
      metaTags.push(
        ...generateArticleMeta({
          publishedTime: meta.date,
          modifiedTime: meta.lastUpdated,
          author: meta.author,
        }),
      );
    }

    // Build links array (canonical URL)
    const links: HeadLinkEntry[] = [{ rel: "canonical", href: canonicalUrl }];

    // Build scripts array (JSON-LD for articles)
    const scripts: HeadScriptEntry[] = [];
    if (isBlogMeta(meta)) {
      scripts.push({
        type: "application/ld+json",
        children: generateArticleJsonLd({
          title: meta.title,
          description: meta.description,
          url: canonicalUrl,
          image: ogImage,
          article: {
            publishedTime: meta.date,
            modifiedTime: meta.lastUpdated,
            author: meta.author,
          },
        }),
      });
    }

    return {
      meta: metaTags,
      links,
      scripts: scripts.length > 0 ? scripts : undefined,
    };
  };
}

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
    // eslint-disable-next-line @typescript-eslint/no-explicit-any, @typescript-eslint/no-unsafe-argument
    const content = useLoaderData({ from: path } as any);
    if (!content) {
      return <NotFound />;
    }
    return <PageComponent content={content} />;
  };
}
