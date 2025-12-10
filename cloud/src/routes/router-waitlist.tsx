import { createFileRoute } from "@tanstack/react-router";
import { environment } from "@/src/lib/content/environment";
import { RouterWaitlist } from "@/src/components/routes/router-waitlist";

export const Route = createFileRoute("/router-waitlist")({
  ssr: false, // Client-side rendered
  component: RouterWaitlist,
  onError: (error: Error) => environment.onError(error),
});
