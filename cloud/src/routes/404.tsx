import { createFileRoute } from "@tanstack/react-router";
import NotFound from "@/src/components/routes/NotFound";
import { environment } from "@/src/lib/content/environment";

export const Route = createFileRoute("/404")({
  component: () => <NotFound />,
  onError: (error: Error) => environment.onError(error),
  validateSearch: () => ({}),
});
