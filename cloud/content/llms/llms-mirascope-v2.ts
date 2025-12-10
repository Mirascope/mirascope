import { LLMContent } from "@/src/lib/content/llm-content";
import { include } from "@/src/lib/content/llm-includes";
import { MIRASCOPE } from "@/src/lib/constants/site";

export const mirascopeContent = LLMContent.fromChildren({
  slug: "mirascope-version2",
  title: "Mirascope V2",
  description: MIRASCOPE.tagline,
  route: "/docs/mirascope/v2/llms-full",
  children: [include.file("mirascope/v2/index.mdx")],
});

export default mirascopeContent;
