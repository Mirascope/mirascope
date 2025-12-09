import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { routeToFilename } from "@/src/lib/utils";
import DevLayout from "@/src/components/routes/dev/DevLayout";
import { environment } from "@/src/lib/content/environment";
import { getAllDevMeta } from "@/src/lib/content";
import { LoadingContent, ContentErrorHandler, PageMeta } from "@/src/components";

export const Route = createFileRoute("/audit-metadata")({
  component: AuditMetadata,
  loader: async () => {
    try {
      // Get all MDX-based dev pages for the sidebar
      const devPages = await getAllDevMeta();
      return { devPages };
    } catch (error) {
      console.error("Error loading dev pages:", error);
      return { devPages: [] };
    }
  },
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

interface PageMetadataItem {
  route: string;
  title: string;
  description: string | null;
  image?: string | null;
  ogTitle?: string;
  ogDescription?: string;
  ogImage?: string;
}

function AuditMetadata() {
  const { devPages } = useLoaderData({ from: "/dev/audit-metadata" });
  const [metadata, setMetadata] = useState<PageMetadataItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchMetadata() {
      try {
        const response = await fetch("/seo-metadata.json");
        if (!response.ok) {
          throw new Error(`Failed to fetch metadata: ${response.status}`);
        }
        const data = await response.json();
        setMetadata(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error occurred");
      } finally {
        setLoading(false);
      }
    }

    fetchMetadata();
  }, []);

  const content = () => {
    if (loading) {
      return <div>Loading metadata...</div>;
    }

    if (error) {
      return <div className="text-red-500">Error: {error}</div>;
    }

    // Use the metadata array directly
    const metadataItems = metadata;

    return (
      <>
        <h1 className="mb-6 text-3xl font-bold">Page Metadata Audit</h1>

        <p className="text-muted-foreground mb-6">
          This page displays all routes with their page metadata for auditing purposes.
        </p>

        <div className="space-y-6">
          {metadataItems.map((item) => (
            <div key={item.route} className="rounded-lg border p-6 shadow-sm">
              <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div className="space-y-5">
                  <div>
                    <span className="text-foreground mr-2">Route:</span>
                    <a
                      href={item.route}
                      className="font-medium break-all text-blue-600 hover:underline"
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {item.route}
                    </a>
                  </div>

                  <div>
                    <div className="text-foreground mb-1">Title:</div>
                    <div className="text-lg font-medium">{item.title}</div>
                  </div>

                  <div>
                    <div className="text-foreground mb-1">Description:</div>
                    <div className="text-lg">{item.description}</div>
                  </div>
                </div>

                <div>
                  <div className="overflow-hidden rounded border">
                    <img
                      src={`/social-cards/${routeToFilename(item.route)}.webp`}
                      alt={`Social card for ${item.route}`}
                      className="w-full"
                      onError={(e) => {
                        // Hide the image if it fails to load
                        const target = e.target as HTMLImageElement;
                        target.style.display = "none";
                        target.parentElement!.innerHTML =
                          '<div class="p-4 text-foreground italic">No social card available</div>';
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </>
    );
  };

  return (
    <>
      <PageMeta title="SEO Metadata Audit" description="Audit page metadata and social cards" />
      <DevLayout devPages={devPages}>
        <div className="container">{content()}</div>
      </DevLayout>
    </>
  );
}
