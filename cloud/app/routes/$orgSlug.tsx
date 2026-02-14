import { createFileRoute, Outlet } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useEffect } from "react";

import { CloudLayout } from "@/app/components/cloud-layout";
import { NotFound } from "@/app/components/not-found";
import { Protected } from "@/app/components/protected";
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
    return <NotFound />;
  }

  return (
    <Protected>
      <ProjectProvider>
        <EnvironmentProvider>
          <ClawProvider>
            <CloudLayout>
              <Outlet />
            </CloudLayout>
          </ClawProvider>
        </EnvironmentProvider>
      </ProjectProvider>
    </Protected>
  );
}

export const Route = createFileRoute("/$orgSlug")({
  component: OrgLayout,
});
