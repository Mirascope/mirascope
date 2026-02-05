import { createFileRoute, Outlet } from "@tanstack/react-router";

import { EnvironmentProvider } from "@/app/contexts/environment";
import { ProjectProvider } from "@/app/contexts/project";

function CloudLayout() {
  return (
    <ProjectProvider>
      <EnvironmentProvider>
        <Outlet />
      </EnvironmentProvider>
    </ProjectProvider>
  );
}

export const Route = createFileRoute("/cloud")({
  component: CloudLayout,
});
