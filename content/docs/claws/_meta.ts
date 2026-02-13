import type { SectionSpec } from "../../../cloud/app/lib/content/spec";

const claws: SectionSpec = {
  slug: "index",
  label: "Claws",
  children: [
    { slug: "index", label: "Welcome" },
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

export default claws;
