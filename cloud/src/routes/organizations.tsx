import { OrganizationsPage } from "@/src/components/dashboard";
import { Protected } from "@/src/components/core/navigation";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/organizations")({
  component: OrganizationsRoute,
});

function OrganizationsRoute() {
  return (
    <Protected>
      <OrganizationsPage />
    </Protected>
  );
}
