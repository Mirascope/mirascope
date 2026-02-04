import {
  getDocsFromSpec,
  type DocInfo,
  type FullDocsSpec,
  type SectionSpec,
  type VersionSpec,
} from "../../cloud/app/lib/content/spec";
import api from "./api/_meta";
import guides from "./guides/_meta";
import learn from "./learn/_meta";
import v1 from "./v1/_meta";

// Welcome section - content at docs root level
const welcome: SectionSpec = {
  slug: "index", // "index" means content lives at docs root
  label: "Welcome",
  children: [
    { slug: "index", label: "Welcome" },
    { slug: "why", label: "Why Mirascope?" },
    { slug: "quickstart", label: "Mirascope Quickstart" },
    { slug: "migration", label: "Migrating to v2" },
    { slug: "contributing", label: "Contributing" },
  ],
};

// Single version with all sections including v1 as a regular section
const docs: VersionSpec = {
  sections: [welcome, learn, guides, api, v1],
};

export const docsSpec: FullDocsSpec = [docs];

export const docInfos = getDocsFromSpec(docsSpec);

const pathToDocInfo = new Map<string, DocInfo>();
for (const docInfo of docInfos) {
  pathToDocInfo.set(docInfo.path, docInfo);
}

export function getDocInfoByPath(path: string): DocInfo | undefined {
  // DocInfo.path includes "docs/" prefix, but vite plugin passes subpath without prefix
  return pathToDocInfo.get(`docs/${path}`) ?? pathToDocInfo.get(path);
}
