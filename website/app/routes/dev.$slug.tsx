import { createFileRoute } from "@tanstack/react-router";

import DevPage from "@/app/components/blocks/dev/dev-page";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  DEV_MODULE_MAP,
  getAllDevMeta,
} from "@/app/lib/content/virtual-module";

export const Route = createFileRoute("/dev/$slug")(
  createContentRouteConfig("/dev/$slug", {
    getMeta: getAllDevMeta,
    moduleMap: DEV_MODULE_MAP,
    prefix: "dev",
    component: DevPage,
  }),
);
