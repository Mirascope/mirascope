import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { Info } from "lucide-react";

import DevLayout from "@/app/components/blocks/dev/dev-layout";
import LoadingContent from "@/app/components/blocks/loading-content";
import { Alert, AlertDescription } from "@/app/components/ui/alert";
import {
  getAllContentMeta,
  getAllDevMeta,
} from "@/app/lib/content/virtual-module";
import { createPageHead } from "@/app/lib/seo/head";

/**
 * Convert a route path to a filename for social cards.
 * E.g., "/blog/my-post" -> "blog-my-post"
 */
function routeToFilename(route: string): string {
  const cleanRoute = route.endsWith("/") ? route.slice(0, -1) : route;
  return cleanRoute.replace(/^\//, "").replace(/\//g, "-") || "index";
}

export const Route = createFileRoute("/dev/audit-metadata")({
  head: () =>
    createPageHead({
      route: "/dev/audit-metadata",
      title: "Developer Tools - SEO Metadata Audit",
      description: "Audit page metadata and social cards",
    }),
  component: AuditMetadata,
  loader: () => {
    const devPages = getAllDevMeta();
    const allContent = getAllContentMeta();
    return { devPages, allContent };
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
});

function AuditMetadata() {
  const { devPages, allContent } = useLoaderData({
    from: "/dev/audit-metadata",
  });

  const sortedContent = [...allContent].sort((a, b) => {
    const lengthDiff = a.route.length - b.route.length;
    if (lengthDiff !== 0) return lengthDiff;
    const slugCompare = a.slug.localeCompare(b.slug);
    if (slugCompare !== 0) return slugCompare;
    return a.title.localeCompare(b.title);
  });

  return (
    <DevLayout devPages={devPages}>
      <div className="container">
        <h1 className="mb-6 text-3xl font-bold">Page Metadata Audit</h1>

        <p className="text-muted-foreground mb-4">
          This page displays all routes with their page metadata for auditing
          purposes.
        </p>

        <Alert className="mb-6">
          <Info className="h-4 w-4" />
          <AlertDescription>
            Social cards require a build to generate — run{" "}
            <code className="text-sm text-accent font-bold">bun run build</code>{" "}
            if images are missing in dev.
          </AlertDescription>
        </Alert>

        <div className="space-y-6">
          {sortedContent.map((item) => (
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
                        if (target.parentElement) {
                          target.parentElement.innerHTML =
                            '<div class="p-4 text-foreground italic">No social card available</div>';
                        }
                      }}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </DevLayout>
  );
}
