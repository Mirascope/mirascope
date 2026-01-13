import { createFileRoute } from "@tanstack/react-router";
import { createContentRouteConfig } from "@/app/lib/content/route-config";
import {
  POLICY_MODULE_MAP,
  getAllPolicyMeta,
} from "@/app/lib/content/virtual-module";
import PolicyPage from "@/app/components/policy-page";

export const Route = createFileRoute("/terms/$")(
  createContentRouteConfig("/terms/$", {
    getMeta: getAllPolicyMeta,
    moduleMap: POLICY_MODULE_MAP,
    prefix: "policy",
    fixedPath: "terms",
    component: PolicyPage,
    redirectOnEmptySplat: { to: "/terms/$", params: { _splat: "use" } },
  }),
);
