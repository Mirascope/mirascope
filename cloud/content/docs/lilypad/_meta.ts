import type { ProductSpec } from "@/src/lib/content/spec";
/**
 * Documentation structure for lilypad in new DocSpec format
 */
const lilypadSpec: ProductSpec = {
  product: { name: "lilypad" },
  sections: [
    {
      slug: "index",
      label: "Lilypad",
      children: [
        {
          slug: "index",
          label: "Welcome",
        },
        {
          slug: "open-source",
          label: "Open Source",
        },
        {
          slug: "getting-started",
          label: "Getting Started",
          children: [
            {
              slug: "quickstart",
              label: "Quickstart",
            },
            {
              slug: "self-hosting",
              label: "Self-Hosting",
            },
            {
              slug: "playground",
              label: "Playground",
            },
          ],
        },
        {
          slug: "observability",
          label: "Observability",
          children: [
            {
              slug: "opentelemetry",
              label: "OpenTelemetry",
            },
            {
              slug: "spans",
              label: "Spans",
            },
            {
              slug: "traces",
              label: "Traces",
            },
            {
              slug: "versioning",
              label: "Versioning",
            },
          ],
        },
        {
          slug: "evaluation",
          label: "Evaluation",
          children: [
            {
              slug: "cost-and-latency",
              label: "Cost & Latency",
            },
            {
              slug: "comparisons",
              label: "Comparisons",
            },
            {
              slug: "annotations",
              label: "Annotations",
            },
          ],
        },
      ],
    },

    {
      slug: "api",
      label: "API Reference",
      children: [
        {
          slug: "index",
          label: "Lilypad API Reference",
        },
      ],
    },
  ],
};

export default lilypadSpec;
