import { createFileRoute, Outlet } from "@tanstack/react-router";
import { OrganizationProvider } from "@/app/contexts/organization";
import { ProjectProvider } from "@/app/contexts/project";
import { EnvironmentProvider } from "@/app/contexts/environment";

function CloudLayout() {
  return (
    <OrganizationProvider>
      <ProjectProvider>
        <EnvironmentProvider>
          <Outlet />
        </EnvironmentProvider>
      </ProjectProvider>
    </OrganizationProvider>
  );
}

export const Route = createFileRoute("/cloud")({
  component: CloudLayout,
});
