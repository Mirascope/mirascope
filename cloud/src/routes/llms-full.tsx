import { createFileRoute, useLoaderData } from "@tanstack/react-router";
import { LLMPage } from "@/src/components/routes/llms";
import { environment } from "@/src/lib/content/environment";
import { ContentErrorHandler } from "@/src/components";
import { LLMContent } from "@/src/lib/content/llm-content";

/**
 * Loader for LLM document viewer routes
 * Handles routes like /docs/llms-full, /docs/mirascope/llms-full, etc.
 */
async function llmDocLoader() {
  // Construct paths to both JSON and TXT files
  const jsonPath = `/static/content/llms-full.json`;
  const txtPath = `/llms-full.txt`;

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
      viewerPath: `/llms-full`,
    };
  } catch (error) {
    console.error(`Error loading LLM doc: ${jsonPath}`, error);
    throw error;
  }
}

export const Route = createFileRoute("/llms-full")({
  ssr: false, // Client-side rendered
  component: LLMDocViewerPage,

  loader: llmDocLoader,

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

function LLMDocViewerPage() {
  const data = useLoaderData({
    from: "/llms-full",
    structuralSharing: false,
  });

  return <LLMPage {...data} />;
}
