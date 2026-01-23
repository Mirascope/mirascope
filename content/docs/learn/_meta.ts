// NOTE: Must use relative path instead of @/app alias because this file
// is imported by vite.config.ts during Vite's config processing phase, before
// the alias resolution is set up. Using the alias would cause module resolution errors.
import type { SectionSpec } from "../../../cloud/app/lib/content/spec";
import llm from "./llm/_meta";
import ops from "./ops/_meta";

const learn: SectionSpec = {
  slug: "learn",
  label: "Learn",
  products: [
    { slug: "llm", label: "LLM" },
    { slug: "ops", label: "Ops" },
  ],
  children: [llm, ops],
};

export default learn;
