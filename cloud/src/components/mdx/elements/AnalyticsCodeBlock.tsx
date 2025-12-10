import { useRef, useMemo } from "react";
import { CodeBlock } from "@/mirascope-ui/blocks/code-block/code-block";
import { useProduct } from "@/src/components/core";
import analyticsManager from "@/src/lib/services/analytics";

interface AnalyticsCodeBlockProps {
  code: string;
  language?: string;
  meta?: string;
  className?: string;
  showLineNumbers?: boolean;
}

export function AnalyticsCodeBlock({
  code,
  language,
  meta,
  className,
  showLineNumbers,
}: AnalyticsCodeBlockProps) {
  const product = useProduct();
  const codeRef = useRef<HTMLDivElement>(null);

  // Create a stable identifier for this code block based on its content
  // This ensures the ID remains consistent across rerenders
  const codeHash = useMemo(() => {
    // Simple hash function for the code content
    let hash = 0;
    for (let i = 0; i < code.length; i++) {
      const char = code.charCodeAt(i);
      hash = (hash << 5) - hash + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(16).substring(0, 8);
  }, [code]);

  const onCopy = () => {
    const pagePath = window.location.pathname;
    // Use path, language and hash of code to create a stable identifier
    const itemId = `${pagePath}#${language || "code"}-${codeHash}`;

    analyticsManager.trackCopyEvent({
      contentType: "code_snippet",
      itemId,
      product,
      language: language || "text",
    });
  };

  return (
    <div ref={codeRef} data-code-hash={codeHash} className="analytics-code-block">
      <CodeBlock
        code={code}
        language={language}
        meta={meta}
        className={className}
        showLineNumbers={showLineNumbers}
        onCopy={onCopy}
      />
    </div>
  );
}
