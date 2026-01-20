import type { DocSpec } from "@/app/lib/content/spec";

const ops: DocSpec = {
  label: "Ops",
  slug: "ops",
  weight: 1,
  children: [
    {
      slug: "index",
      label: "Overview",
    },
    // Additional docs will be added in PR 2
  ],
};

export default ops;
