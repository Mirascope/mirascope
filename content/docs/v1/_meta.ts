// NOTE: Must use relative path instead of @/app alias because this file
// is imported by vite.config.ts during Vite's config processing phase, before
// the alias resolution is set up. Using the alias would cause module resolution errors.
import type { DocSpec, SectionSpec } from "../../../cloud/app/lib/content/spec";
import api from "./api/_meta";
import guides from "./guides/_meta";

// Docs content as a DocSpec (will be a product in the sidebar)
const docs: DocSpec = {
  label: "Docs",
  slug: "docs",
  weight: 0,
  children: [
    {
      slug: "index",
      label: "Welcome",
    },
    {
      slug: "getting-started",
      label: "Getting Started",
      children: [
        {
          slug: "why",
          label: "Why Mirascope?",
        },
        {
          slug: "help",
          label: "Help",
        },
        {
          slug: "contributing",
          label: "Contributing",
        },
        {
          slug: "migration",
          label: "0.x Migration Guide",
        },
      ],
    },
    {
      slug: "learn",
      label: "Learn",
      weight: 2,
      children: [
        {
          slug: "index",
          label: "Overview",
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
          slug: "streams",
          label: "Streams",
        },
        {
          slug: "chaining",
          label: "Chaining",
        },
        {
          slug: "response_models",
          label: "Response Models",
        },
        {
          slug: "json_mode",
          label: "JSON Mode",
        },
        {
          slug: "output_parsers",
          label: "Output Parsers",
        },
        {
          slug: "tools",
          label: "Tools",
        },
        {
          slug: "agents",
          label: "Agents",
        },
        {
          slug: "evals",
          label: "Evals",
        },
        {
          slug: "async",
          label: "Async",
        },
        {
          slug: "retries",
          label: "Retries",
        },
        {
          slug: "local_models",
          label: "Local Models",
        },
      ],
    },
    {
      slug: "learn/provider-specific",
      label: "Provider-Specific Features",
      children: [
        { slug: "thinking-and-reasoning", label: "Thinking & Reasoning" },
        {
          slug: "openai",
          label: "OpenAI",
        },
        {
          slug: "anthropic",
          label: "Anthropic",
        },
      ],
    },
    {
      slug: "learn/extensions",
      label: "Extensions",
      children: [
        {
          slug: "middleware",
          label: "Middleware",
        },
        {
          slug: "custom_provider",
          label: "Custom LLM Provider",
        },
      ],
    },
    {
      slug: "learn/mcp",
      label: "MCP - Model Context Protocol",
      children: [
        {
          slug: "client",
          label: "Client",
        },
      ],
    },
  ],
};

// v1 as a regular section with products for Docs, Guides, API
const v1: SectionSpec = {
  label: "v1 (Legacy)",
  slug: "v1",
  weight: 0,
  products: [
    { slug: "docs", label: "Docs" },
    { slug: "guides", label: "Guides" },
    { slug: "api", label: "API" },
  ],
  children: [docs, guides, api],
};

export default v1;
