import { useEffect, useState } from "react";
import LoadingContent from "@/app/components/blocks/loading-content";
import { useProvider } from "@/app/components/mdx/elements/model-provider-provider";
import { CodeBlock } from "@/app/components/blocks/code-block/code-block";

interface ProviderCodeBlockProps {
  examplePath: string; // Path relative to public/examples
  language?: string;
  className?: string;
}

/**
 * Component that displays code examples specific to the selected provider.
 * Loads and displays examples from /public/examples/{examplePath}/sdk/{lowercaseProviderName}.py
 */
export default function ProviderCodeBlock({
  examplePath,
  language = "python",
  className = "",
}: ProviderCodeBlockProps) {
  // Get the currently selected provider
  const { provider } = useProvider();

  // State for code examples and loading
  const [codeMap, setCodeMap] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);

  // Load all available provider code examples on mount
  useEffect(() => {
    async function loadProviderExamples() {
      setIsLoading(true);
      const newCodeMap: Record<string, string> = {};

      try {
        // Load the current provider's example
        const url = `/examples/${examplePath}/${provider}.py`;

        try {
          const response = await fetch(url);
          if (response.ok) {
            const text = await response.text();

            // If we get html back, it's likely a disguised 404 (returning index content)
            if (text.trim().startsWith("<!DOCTYPE html>")) {
              throw new Error(`Expected python code for ${provider}, got html`);
            } else {
              newCodeMap[provider] = text;
            }
          }
        } catch (err) {
          console.error(`Failed to load example for ${provider}:`, err);
        }

        setCodeMap(newCodeMap);
        setIsLoading(false);
      } catch (err) {
        console.error("Error loading provider examples:", err);
        setIsLoading(false);
      }
    }

    void loadProviderExamples();
  }, [examplePath, provider]);

  // Show loading state
  if (isLoading) {
    return (
      <div className={`my-4 ${className}`}>
        <LoadingContent spinnerClassName="h-8 w-8" fullHeight={false} />
      </div>
    );
  }

  // Find the code for the current provider
  const currentProviderCode = codeMap[provider];

  // Display the code with the Info callout component
  return (
    <>
      {!currentProviderCode && (
        <div className="bg-destructive/20 text-destructive mb-2 px-4 py-2 text-sm">
          Example for {provider} not available yet.
        </div>
      )}
      {currentProviderCode && (
        <CodeBlock code={currentProviderCode} language={language} />
      )}
    </>
  );
}
