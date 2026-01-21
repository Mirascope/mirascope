import { HomePage } from "@/app/components/home-page";
import { createFileRoute } from "@tanstack/react-router";
import { createPageHead } from "@/app/lib/seo/head";

export const Route = createFileRoute("/")({
  head: () =>
    createPageHead({
      route: "/",
      title: "Home",
      description: "The AI Engineer's Developer Stack",
    }),
  component: HomePage,
});
