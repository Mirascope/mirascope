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
    {
      slug: "configuration",
      label: "Configuration",
    },
    {
      slug: "tracing",
      label: "Tracing",
    },
    {
      slug: "sessions",
      label: "Sessions",
    },
    {
      slug: "spans",
      label: "Spans",
    },
    {
      slug: "versioning",
      label: "Versioning",
    },
    {
      slug: "instrumentation",
      label: "LLM Instrumentation",
    },
    {
      slug: "context-propagation",
      label: "Context Propagation",
    },
  ],
};

export default ops;
