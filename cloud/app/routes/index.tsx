import { HomePage } from "@/app/components/home-page";
import { createFileRoute } from "@tanstack/react-router";
import { createStaticRouteHead } from "@/app/lib/seo/static-route-head";

export const Route = createFileRoute("/")({
  head: createStaticRouteHead("/"),
  component: HomePage,
});
