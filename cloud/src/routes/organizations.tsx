import { OrganizationsPage } from "@/src/components/organizations-page";
import { Protected } from "@/src/components/protected";
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
