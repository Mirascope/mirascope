import { BASE_URL, PRODUCT_CONFIGS } from "@/src/lib/constants/site";
import { useRouterState } from "@tanstack/react-router";
import { routeToFilename, canonicalizePath } from "@/src/lib/utils";
import { isHiddenRoute } from "@/src/lib/hidden-routes";
import { RouteMeta } from "./RouteMeta";
import type { ProductName } from "@/src/lib/content/spec";
export interface PageMetaProps {
  title?: string;
  description?: string;
  image?: string;
  type?: "website" | "article";
  product?: ProductName;
  robots?: string;
  article?: {
    publishedTime?: string;
    modifiedTime?: string;
    author?: string;
    tags?: string[];
  };
}

// Helper function to convert a route path to a consistent image path
export function routeToImagePath(route: string): string {
  const filename = routeToFilename(route);
  return `/social-cards/${filename}.webp`;
}

export function PageMeta(props: PageMetaProps) {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const {
    title,
    description,
    image,
    type = "website",
    product,
    article,
    robots,
  } = props;

  // Calculate metadata values
  const siteTitle = product ? `${PRODUCT_CONFIGS[product].title}` : "Mirascope";
  const pageTitle = title ? `${title} | ${siteTitle}` : siteTitle;

  // Auto-set noindex/nofollow for hidden routes (can be overridden by explicit robots prop)
  const computedRobots =
    robots ?? (isHiddenRoute(currentPath) ? "noindex, nofollow" : undefined);

  // Generate image path if not provided
  const computedImage = image || routeToImagePath(currentPath);

  // Create canonical URL following NTS rule (no trailing slash except homepage)
  const canonicalPath = canonicalizePath(currentPath);
  const canonicalUrl = `${BASE_URL}${canonicalPath}`;

  // Create absolute image URL
  const ogImage = computedImage.startsWith("http")
    ? computedImage
    : `${BASE_URL}${computedImage}`;

  return (
    <RouteMeta>
      <title>{pageTitle}</title>
      {description && <meta name="description" content={description} />}
      {computedRobots && <meta name="robots" content={computedRobots} />}

      {/* Canonical URL - self-referencing to prevent duplicate content issues */}
      <link rel="canonical" href={canonicalUrl} />

      {/* Article schema as JSON-LD */}
      {type === "article" && article && (
        <script type="application/ld+json">
          {JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            headline: title,
            description: description,
            image: ogImage,
            url: canonicalUrl,
            mainEntityOfPage: {
              "@type": "WebPage",
              "@id": canonicalUrl,
            },
            publisher: {
              "@type": "Organization",
              name: siteTitle,
              logo: {
                "@type": "ImageObject",
                url: `${BASE_URL}/assets/branding/mirascope-logo.svg`,
              },
            },
            ...(article.publishedTime
              ? { datePublished: article.publishedTime }
              : {}),
            ...(article.modifiedTime
              ? { dateModified: article.modifiedTime }
              : {}),
            ...(article.author
              ? {
                  author: {
                    "@type": "Person",
                    name: article.author,
                  },
                }
              : {}),
          })}
        </script>
      )}

      {/* Open Graph / Facebook */}
      <meta property="og:type" content={type} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:title" content={pageTitle} />
      {description && <meta property="og:description" content={description} />}
      <meta property="og:image" content={ogImage} />

      {/* Twitter */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:url" content={canonicalUrl} />
      <meta name="twitter:title" content={pageTitle} />
      {description && <meta name="twitter:description" content={description} />}
      <meta name="twitter:image" content={ogImage} />

      {/* Article specific metadata */}
      {type === "article" && article?.publishedTime && (
        <meta
          property="article:published_time"
          content={article.publishedTime}
        />
      )}
      {type === "article" && article?.modifiedTime && (
        <meta property="article:modified_time" content={article.modifiedTime} />
      )}
      {type === "article" && article?.author && (
        <meta property="article:author" content={article.author} />
      )}
      {type === "article" &&
        article?.tags &&
        article.tags.map((tag, index) => (
          <meta key={`tag-${index}`} property="article:tag" content={tag} />
        ))}
    </RouteMeta>
  );
}

export default PageMeta;
