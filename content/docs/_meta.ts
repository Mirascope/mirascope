import type {
  FullDocsSpec,
  SectionSpec,
  VersionSpec,
} from "../../cloud/app/lib/content/spec";
import api from "./api/_meta";
import guides from "./guides/_meta";
import sdk from "./sdk/_meta";
import v1 from "./v1/_meta";

// Claws section - landing page for /docs
// slug "index" means content lives at docs root level
const claws: SectionSpec = {
  slug: "claws",
  label: "Claws",
  children: [
    { slug: "index", label: "Welcome" },
    { slug: "why", label: "Why Claws?" },
    { slug: "quickstart", label: "Quickstart" },
    { slug: "configuration", label: "Configuration" },
    { slug: "channels", label: "Channels" },
    { slug: "skills", label: "Skills" },
    { slug: "memory", label: "Memory & Context" },
    { slug: "tools", label: "Tools" },
    { slug: "deployment", label: "Deployment" },
    { slug: "contributing", label: "Contributing" },
  ],
};

const docs: VersionSpec = {
  sections: [claws, guides, sdk, api, v1],
};

export const docsSpec: FullDocsSpec = [docs];
