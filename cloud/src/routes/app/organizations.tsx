import { OrganizationsPage } from "@/src/components/dashboard";
// Import directly to avoid circular dependencies
import Protected from "@/src/components/core/navigation/Protected";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/app/organizations")({
  component: OrganizationsRoute,
});

function OrganizationsRoute() {
  return (
    <Protected>
      <OrganizationsPage />
    </Protected>
  );
}
