import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import DevLayout from "@/src/components/routes/dev/DevLayout";
import { environment } from "@/src/lib/content/environment";
import { LoadingContent, ContentErrorHandler, PageMeta } from "@/src/components/";

export const Route = createFileRoute("/dev/")({
  ssr: false, // Client-side rendered
  component: DevIndexPage,
  // No loader needed since we use the parent route's loader
  pendingComponent: () => {
    return (
      <DevLayout devPages={[]}>
        <div className="container">
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

function DevIndexPage() {
  // Get devPages from parent route's loader
  const { devPages } = useLoaderData({ from: "/dev" });

  return (
    <>
      <PageMeta
        title="Developer Tools"
        description="Development and maintenance tools for the Mirascope website"
      />
      <DevLayout devPages={devPages}>
        <div className="container">
          <h1 className="mb-6 text-3xl font-bold">Developer Tools</h1>

          <p className="mb-6">
            Welcome to the developer section. This area contains tools for developing and
            maintaining the website, and is hidden from sitemap.xml.
          </p>

          <div className="space-y-4">
            {/* Hardcoded tool routes */}
            <div className="rounded-lg border p-6 shadow-sm">
              <a href="/dev/audit-metadata" className="hover:underline">
                <h2 className="text-primary mb-2 text-xl font-semibold">SEO Metadata Audit</h2>
              </a>
              <p className="mb-4">View and audit SEO metadata for all website routes.</p>
            </div>

            <div className="rounded-lg border p-6 shadow-sm">
              <a href="/dev/social-card" className="hover:underline">
                <h2 className="text-primary mb-2 text-xl font-semibold">Social Card Preview</h2>
              </a>
              <p className="mb-4">
                Preview how social cards will look with different titles. Useful for iterating on
                the social-card.html file.
              </p>
            </div>

            <div className="rounded-lg border p-6 shadow-sm">
              <a href="/dev/layout-test" className="hover:underline">
                <h2 className="text-primary mb-2 text-xl font-semibold">Layout Test</h2>
              </a>
              <p className="mb-4">
                Test and visualize the AppLayout component with highlighted sections for debugging
                layout issues.
              </p>
            </div>

            {/* Style test pages section */}
            {devPages.length > 0 && (
              <>
                <h2 className="mt-8 mb-4 text-2xl font-semibold">Style Tests</h2>
                <div className="space-y-4">
                  {devPages.map((page: { slug: string; title: string; description: string }) => (
                    <div key={page.slug} className="rounded-lg border p-6 shadow-sm">
                      <a href={`/dev/${page.slug}`} className="hover:underline">
                        <h2 className="text-primary mb-2 text-xl font-semibold">{page.title}</h2>
                      </a>
                      <p className="mb-4">{page.description}</p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </DevLayout>
    </>
  );
}

