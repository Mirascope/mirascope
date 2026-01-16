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
      slug: "messages",
      label: "Messages",
    },
    {
      slug: "models",
      label: "Models",
    },
    {
      slug: "responses",
      label: "Responses",
    },
    {
      slug: "prompts",
      label: "Prompts",
    },
    {
      slug: "calls",
      label: "Calls",
    },
    {
      slug: "thinking",
      label: "Thinking",
    },
    {
      slug: "tools",
      label: "Tools",
    },
    {
      slug: "structured-output",
      label: "Structured Output",
    },
    {
      slug: "streaming",
      label: "Streaming",
    },
    {
      slug: "async",
      label: "Async",
    },
    {
      slug: "agents",
      label: "Agents",
    }, // TODO
    {
      slug: "context",
      label: "Context",
    },
    {
      slug: "chaining",
      label: "Chaining",
    }, // TODO
    {
      slug: "errors",
      label: "Errors",
    },
    {
      slug: "reliability",
      label: "Reliability",
    }, // TODO
    {
      slug: "providers",
      label: "Providers & Supported Features",
    }, // TODO
    {
      slug: "local-models",
      label: "Local Models",
    }, // TODO
    {
      slug: "mcp",
      label: "MCP",
    },
  ],
};

const mirascopeV2Spec: ProductSpec = {
  product: { name: "mirascope", version: "v2" },
  sections: [docsSection, api],
};

export default mirascopeV2Spec;
