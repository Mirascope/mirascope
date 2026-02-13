import { createFileRoute, Navigate } from "@tanstack/react-router";

import { useOrganization } from "@/app/contexts/organization";

function CloudRedirect() {
  const { selectedOrganization, isLoading } = useOrganization();

  if (isLoading) return null;

  if (selectedOrganization) {
    return (
      <Navigate
        to="/$orgSlug"
        params={{ orgSlug: selectedOrganization.slug }}
        replace
      />
    );
  }

  // No org selected, redirect to login
  return <Navigate to="/onboarding" replace />;
}

export const Route = createFileRoute("/org-redirect")({
  component: CloudRedirect,
});
