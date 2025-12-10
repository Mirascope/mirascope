import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import PolicyPage, {
  PolicyPageLoading,
  PolicyPageError,
} from "@/src/components/routes/policy/PolicyPage";
import { PageMeta } from "@/src/components/";
import { createPolicyLoader } from "@/src/lib/content";
import type { PolicyContent } from "@/src/lib/content";
import { environment } from "@/src/lib/content/environment";

export const Route = createFileRoute("/privacy")({
  ssr: false, // Client-side rendered
  component: PrivacyPage,

  // Use our inline policy loader
  loader: createPolicyLoader("/policy/privacy"),

  // Configure loading state
  pendingComponent: () => <PolicyPageLoading type="privacy" />,

  // Configure error handling
  errorComponent: ({ error }) => (
    <PolicyPageError
      type="privacy"
      error={error instanceof Error ? error.message : String(error)}
    />
  ),
  onError: (error: Error) => environment.onError(error),
});

function PrivacyPage() {
  // Access the loaded content directly
  const content = useLoaderData({ from: "/privacy", structuralSharing: false }) as PolicyContent;

  return (
    <>
      <PageMeta
        title={content?.meta?.title || "Privacy Policy"}
        description={
          content?.mdx?.frontmatter?.description ||
          "How Mirascope collects, uses, and protects your personal information."
        }
        type="article"
      />
      <PolicyPage content={content} type="privacy" />
    </>
  );
}

