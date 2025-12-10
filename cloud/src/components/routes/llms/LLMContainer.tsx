import { LLMContent } from "@/src/lib/content/llm-content";
import LLMRenderer from "./LLMRenderer";
import LLMHeader from "./LLMHeader";

interface LLMContainerProps {
  content: LLMContent;
  level?: number;
}

export default function LLMContainer({
  content,
  level = 1,
}: LLMContainerProps) {
  const sectionId = `section-${content.slug}`;

  return (
    <div key={sectionId}>
      <div
        id={sectionId}
        className="border-border mb-6 border-b pt-2"
        style={{ scrollMarginTop: "var(--header-height)" }}
      >
        <LLMHeader content={content} level={level} />
      </div>

      {/* Render children */}
      {content.getChildren().map((child) => (
        <LLMRenderer key={child.slug} content={child} level={level + 1} />
      ))}
    </div>
  );
}
