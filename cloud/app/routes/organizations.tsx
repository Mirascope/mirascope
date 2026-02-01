import { createFileRoute } from "@tanstack/react-router";

import { CenteredLayout } from "@/app/components/centered-layout";
import { OrganizationsPage } from "@/app/components/organizations-page";
import { Protected } from "@/app/components/protected";

export const Route = createFileRoute("/organizations")({
  component: OrganizationsRoute,
});

function OrganizationsRoute() {
  return (
    <CenteredLayout>
      <Protected>
        <OrganizationsPage />
      </Protected>
    </CenteredLayout>
  );
}
