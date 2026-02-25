import { createFileRoute, Navigate } from "@tanstack/react-router";

function OrgIndexRedirect() {
  const { orgSlug } = Route.useParams();

  return <Navigate to="/$orgSlug/projects" params={{ orgSlug }} replace />;
}

export const Route = createFileRoute("/$orgSlug/")({
  component: OrgIndexRedirect,
});
