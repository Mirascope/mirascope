import { createFileRoute } from "@tanstack/react-router";
import {
  docsContentLoader,
  type DocsLoaderData,
} from "@/app/lib/content/content-loader";
import DocsPage from "@/app/components/docs-page";
import { NotFound } from "@/app/components/not-found";

export const Route = createFileRoute("/docs/v1/$")({
  ssr: false,
  head: (ctx) => {
    // todo(sebastian): simplify and add other SEO metadata
    const meta = ctx.loaderData?.meta;
    if (!meta) {
      return {
        meta: [
          { title: "Loading..." },
          { name: "description", content: "Loading documentation content" },
        ],
      };
    }
    return {
      meta: [
        { title: meta.title },
        { name: "description", content: meta.description },
      ],
    };
  },
  loader: docsContentLoader("v1"),
  component: Document,
});

function Document() {
  const doc: DocsLoaderData = Route.useLoaderData();
  if (!doc) {
    return <NotFound />;
  }
  return <DocsPage document={doc} />;
}
