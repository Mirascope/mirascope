import {
  getDocsFromSpec,
  type DocInfo,
  type FullDocsSpec,
} from "../../app/lib/content/spec";
import v1DocsSection from "./v1/_meta";
import v1ApiSection from "./v1/api/_meta";
import v1GuidesSection from "./v1/guides/_meta";

export const docsSpec: FullDocsSpec = {
  sections: [v1DocsSection, v1ApiSection, v1GuidesSection],
};

export const docInfos = getDocsFromSpec(docsSpec);

const pathToDocInfo = new Map<string, DocInfo>();
for (const docInfo of docInfos) {
  pathToDocInfo.set(docInfo.path, docInfo);
}

export function getDocInfoByPath(path: string): DocInfo | undefined {
  return pathToDocInfo.get(path);
}
