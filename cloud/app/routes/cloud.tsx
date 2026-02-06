import { createFileRoute, Outlet } from "@tanstack/react-router";

import { ClawProvider } from "@/app/contexts/claw";
import { EnvironmentProvider } from "@/app/contexts/environment";
import { ProjectProvider } from "@/app/contexts/project";

function CloudLayout() {
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

export const Route = createFileRoute("/cloud")({
  component: CloudLayout,
});
