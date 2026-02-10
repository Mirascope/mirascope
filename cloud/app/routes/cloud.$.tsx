import { createFileRoute, Navigate, useParams } from "@tanstack/react-router";

import { useOrganization } from "@/app/contexts/organization";

/**
 * Catch-all redirect for legacy /cloud/* bookmarks.
 *
 * Redirects paths like /cloud/claws/my-claw to /$orgSlug/claws/my-claw
 * using the user's currently selected organization.
 */
function CloudCatchAllRedirect() {
  const { _splat } = useParams({ strict: false });
  const { selectedOrganization, isLoading } = useOrganization();

  if (isLoading) return null;

  if (selectedOrganization) {
    const remainder = _splat ? `/${_splat}` : "";
    return (
      <Navigate
        to={`/$orgSlug${remainder}`}
        params={{ orgSlug: selectedOrganization.slug }}
        replace
      />
    );
  }

  // No org selected, redirect to login
  return <Navigate to="/login" replace />;
}

export const Route = createFileRoute("/cloud/$")({
  component: CloudCatchAllRedirect,
});
