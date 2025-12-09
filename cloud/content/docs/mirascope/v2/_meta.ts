import type { ProductSpec } from "@/src/lib/content/spec";
import api from "./api/_meta";

const docsSection = {
  label: "Docs",
  slug: "index",
  weight: 2,
  children: [
    {
      slug: "index",
      label: "Welcome",
    },
    {
      slug: "examples",
      label: "Examples (For LLMs)",
    },
  ],
};

const mirascopeV2Spec: ProductSpec = {
  product: { name: "mirascope", version: "v2" },
  sections: [docsSection, api],
};

export default mirascopeV2Spec;
