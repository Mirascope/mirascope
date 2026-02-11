import { createFileRoute, Navigate } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";

import { useOrganization } from "@/app/contexts/organization";

function OrganizationsIndexRedirect() {
  const { organizations, selectedOrganization, isLoading } = useOrganization();

  if (isLoading) {
    return (
      <div className="flex justify-center pt-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const defaultOrg = selectedOrganization || organizations[0];
  if (defaultOrg) {
    return (
      <Navigate
        to="/settings/organizations/$orgSlug"
        params={{ orgSlug: defaultOrg.slug }}
        replace
      />
    );
  }

  return (
    <div className="flex justify-center pt-12">
      <div className="text-muted-foreground">
        No organizations found. Please create one first.
      </div>
    </div>
  );
}

export const Route = createFileRoute("/settings/organizations/")({
  component: OrganizationsIndexRedirect,
});
