/**
 * Test route for MDX rendering
 *
 * Route: /docs/v1/test
 */

import { createFileRoute } from "@tanstack/react-router";
import { MDXRenderer } from "@/app/components/mdx/renderer";
import { mdx } from "@/content/docs/v1/placeholder.mdx";

export const Route = createFileRoute("/docs/v1/placeholder")({
  component: DocsTestPage,
});

function DocsTestPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mx-auto max-w-4xl">
        {/* Header with frontmatter */}
        {mdx.frontmatter.title && (
          <header className="mb-8 border-b pb-4">
            <h1 className="mb-2 text-4xl font-bold">{mdx.frontmatter.title}</h1>
            {mdx.frontmatter.description && (
              <p className="text-lg text-gray-600">
                {mdx.frontmatter.description}
              </p>
            )}
          </header>
        )}

        {/* Rendered MDX content - component imported at module level */}
        <MDXRenderer mdx={mdx} />

        {/* Debug info in development */}
        {process.env.NODE_ENV === "development" && (
          <details className="mt-8 rounded-lg bg-gray-100 p-4">
            <summary className="cursor-pointer font-semibold">
              Debug Info
            </summary>
            <div className="mt-4 space-y-2">
              <div>
                <strong>Frontmatter:</strong>
                <pre className="mt-2 overflow-x-auto rounded bg-white p-2 text-sm">
                  {JSON.stringify(mdx.frontmatter, null, 2)}
                </pre>
              </div>
              <div>
                <strong>Table of Contents:</strong>
                <pre className="mt-2 overflow-x-auto rounded bg-white p-2 text-sm">
                  {JSON.stringify(mdx.tableOfContents, null, 2)}
                </pre>
              </div>
            </div>
          </details>
        )}
      </div>
    </div>
  );
}
