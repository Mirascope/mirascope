import { createFileRoute, useParams, useLoaderData } from "@tanstack/react-router";
import { ContentErrorHandler } from "@/src/components/core/feedback";
import { getBlogContent, type BlogContent } from "@/src/lib/content";
import { environment } from "@/src/lib/content/environment";
import { BlogPostPage } from "@/src/components/routes/blog";

/**
 * Blog content loader that directly calls getBlogContent
 */
async function blogLoader({ params }: { params: { slug: string } }) {
  try {
    return await getBlogContent(`/blog/${params.slug}`);
  } catch (error) {
    console.error(`Error loading blog: ${params.slug}`, error);
    throw error;
  }
}

// Wrapper component that connects route data to the BlogPostPage component
function BlogRoute() {
  const { slug } = useParams({ from: "/blog/$slug" });
  const post = useLoaderData({ from: "/blog/$slug", structuralSharing: false }) as BlogContent;

  return <BlogPostPage post={post} slug={slug} />;
}

export const Route = createFileRoute("/blog/$slug")({
  component: BlogRoute,

  // Use our inline loader
  loader: blogLoader,

  // Configure loading state
  pendingComponent: () => {
    // We can use a placeholder "empty" blog post for the loading state
    const { slug } = useParams({ from: "/blog/$slug" });
    const emptyPost: BlogContent = {
      meta: {
        title: "Loading...",
        date: "",
        readTime: "",
        author: "",
        lastUpdated: "",
        path: "",
        description: "Loading blog post",
        slug: slug,
        route: `/blog/${slug}`,
        type: "blog" as const,
      },
      content: "",
      mdx: {
        code: "",
        frontmatter: {},
        tableOfContents: [],
      },
    };

    return <BlogPostPage post={emptyPost} slug={slug} isLoading={true} />;
  },

  // Configure error handling
  errorComponent: ({ error }) => {
    environment.onError(error);
    return (
      <ContentErrorHandler
        error={error instanceof Error ? error : new Error(String(error))}
        contentType="blog"
      />
    );
  },
  onError: (error: Error) => environment.onError(error),
});
