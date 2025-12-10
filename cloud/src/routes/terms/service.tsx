import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import PolicyPage, {
  PolicyPageLoading,
  PolicyPageError,
} from "@/src/components/routes/policy/PolicyPage";
import { PageMeta } from "@/src/components/";
import { createPolicyLoader } from "@/src/lib/content";
import type { PolicyContent } from "@/src/lib/content";
import { environment } from "@/src/lib/content/environment";

export const Route = createFileRoute("/terms/service")({
  ssr: false, // Client-side rendered
  component: TermsOfServicePage,

  // Use our inline policy loader
  loader: createPolicyLoader("/policy/terms/service"),

  // Configure loading state
  pendingComponent: () => <PolicyPageLoading type="terms-service" />,

  // Configure error handling
  errorComponent: ({ error }) => (
    <PolicyPageError
      type="terms-service"
      error={error instanceof Error ? error.message : String(error)}
    />
  ),
  onError: (error: Error) => environment.onError(error),
});

function TermsOfServicePage() {
  // Access the loaded content directly
  const content = useLoaderData({
    from: "/terms/service",
    structuralSharing: false,
  }) as PolicyContent;

  return (
    <>
      <PageMeta
        title={content?.meta?.title || "Terms of Service"}
        description={
          content?.mdx?.frontmatter?.description ||
          "Legal terms governing your use of Mirascope's platform and services."
        }
        type="article"
      />
      <PolicyPage content={content} type="terms-service" />
    </>
  );
}

