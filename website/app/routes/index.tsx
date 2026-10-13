import { createFileRoute } from "@tanstack/react-router";

import { HomePage } from "@/app/components/home-page";
import { createStaticRouteHead } from "@/app/lib/seo/static-route-head";

export const Route = createFileRoute("/")({
  head: createStaticRouteHead("/"),
  component: HomePage,
});
