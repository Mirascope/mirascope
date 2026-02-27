import { createFileRoute, Outlet } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useEffect } from "react";

import { useEnvironment } from "@/app/contexts/environment";

function EnvLayout() {
  const { envSlug } = Route.useParams();
  const { environments, setSelectedEnvironment, isLoading } = useEnvironment();

  // Sync environment from URL slug
  useEffect(() => {
    if (isLoading) return;
    const env = environments.find((e) => e.slug === envSlug);
    if (env) {
      setSelectedEnvironment(env);
    }
  }, [envSlug, environments, isLoading, setSelectedEnvironment]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const env = environments.find((e) => e.slug === envSlug);
  if (!env) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Not Found</h1>
          <p className="text-muted-foreground mt-2">Environment not found.</p>
        </div>
      </div>
    );
  }

  return <Outlet />;
}

export const Route = createFileRoute(
  "/$orgSlug/projects/$projectSlug/$envSlug",
)({
  component: EnvLayout,
});
