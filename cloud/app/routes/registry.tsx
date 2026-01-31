import { createFileRoute } from "@tanstack/react-router";

import { RegistryPage } from "@/app/components/registry-page";
import { createStaticRouteHead } from "@/app/lib/seo/static-route-head";

export const Route = createFileRoute("/registry")({
  head: createStaticRouteHead("/registry"),
  component: RegistryPage,
});
