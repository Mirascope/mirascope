import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import DevLayout from "@/src/components/routes/dev/DevLayout";
import { MDXRenderer, ContentErrorHandler, LoadingContent, PageMeta } from "@/src/components/";
import { getDevContent } from "@/src/lib/content";
import { environment } from "@/src/lib/content/environment";

export const Route = createFileRoute("/dev/$slug")({
  ssr: false, // Client-side rendered
  component: DevContentPage,
  loader: async ({ params }) => {
    const { slug } = params;
    // Get content for this specific slug
    const content = await getDevContent(slug);
    // Parent route loader already loads devPages, so we don't need to load them again
    return { content };
  },
  pendingComponent: () => {
    return (
      <DevLayout devPages={[]}>
        <div className="container py-8">
          <LoadingContent spinnerClassName="h-12 w-12" fullHeight={false} />
        </div>
      </DevLayout>
    );
  },
  errorComponent: ({ error }) => {
    environment.onError(error);
    return (
      <ContentErrorHandler
        error={error instanceof Error ? error : new Error(String(error))}
        contentType="dev"
      />
    );
  },
});

function DevContentPage() {
  // Get specific content from this route's loader
  const { content } = useLoaderData({
    from: "/dev/$slug",
    structuralSharing: false,
  });

  // Get devPages from parent route's loader
  const { devPages } = useLoaderData({
    from: "/dev",
  });

  return (
    <>
      <PageMeta title={content.meta.title} description={content.meta.description} />
      <DevLayout devPages={devPages}>
        <div className="mx-auto w-full">
          <div className="prose dark:prose-invert max-w-none">
            <MDXRenderer code={content.mdx.code} frontmatter={content.mdx.frontmatter} />
          </div>
        </div>
      </DevLayout>
    </>
  );
}

