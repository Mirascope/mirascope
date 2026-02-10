import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { useMemo } from "react";

import DevLayout from "@/app/components/blocks/dev/dev-layout";
import LoadingContent from "@/app/components/blocks/loading-content";
import { getAllDevMeta } from "@/app/lib/content/virtual-module";
import { createPageHead } from "@/app/lib/seo/head";

export const Route = createFileRoute("/dev/")({
  head: () =>
    createPageHead({
      route: "/dev",
      title: "Developer Tools",
      description:
        "Development tools and utilities for maintaining the Mirascope website",
    }),
  component: DevIndexPage,
  loader: () => {
    const devPages = getAllDevMeta();
    return { devPages };
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

function DevIndexPage() {
  const { devPages } = useLoaderData({ from: "/dev/" });

  const sortedDevPages = useMemo(() => {
    return [...devPages].sort((a, b) => a.title.localeCompare(b.title));
  }, [devPages]);

  return (
    <DevLayout devPages={sortedDevPages}>
      <div className="container">
        <h1 className="mb-6 text-3xl font-bold">Developer Tools</h1>

        <p className="mb-6">
          Welcome to the developer section. This area contains tools for
          developing and maintaining the website, and is hidden from
          sitemap.xml.
        </p>

        <div className="space-y-4">
          {/* Hardcoded tool routes */}
          <div className="rounded-lg border p-6 shadow-sm">
            <a href="/dev/audit-metadata" className="hover:underline">
              <h2 className="text-primary mb-2 text-xl font-semibold">
                SEO Metadata Audit
              </h2>
            </a>
            <p className="mb-4">
              View and audit SEO metadata for all website routes.
            </p>
          </div>

          <div className="rounded-lg border p-6 shadow-sm">
            <a href="/dev/social-card" className="hover:underline">
              <h2 className="text-primary mb-2 text-xl font-semibold">
                Social Card Preview
              </h2>
            </a>
            <p className="mb-4">
              Preview how social cards will look with different titles. Useful
              for iterating on the social-card.html file.
            </p>
          </div>

          <div className="rounded-lg border p-6 shadow-sm">
            <a href="/dev/layout-test" className="hover:underline">
              <h2 className="text-primary mb-2 text-xl font-semibold">
                Layout Test
              </h2>
            </a>
            <p className="mb-4">
              Test and visualize the AppLayout component with highlighted
              sections for debugging layout issues.
            </p>
          </div>

          {/* Cloud component routes */}
          <h2 className="mt-8 mb-4 text-2xl font-semibold">Cloud Components</h2>

          <div className="rounded-lg border p-6 shadow-sm">
            <a href="/dev/claw-cards" className="hover:underline">
              <h2 className="text-primary mb-2 text-xl font-semibold">
                Claw Cards
              </h2>
            </a>
            <p className="mb-4">
              All claw card variants — status colors, instance types, edge
              cases, and the full status x instance matrix.
            </p>
          </div>

          {/* Style test pages section */}
          {sortedDevPages.length > 0 && (
            <>
              <h2 className="mt-8 mb-4 text-2xl font-semibold">Style Tests</h2>
              <div className="space-y-4">
                {sortedDevPages.map((page) => (
                  <div
                    key={page.slug}
                    className="rounded-lg border p-6 shadow-sm"
                  >
                    <a href={`/dev/${page.slug}`} className="hover:underline">
                      <h2 className="text-primary mb-2 text-xl font-semibold">
                        {page.title}
                      </h2>
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
  );
}
