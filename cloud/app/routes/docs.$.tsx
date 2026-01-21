import { createFileRoute } from "@tanstack/react-router";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  getAllDocsMeta,
  DOCS_MODULE_MAP,
} from "@/app/lib/content/virtual-module";
import DocsPage from "@/app/components/docs-page";

export const Route = createFileRoute("/docs/$")(
  createContentRouteConfig("/docs/$", {
    getMeta: getAllDocsMeta,
    moduleMap: DOCS_MODULE_MAP,
    prefix: "docs",
    component: DocsPage,
  }),
);
