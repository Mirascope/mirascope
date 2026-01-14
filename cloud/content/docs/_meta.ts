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
      label: "Welcome",
    },
  ],
};

export const docsSpec: FullDocsSpec = {
  sections: [toplevelDocs, v1DocsSection, v1GuidesSection, v1ApiSection],
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
