import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { type BlogMeta, getAllBlogMeta } from "@/src/lib/content";
import { ContentErrorHandler } from "@/src/components";
import { environment } from "@/src/lib/content/environment";
import { BlogIndexPage, BlogLoadingState } from "@/src/components/routes/blog";

/**
 * Blog list loader that fetches all blog metadata
 */
async function blogListLoader() {
  try {
    return await getAllBlogMeta();
  } catch (error) {
    console.error("Error loading blog list:", error);
    throw error;
  }
}

export const Route = createFileRoute("/blog/")({
  // Use our inline loader
  loader: blogListLoader,

  component: () => {
    // Access the loaded posts directly
    const posts = useLoaderData({ from: "/blog/", structuralSharing: false }) as BlogMeta[];
    return <BlogIndexPage posts={posts} />;
  },

  // Configure loading state using our extracted component
  pendingComponent: BlogLoadingState,

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
