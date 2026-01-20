import {
  getDocsFromSpec,
  type DocInfo,
  type FullDocsSpec,
  type SectionSpec,
} from "../../app/lib/content/spec";
import v1DocsSection from "./v1/_meta";
import v1ApiSection from "./v1/api/_meta";
import v1GuidesSection from "./v1/guides/_meta";

const toplevelDocs: SectionSpec = {
  label: "Docs",
  slug: "index",
  weight: 2,
  children: [
    {
      slug: "index",
      label: "Quickstart",
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

export const docsSpec: FullDocsSpec = {
  sections: [toplevelDocs, v1GuidesSection, v1ApiSection, v1DocsSection],
};

export const docInfos = getDocsFromSpec(docsSpec);

const pathToDocInfo = new Map<string, DocInfo>();
for (const docInfo of docInfos) {
  pathToDocInfo.set(docInfo.path, docInfo);
}

export function getDocInfoByPath(path: string): DocInfo | undefined {
  // DocInfo.path includes "docs/" prefix, but vite plugin passes subpath without prefix
  return pathToDocInfo.get(`docs/${path}`) ?? pathToDocInfo.get(path);
}
