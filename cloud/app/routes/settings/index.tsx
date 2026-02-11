import { createFileRoute, Navigate } from "@tanstack/react-router";

function SettingsIndexRedirect() {
  return <Navigate to="/settings/me" replace />;
}

export const Route = createFileRoute("/settings/")({
  component: SettingsIndexRedirect,
});
