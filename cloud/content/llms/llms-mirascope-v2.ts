import { LLMContent } from "@/app/lib/content/llm-content";
import { include } from "@/app/lib/content/llm-includes";
import { MIRASCOPE } from "@/app/lib/site";

export const mirascopeContent = LLMContent.fromChildren({
  slug: "mirascope-version2",
  title: "Mirascope V2",
  description: MIRASCOPE.tagline,
  route: "/docs/mirascope/v2/llms-full",
  children: [include.file("mirascope/v2/index.mdx")],
});

export default mirascopeContent;
