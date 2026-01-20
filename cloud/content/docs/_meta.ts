import {
  getDocsFromSpec,
  type DocInfo,
  type FullDocsSpec,
  type VersionSpec,
} from "../../app/lib/content/spec";
import api from "./api/_meta";
import v1 from "./v1/_meta";

const v2: VersionSpec = {
  sections: [
    {
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
    },
    api,
  ],
};

export const docsSpec: FullDocsSpec = [v2, v1];

export const docInfos = getDocsFromSpec(docsSpec);

const pathToDocInfo = new Map<string, DocInfo>();
for (const docInfo of docInfos) {
  pathToDocInfo.set(docInfo.path, docInfo);
}

export function getDocInfoByPath(path: string): DocInfo | undefined {
  // DocInfo.path includes "docs/" prefix, but vite plugin passes subpath without prefix
  return pathToDocInfo.get(`docs/${path}`) ?? pathToDocInfo.get(path);
}
