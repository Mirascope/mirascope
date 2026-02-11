import { createFileRoute, Outlet } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useEffect } from "react";

import { ClawProvider } from "@/app/contexts/claw";
import { EnvironmentProvider } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { ProjectProvider } from "@/app/contexts/project";

function OrgLayout() {
  const { orgSlug } = Route.useParams();
  const { organizations, setSelectedOrganization, isLoading } =
    useOrganization();

  // Sync org from URL slug
  useEffect(() => {
    if (isLoading) return;
    const org = organizations.find((o) => o.slug === orgSlug);
    if (org) {
      setSelectedOrganization(org);
    }
  }, [orgSlug, organizations, isLoading, setSelectedOrganization]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const org = organizations.find((o) => o.slug === orgSlug);
  if (!org) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Not Found</h1>
          <p className="text-muted-foreground mt-2">Organization not found.</p>
        </div>
      </div>
    );
  }

  return (
    <ProjectProvider>
      <EnvironmentProvider>
        <ClawProvider>
          <Outlet />
        </ClawProvider>
      </EnvironmentProvider>
    </ProjectProvider>
  );
}

export const Route = createFileRoute("/$orgSlug")({
  component: OrgLayout,
});
