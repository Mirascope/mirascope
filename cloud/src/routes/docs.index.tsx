import { createFileRoute, Navigate } from "@tanstack/react-router";
import { getProductRoute } from "@/src/lib/routes";
import { environment } from "@/src/lib/content/environment";
import { ContentErrorHandler } from "@/src/components/";

export const Route = createFileRoute("/docs/")({
  ssr: false, // Client-side rendered
  component: DocsIndexPage,
  errorComponent: ({ error }) => {
    environment.onError(error);
    return (
      <ContentErrorHandler
        error={error instanceof Error ? error : new Error(String(error))}
        contentType="docs"
      />
    );
  },
});

/**
 * DocsIndexPage
 *
 * Default docs entry point. Redirects to the default product (Mirascope)
 */
function DocsIndexPage() {
  // Redirect to default product
  // Redirect to the Mirascope docs by default
  return <Navigate to={getProductRoute({ name: "mirascope" })} />;
}

