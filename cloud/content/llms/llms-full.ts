import { LLMContent } from "@/src/lib/content/llm-content";
import { mirascopeContent } from "./llms-mirascope";
import { lilypadContent } from "./llms-lilypad";

// Create the full document with both sections
const fullContent = LLMContent.fromChildren({
  slug: "llms-full",
  title: "llms-full.txt",
  description:
    "Concatenated documentation for Mirascope and Lilypad, intended to get LLMs up to speed on both products.",
  route: "/llms-full",
  children: [mirascopeContent, lilypadContent],
});

// Export content (ToC is generated dynamically in getContent())
export default fullContent;
