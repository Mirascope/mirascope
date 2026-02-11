import { createFileRoute, Navigate } from "@tanstack/react-router";

function SettingsIndexRedirect() {
  const { orgSlug } = Route.useParams();
  return <Navigate to="/$orgSlug/settings/me" params={{ orgSlug }} replace />;
}

export const Route = createFileRoute("/$orgSlug/settings/")({
  component: SettingsIndexRedirect,
});
