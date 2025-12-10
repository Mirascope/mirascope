import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { LLMPage } from "@/src/components/routes/llms";
import { environment } from "@/src/lib/content/environment";
import { ContentErrorHandler } from "@/src/components";
import { LLMContent } from "@/src/lib/content/llm-content";
import DocsSidebar from "@/src/components/routes/docs/DocsSidebar";
import { ButtonLink } from "@/mirascope-ui/ui/button-link";
import { type Product } from "@/src/lib/content/spec";
/**
 * Hack: custom route for mirascope/v2/llms-full.txt
 * TODO: Dedup this with docs.$product.llms-full.txt
 */
async function mirascopeV2LlmLoader() {
  const jsonPath = `/static/content/docs/mirascope/v2/llms-full.json`;
  const txtPath = `/docs/mirascope/v2/llms-full.txt`;

  try {
    // Fetch the processed JSON data
    const response = await environment.fetch(jsonPath);

    if (!response.ok) {
      throw new Error(`LLM document not found: ${jsonPath}`);
    }

    const data = await response.json();
    const content = LLMContent.fromJSON(data);

    return {
      content,
      txtPath,
      viewerPath: `/docs/mirascope/v2/llms`,
    };
  } catch (error) {
    console.error(`Error loading LLM doc: ${jsonPath}`, error);
    throw error;
  }
}

export const Route = createFileRoute("/docs/mirascope/v2/llms-full")({
  ssr: false, // Client-side rendered
  component: ProductLLMDocViewerPage,

  loader: mirascopeV2LlmLoader,

  pendingComponent: () => {
    return <div>Loading LLM document...</div>;
  },

  errorComponent: ({ error }) => {
    environment.onError(error);
    return (
      <ContentErrorHandler
        error={error instanceof Error ? error : new Error(String(error))}
        contentType="llm-docs"
      />
    );
  },
});

function ProductLLMDocViewerPage() {
  const data = useLoaderData({
    from: "/docs/mirascope/v2/llms-full",
    structuralSharing: false,
  });

  const { content, txtPath } = data;
  const product: Product = { name: "mirascope", version: "v2" };

  return (
    <LLMPage
      content={content}
      txtPath={txtPath}
      leftSidebar={<DocsSidebar product={product} />}
      rightSidebarExtra={
        <ButtonLink variant="outline" href="/llms-full">
          Cross-Product LLM Docs
        </ButtonLink>
      }
    />
  );
}
