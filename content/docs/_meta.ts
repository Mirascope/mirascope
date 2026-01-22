import {
  getDocsFromSpec,
  type DocInfo,
  type FullDocsSpec,
  type VersionSpec,
} from "../../cloud/app/lib/content/spec";
import api from "./api/_meta";
import llm from "./llm/_meta";
import ops from "./ops/_meta";
import v1 from "./v1/_meta";

const v2: VersionSpec = {
  sections: [
    {
      label: "Docs",
      slug: "index",
      weight: 3,
      children: [
        {
          slug: "index",
          label: "Quickstart",
        },
        {
          slug: "contributing",
          label: "Contributing",
        },
        llm,
        ops,
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
