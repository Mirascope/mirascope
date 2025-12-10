import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import PolicyPage, {
  PolicyPageLoading,
  PolicyPageError,
} from "@/src/components/routes/policy/PolicyPage";
import { PageMeta } from "@/src/components/";
import { createPolicyLoader } from "@/src/lib/content";
import type { PolicyContent } from "@/src/lib/content";
import { environment } from "@/src/lib/content/environment";

export const Route = createFileRoute("/terms/use")({
  ssr: false, // Client-side rendered
  component: TermsOfUsePage,

  // Use our inline policy loader
  loader: createPolicyLoader("/policy/terms/use"),

  // Configure loading state
  pendingComponent: () => <PolicyPageLoading type="terms-use" />,

  // Configure error handling
  errorComponent: ({ error }) => (
    <PolicyPageError
      type="terms-use"
      error={error instanceof Error ? error.message : String(error)}
    />
  ),

  onError: (error: Error) => environment.onError(error),
});

function TermsOfUsePage() {
  // Access the loaded content directly
  const content = useLoaderData({
    from: "/terms/use",
    structuralSharing: false,
  }) as PolicyContent;

  return (
    <>
      <PageMeta
        title={content?.meta?.title || "Terms of Use"}
        description={
          content?.mdx?.frontmatter?.description ||
          "Guidelines and rules for using the Mirascope website."
        }
        type="article"
      />
      <PolicyPage content={content} type="terms-use" />
    </>
  );
}
