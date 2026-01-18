import { createFileRoute, Outlet } from "@tanstack/react-router";
import { OrganizationProvider } from "@/app/contexts/organization";
import { ProjectProvider } from "@/app/contexts/project";

function CloudLayout() {
  return (
    <OrganizationProvider>
      <ProjectProvider>
        <Outlet />
      </ProjectProvider>
    </OrganizationProvider>
  );
}

export const Route = createFileRoute("/cloud")({
  component: CloudLayout,
});
