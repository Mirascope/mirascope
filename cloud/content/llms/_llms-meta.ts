import llmsFull from "./llms-full";
import llmsMirascope from "./llms-mirascope";
import llmsMirascopeV2 from "./llms-mirascope-v2";
import type { LLMContent } from "@/app/lib/content/llm-content";

const meta: LLMContent[] = [llmsFull, llmsMirascope, llmsMirascopeV2];

export default meta;
