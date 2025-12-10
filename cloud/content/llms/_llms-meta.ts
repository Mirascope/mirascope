import llmsFull from "./llms-full";
import llmsMirascope from "./llms-mirascope";
import llmsMirascopeV2 from "./llms-mirascope-v2";
import llmsLilypad from "./llms-lilypad";
import type { LLMContent } from "@/src/lib/content/llm-content";

const meta: LLMContent[] = [
  llmsFull,
  llmsMirascope,
  llmsLilypad,
  llmsMirascopeV2,
];

export default meta;
