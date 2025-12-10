import { useState } from "react";
import { LLMContent } from "@/src/lib/content/llm-content";
import LLMHeader from "./LLMHeader";

interface LLMLeafProps {
  content: LLMContent;
}

export default function LLMLeaf({ content }: LLMLeafProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const sectionId = `section-${content.slug}`;

  return (
    <div
      id={sectionId}
      className="[&:not(:last-child)]:mb-4"
      style={{ scrollMarginTop: "var(--header-height)" }}
    >
      <div className="border-border border-b pb-2">
        <LLMHeader
          content={content}
          clickable={true}
          isExpanded={isExpanded}
          onToggle={() => setIsExpanded(!isExpanded)}
        />
      </div>

      {isExpanded && (
        <pre className="text-foreground overflow-auto font-mono text-sm whitespace-pre-wrap">
          {content.getContent()}
        </pre>
      )}
    </div>
  );
}
