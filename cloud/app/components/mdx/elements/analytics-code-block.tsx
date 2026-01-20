import { useRef, useMemo } from "react";
import { CodeBlock } from "@/app/components/blocks/code-block/code-block";
import { useAnalytics } from "@/app/contexts/analytics";
import { useLocation } from "@tanstack/react-router";

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
  const location = useLocation();
  const analytics = useAnalytics();
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
    const pagePath = location.pathname;
    // Use path, language and hash of code to create a stable identifier
    const itemId = `${pagePath}#${language || "code"}-${codeHash}`;
    analytics.trackEvent("select_content", {
      contentType: "code_snippet",
      itemId,
      language: language,
    });
  };

  return (
    <div
      ref={codeRef}
      data-code-hash={codeHash}
      className="analytics-code-block"
    >
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
