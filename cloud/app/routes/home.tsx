import { createFileRoute } from "@tanstack/react-router";
import { HomePage } from "@/app/components/home-page";
import { createPageHead } from "../lib/seo/head";

export const Route = createFileRoute("/home")({
  head: () =>
    createPageHead({
      route: "/home",
      title: "Home",
      description: "The AI Engineer's Developer Stack",
    }),
  component: HomePage,
});
