import { LLMContent } from "@/src/lib/content/llm-content";
import LLMContainer from "./LLMContainer";
import LLMLeaf from "./LLMLeaf";

interface LLMRendererProps {
  content: LLMContent;
  level?: number;
}

export default function LLMRenderer({ content, level = 1 }: LLMRendererProps) {
  const isContainer = content.isContainer();

  if (isContainer) {
    return <LLMContainer content={content} level={level} />;
  } else {
    return <LLMLeaf content={content} />;
  }
}
