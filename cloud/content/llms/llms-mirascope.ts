import { LLMContent } from "@/app/lib/content/llm-content";
import { include } from "@/app/lib/content/llm-includes";
import { MIRASCOPE } from "@/app/lib/site";

export const mirascopeContent = LLMContent.fromChildren({
  slug: "mirascope",
  title: "Mirascope",
  description: MIRASCOPE.tagline,
  route: "/docs/mirascope/llms-full",
  children: [
    // Getting Started
    include.file("mirascope/index.mdx"),
    include.file("mirascope/guides/getting-started/quickstart.mdx"),
    // Learning Mirascope
    ...include.directory("mirascope/learn"),
  ],
});

export default mirascopeContent;
