import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { createPolicyLoader } from "@/app/lib/content/content";
import { environment } from "@/app/lib/content/environment";

export const Route = createFileRoute("/terms/use")({
  // Disable SSR until we work on prerendering
  ssr: false,

  component: TermsOfUsePage,

  // Use our inline policy loader
  loader: createPolicyLoader("/policy/terms/use"),

  // Configure error handling
  errorComponent: ({ error }) => <div>Error: {error.message}</div>,

  // todo(sebastian): use effect layers to manage environments?
  onError: (error: Error) => environment.onError(error),
});

function TermsOfUsePage() {
  // Access the loaded content directly
  const content = useLoaderData({
    from: "/terms/use",
    structuralSharing: false,
  });

  // todo(sebastian): add actual page and metadata
  return (
    <>
      {/* <PageMeta
        title={content?.meta?.title || "Terms of Use"}
        description={
          content?.mdx?.frontmatter?.description ||
          "Guidelines and rules for using the Mirascope website."
        }
        type="article"
      /> */}
      <div>
        <h1>{content?.meta?.title}</h1>
        <div>{content?.content}</div>
      </div>
    </>
  );
}
