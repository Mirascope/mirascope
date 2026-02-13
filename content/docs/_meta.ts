import type {
  FullDocsSpec,
  VersionSpec,
} from "../../cloud/app/lib/content/spec";
import api from "./api/_meta";
import claws from "./claws/_meta";
import guides from "./guides/_meta";
import sdk from "./sdk/_meta";
import v1 from "./v1/_meta";

// Claws section - landing page for /docs
// slug "index" means content lives at docs root level (no /claws/ prefix in URL)
const docs: VersionSpec = {
  sections: [claws, guides, sdk, api, v1],
};

export const docsSpec: FullDocsSpec = [docs];
