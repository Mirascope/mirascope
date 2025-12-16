import { createFileRoute } from "@tanstack/react-router";
import { HomePage } from "@/app/components/home-page";

export const Route = createFileRoute("/home")({
  component: HomePage,
});
