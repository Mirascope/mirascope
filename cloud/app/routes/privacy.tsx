import { createFileRoute, type LoaderFnContext } from "@tanstack/react-router";
import { NotFound } from "@/app/components/not-found";
import {
  privacyContentLoader,
  type PolicyLoaderData,
} from "@/app/lib/content/content-loader";
import PolicyPage from "@/app/components/policy-page";

export const Route = createFileRoute("/privacy")({
  ssr: false,
  head: (ctx) => {
    // todo(sebastian): simplify and add other SEO metadata
    const meta = ctx.loaderData?.meta;
    if (!meta) {
      return {
        meta: [
          { title: "Loading..." },
          { name: "description", content: "Loading privacy content" },
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
  loader: async (
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    ctx: LoaderFnContext<unknown, any, "/privacy", Record<string, never>>,
  ): Promise<PolicyLoaderData> => {
    return privacyContentLoader()(ctx);
  },
  component: () => {
    const content: PolicyLoaderData = Route.useLoaderData();
    if (!content) {
      return <NotFound />;
    }
    return <PolicyPage content={content} />;
  },
});
