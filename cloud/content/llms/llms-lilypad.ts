import { LLMContent } from "@/src/lib/content/llm-content";
import { include } from "@/src/lib/content/llm-includes";
import { LILYPAD } from "@/src/lib/constants/site";

export const lilypadContent = LLMContent.fromChildren({
  slug: "lilypad",
  title: "Lilypad",
  description: LILYPAD.tagline,
  route: "/docs/lilypad/llms-full",
  children: include.flatTree("lilypad"),
});

export default lilypadContent;
