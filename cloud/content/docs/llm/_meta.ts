import type { DocSpec } from "@/app/lib/content/spec";

const llm: DocSpec = {
  label: "LLM",
  slug: "llm",
  weight: 2,
  children: [
    {
      slug: "index",
      label: "Overview",
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
    },
    {
      slug: "context",
      label: "Context",
    },
    {
      slug: "chaining",
      label: "Chaining",
    },
    {
      slug: "errors",
      label: "Errors",
    },
    {
      slug: "reliability",
      label: "Reliability",
    },
    {
      slug: "providers",
      label: "Providers",
    },
    {
      slug: "local-models",
      label: "Local Models",
    },
    {
      slug: "mcp",
      label: "MCP",
    },
  ],
};

export default llm;
