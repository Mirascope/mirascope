import { createFileRoute } from "@tanstack/react-router";

import PolicyPage from "@/app/components/policy-page";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  POLICY_MODULE_MAP,
  getAllPolicyMeta,
} from "@/app/lib/content/virtual-module";

export const Route = createFileRoute("/terms/$")(
  createContentRouteConfig("/terms/$", {
    getMeta: getAllPolicyMeta,
    moduleMap: POLICY_MODULE_MAP,
    prefix: "policy",
    subdirectory: "terms",
    component: PolicyPage,
    redirectOnEmptySplat: { to: "/terms/$", params: { _splat: "use" } },
  }),
);
