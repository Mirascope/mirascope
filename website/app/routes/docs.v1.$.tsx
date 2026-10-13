import { createFileRoute } from "@tanstack/react-router";

import DocsPage from "@/app/components/docs-page";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  DOCS_MODULE_MAP,
  getAllDocsMeta,
} from "@/app/lib/content/virtual-module";

export const Route = createFileRoute("/docs/v1/$")(
  createContentRouteConfig("/docs/v1/$", {
    getMeta: getAllDocsMeta,
    moduleMap: DOCS_MODULE_MAP,
    prefix: "docs",
    version: "v1",
    component: DocsPage,
  }),
);
