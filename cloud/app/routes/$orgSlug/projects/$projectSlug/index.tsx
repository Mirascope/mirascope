import { createFileRoute, Navigate } from "@tanstack/react-router";

import { useEnvironment } from "@/app/contexts/environment";

function ProjectIndexRedirect() {
  const { orgSlug, projectSlug } = Route.useParams();
  const { selectedEnvironment, isLoading } = useEnvironment();

  if (isLoading) return null;

  if (selectedEnvironment) {
    return (
      <Navigate
        to="/$orgSlug/projects/$projectSlug/$envSlug"
        params={{ orgSlug, projectSlug, envSlug: selectedEnvironment.slug }}
        replace
      />
    );
  }

  return <Navigate to="/$orgSlug" params={{ orgSlug }} replace />;
}

export const Route = createFileRoute("/$orgSlug/projects/$projectSlug/")({
  component: ProjectIndexRedirect,
});
