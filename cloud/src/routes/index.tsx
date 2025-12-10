import { createFileRoute } from "@tanstack/react-router";
import { environment } from "@/src/lib/content/environment";
import { LandingPage } from "@/src/components/routes/home";

export const Route = createFileRoute("/")({
  ssr: false, // Client-side rendered
  component: LandingPage,
  onError: (error: Error) => environment.onError(error),
});
