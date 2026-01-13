import type { LoaderFnContext, AnyRoute } from "@tanstack/react-router";
import type {
  BlogContent,
  BlogMeta,
  DocContent,
  DocMeta,
} from "@/app/lib/content/types";
import type { ProcessedMDX } from "@/app/lib/mdx/types";
import {
  BLOG_MODULE_MAP,
  DOCS_MODULE_MAP,
  getAllBlogMeta,
  getAllDocsMeta,
  type ModuleMap,
} from "./virtual-module";

/**
 * Config for making a content loader by type.
 */
interface ContentLoaderConfig<
  TMeta,
  TParams extends Record<string, string>,
  TContent,
> {
  /** Function to get all metadata for this content type */
  getMeta: () => TMeta[];
  /** Extract the lookup key from route params */
  extractKey: (params: TParams) => string;
  /** Find metadata matching the extracted key (validates against allow list) */
  findMeta: (metas: TMeta[], key: string) => TMeta | undefined;
  /** Get the module map key from metadata (for looking up the MDX loader) */
  getModuleKey: (meta: TMeta, params: TParams) => string;
  /** Build the final content object from metadata and loaded MDX */
  buildContent: (meta: TMeta, mdx: ProcessedMDX) => TContent;
}

/**
 * Create a generic, type-safe content loader for TanStack Router.
 *
 * @param moduleMap - Map from content key to module loader
 * @param config - Content-type-specific configuration
 */
function createContentLoader<
  TMeta,
  TParams extends Record<string, string>,
  TContent,
>(moduleMap: ModuleMap, config: ContentLoaderConfig<TMeta, TParams, TContent>) {
  return async function loader(
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    context: LoaderFnContext<any, AnyRoute, any, TParams>,
  ): Promise<TContent | undefined> {
    // Type assertion needed due to TanStack Router's complex param type expansion
    const key = config.extractKey(context.params as TParams);

    const metas = config.getMeta();

    // Validate key against allow list (security: prevents path traversal)
    const meta = config.findMeta(metas, key);
    if (!meta) {
      return undefined;
    }

    const moduleKey = config.getModuleKey(meta, context.params as TParams);
    const moduleLoader = moduleMap.get(moduleKey);
    if (!moduleLoader) {
      return undefined;
    }

    const module = await moduleLoader();
    return config.buildContent(meta, module.mdx);
  };
}

/* ========== BLOG CONTENT LOADER =========== */

/**
 * Type for the data returned by blogPostContentLoader.
 */
export type BlogPostLoaderData = BlogContent | undefined;

/**
 * Blog post content loader (supports custom module map for testing).
 *
 * @param moduleMap - Optional custom module map (for testing)
 */
export function blogPostContentLoader(moduleMap?: ModuleMap) {
  const effectiveModuleMap = moduleMap ?? BLOG_MODULE_MAP;

  return createContentLoader<BlogMeta, { slug: string }, BlogContent>(
    effectiveModuleMap,
    {
      getMeta: getAllBlogMeta,
      extractKey: (params) => params.slug,
      findMeta: (metas, slug) => metas.find((m) => m.slug === slug),
      getModuleKey: (meta) => meta.slug,
      buildContent: (meta, mdx) => ({ meta, content: mdx.content, mdx }),
    },
  );
}

/* ========== DOCS CONTENT LOADER =========== */

/**
 * Type for the data returned by docsContentLoader.
 */
export type DocsLoaderData = DocContent | undefined;

/**
 * Docs content loader (supports custom module map for testing).
 *
 * @param version - Optional docs version (e.g., "v1"). If omitted, loads non-versioned docs.
 * @param moduleMap - Optional custom module map (for testing)
 */
export function docsContentLoader(version?: string, moduleMap?: ModuleMap) {
  const effectiveModuleMap = moduleMap ?? DOCS_MODULE_MAP;

  return createContentLoader<DocMeta, { _splat?: string }, DocContent>(
    effectiveModuleMap,
    {
      getMeta: getAllDocsMeta,
      extractKey: (params) => {
        // Build path with "docs/" prefix to match DocInfo.path format
        const basePath = version ? `docs/${version}` : "docs";
        return `${basePath}${params._splat ? `/${params._splat}` : ""}`;
      },
      findMeta: (metas, path) => {
        // First try exact match
        const exactMatch = metas.find((m) => m.path === path);
        if (exactMatch) {
          return exactMatch;
        }
        // For index pages, the URL won't include "/index" but the metadata path will
        // e.g., URL "/docs/v1/guides" -> metadata path "docs/v1/guides/index"
        return metas.find((m) => m.path === `${path}/index`);
      },
      getModuleKey: (meta) => {
        // Strip "docs/" prefix to get the module key (file path relative to content/docs/)
        const prefix = "docs/";
        return meta.path.startsWith(prefix)
          ? meta.path.slice(prefix.length)
          : meta.path;
      },
      buildContent: (meta, mdx) => ({ meta, content: mdx.content, mdx }),
    },
  );
}
