/**
 * SEO Head Generation Module
 *
 * Provides types and functions for generating SEO metadata for TanStack Router routes.
 * Can be used standalone for any route or integrated with content route configuration.
 */

import { BASE_URL } from "@/app/lib/site";

/* ========== TYPES =========== */

/**
 * Head metadata entry for routes.
 * Supports title, name-based meta tags (e.g., description),
 * property-based meta tags (e.g., og:title, twitter:card), and charset.
 */
export type HeadMetaEntry =
  | { title: string }
  | { name: string; content: string }
  | { property: string; content: string }
  | { charSet: string };

/**
 * Head link entry for routes.
 * Used for canonical URLs and other link tags.
 */
export type HeadLinkEntry = {
  rel: string;
  href: string;
};

/**
 * Head script entry for routes.
 * Used for JSON-LD structured data.
 */
export type HeadScriptEntry = {
  type: string;
  children: string;
};

/**
 * Return type for head functions.
 */
export interface HeadResult {
  meta: HeadMetaEntry[];
  links?: HeadLinkEntry[];
  scripts?: HeadScriptEntry[];
}

/**
 * Article metadata for blog posts and articles.
 */
export interface ArticleMeta {
  publishedTime?: string;
  modifiedTime?: string;
  author?: string;
}

/**
 * Options for createPageHead function.
 */
export interface PageHeadOptions {
  /** The route path (e.g., "/blog/my-post") */
  route: string;
  /** Page title (will be suffixed with " | Mirascope") */
  title: string;
  /** Page description for meta description and OG/Twitter */
  description: string;
  /** Open Graph type (defaults to "website") */
  ogType?: "website" | "article";
  /** Custom image path or URL for social cards */
  image?: string;
  /** Article metadata for blog posts */
  article?: ArticleMeta;
}

/* ========== HELPER FUNCTIONS =========== */

/**
 * Canonicalize a path by removing trailing slashes (except for root "/").
 */
export function canonicalizePath(path: string): string {
  if (path === "/") return path;
  return path.endsWith("/") ? path.slice(0, -1) : path;
}

/**
 * Convert a route path to a social card image path.
 * E.g., "/blog/my-post" -> "/social-cards/blog-my-post.webp"
 */
export function routeToImagePath(route: string): string {
  const cleanRoute = canonicalizePath(route);
  // Remove leading slash and replace remaining slashes with dashes
  const filename = cleanRoute.replace(/^\//, "").replace(/\//g, "-") || "index";
  return `/social-cards/${filename}.webp`;
}

/**
 * Generate Open Graph meta tags.
 */
export function generateOpenGraphMeta(params: {
  type: "website" | "article";
  url: string;
  title: string;
  description: string;
  image: string;
}): HeadMetaEntry[] {
  return [
    { property: "og:type", content: params.type },
    { property: "og:url", content: params.url },
    { property: "og:title", content: params.title },
    { property: "og:description", content: params.description },
    { property: "og:image", content: params.image },
  ];
}

/**
 * Generate Twitter card meta tags.
 */
export function generateTwitterMeta(params: {
  url: string;
  title: string;
  description: string;
  image: string;
}): HeadMetaEntry[] {
  return [
    { name: "twitter:card", content: "summary_large_image" },
    { name: "twitter:url", content: params.url },
    { name: "twitter:title", content: params.title },
    { name: "twitter:description", content: params.description },
    { name: "twitter:image", content: params.image },
  ];
}

/**
 * Generate article-specific meta tags.
 */
export function generateArticleMeta(article: ArticleMeta): HeadMetaEntry[] {
  const tags: HeadMetaEntry[] = [];
  if (article.publishedTime) {
    tags.push({
      property: "article:published_time",
      content: article.publishedTime,
    });
  }
  if (article.modifiedTime) {
    tags.push({
      property: "article:modified_time",
      content: article.modifiedTime,
    });
  }
  if (article.author) {
    tags.push({ property: "article:author", content: article.author });
  }
  return tags;
}

/**
 * Generate JSON-LD structured data for articles.
 */
export function generateArticleJsonLd(params: {
  title: string;
  description: string;
  url: string;
  image: string;
  article: ArticleMeta;
}): string {
  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: params.title,
    description: params.description,
    image: params.image,
    url: params.url,
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": params.url,
    },
    publisher: {
      "@type": "Organization",
      name: "Mirascope",
      logo: {
        "@type": "ImageObject",
        url: `${BASE_URL}/assets/branding/mirascope-logo.svg`,
      },
    },
  };

  if (params.article.publishedTime) {
    jsonLd.datePublished = params.article.publishedTime;
  }
  if (params.article.modifiedTime) {
    jsonLd.dateModified = params.article.modifiedTime;
  }
  if (params.article.author) {
    jsonLd.author = {
      "@type": "Person",
      name: params.article.author,
    };
  }

  return JSON.stringify(jsonLd);
}

/* ========== MAIN FUNCTION =========== */

/**
 * Create SEO head metadata for a page.
 *
 * Use directly in route definitions for standalone pages:
 *
 * @example
 * ```typescript
 * // blog.index.tsx
 * export const Route = createFileRoute("/blog/")({
 *   head: () => createPageHead({
 *     route: "/blog",
 *     title: "Blog",
 *     description: "Latest news and updates about Mirascope",
 *   }),
 *   component: BlogIndexPage,
 * });
 * ```
 *
 * @example
 * ```typescript
 * // Article with full metadata
 * export const Route = createFileRoute("/blog/$slug")({
 *   head: ({ loaderData }) => createPageHead({
 *     route: `/blog/${loaderData.slug}`,
 *     title: loaderData.title,
 *     description: loaderData.description,
 *     ogType: "article",
 *     article: {
 *       publishedTime: loaderData.date,
 *       modifiedTime: loaderData.lastUpdated,
 *       author: loaderData.author,
 *     },
 *   }),
 *   component: BlogPostPage,
 * });
 * ```
 */
export function createPageHead(options: PageHeadOptions): HeadResult {
  const {
    route,
    title,
    description,
    ogType = "website",
    image,
    article,
  } = options;

  // Build SEO values
  const pageTitle = `${title} | Mirascope`;
  const canonicalPath = canonicalizePath(route);
  const canonicalUrl = `${BASE_URL}${canonicalPath}`;

  // Compute image path - use provided image or auto-generate from route
  const imagePath = image ?? routeToImagePath(route);
  const ogImage = imagePath.startsWith("http")
    ? imagePath
    : `${BASE_URL}${imagePath}`;

  // Build meta tags array
  const metaTags: HeadMetaEntry[] = [
    { title: pageTitle },
    { name: "description", content: description },
  ];

  // Add Open Graph tags
  metaTags.push(
    ...generateOpenGraphMeta({
      type: ogType,
      url: canonicalUrl,
      title: pageTitle,
      description,
      image: ogImage,
    }),
  );

  // Add Twitter tags
  metaTags.push(
    ...generateTwitterMeta({
      url: canonicalUrl,
      title: pageTitle,
      description,
      image: ogImage,
    }),
  );

  // Add article-specific meta tags if provided
  if (article) {
    metaTags.push(...generateArticleMeta(article));
  }

  // Build links array (canonical URL)
  const links: HeadLinkEntry[] = [{ rel: "canonical", href: canonicalUrl }];

  // Build scripts array (JSON-LD for articles)
  const scripts: HeadScriptEntry[] = [];
  if (ogType === "article" && article) {
    scripts.push({
      type: "application/ld+json",
      children: generateArticleJsonLd({
        title,
        description,
        url: canonicalUrl,
        image: ogImage,
        article,
      }),
    });
  }

  return {
    meta: metaTags,
    links,
    scripts: scripts.length > 0 ? scripts : undefined,
  };
}
