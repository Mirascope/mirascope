import { createFileRoute, redirect } from "@tanstack/react-router";
import { environment } from "@/app/lib/content/environment";

// Redirect /terms/ to /terms/use
export const Route = createFileRoute("/terms/")({
  beforeLoad: () => {
    // eslint-disable-next-line @typescript-eslint/only-throw-error
    throw redirect({ to: "/terms/use" });
  },
  onError: (error: Error) => environment.onError(error),
});
