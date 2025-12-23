import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { createPolicyLoader } from "@/app/lib/content/content";
import { environment } from "@/app/lib/content/environment";

export const Route = createFileRoute("/terms/service")({
  // Disable SSR until we work on prerendering
  ssr: false,

  component: TermsOfServicePage,

  // Use our inline policy loader
  loader: createPolicyLoader("/policy/terms/service"),

  // Configure error handling
  errorComponent: ({ error }) => <div>Error: {error.message}</div>,

  // todo(sebastian): use effect layers to manage environments?
  onError: (error: Error) => environment.onError(error),
});

function TermsOfServicePage() {
  // Access the loaded content directly
  const content = useLoaderData({
    from: "/terms/service",
    structuralSharing: false,
  });

  // todo(sebastian): add actual page and metadata
  return (
    <>
      {/* <PageMeta
        title={content?.meta?.title || "Terms of Service"}
        description={
          content?.mdx?.frontmatter?.description ||
          "Legal terms governing your use of Mirascope's platform and services."
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
