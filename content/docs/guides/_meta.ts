// NOTE: Must use relative path instead of @/app alias because this file
// is imported by vite.config.ts during Vite's config processing phase, before
// the alias resolution is set up. Using the alias would cause module resolution errors.
import type { SectionSpec } from "../../../cloud/app/lib/content/spec";

const guides: SectionSpec = {
  slug: "guides",
  label: "Guides",
  children: [
    { slug: "index", label: "Overview" },
  ],
};

export default guides;
