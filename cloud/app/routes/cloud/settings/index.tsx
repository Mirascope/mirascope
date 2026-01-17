import { createFileRoute, Navigate } from "@tanstack/react-router";

function SettingsIndexRedirect() {
  return <Navigate to="/cloud/settings/organization" replace />;
}

export const Route = createFileRoute("/cloud/settings/")({
  component: SettingsIndexRedirect,
});
