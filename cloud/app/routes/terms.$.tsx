import {
  createFileRoute,
  redirect,
  type LoaderFnContext,
} from "@tanstack/react-router";
import { NotFound } from "@/app/components/not-found";
import {
  termsContentLoader,
  type PolicyLoaderData,
} from "@/app/lib/content/content-loader";
import PolicyPage from "@/app/components/policy-page";

export const Route = createFileRoute("/terms/$")({
  ssr: false,
  head: (ctx) => {
    // todo(sebastian): simplify and add other SEO metadata
    const meta = ctx.loaderData?.meta;
    if (!meta) {
      return {
        meta: [
          { title: "Loading..." },
          { name: "description", content: "Loading terms content" },
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
    ctx: LoaderFnContext<any, any, any, { _splat?: string }>,
  ): Promise<PolicyLoaderData> => {
    // Redirect on index case (no splat)
    if (!ctx.params._splat) {
      // eslint-disable-next-line @typescript-eslint/only-throw-error
      throw redirect({
        to: "/terms/$",
        params: { _splat: "use" },
        replace: true,
      });
    }
    return termsContentLoader()(ctx);
  },
  component: () => {
    const content: PolicyLoaderData = Route.useLoaderData();
    if (!content) {
      return <NotFound />;
    }
    // todo(sebastian): Port actual page
    return <PolicyPage content={content} />;
  },
});
