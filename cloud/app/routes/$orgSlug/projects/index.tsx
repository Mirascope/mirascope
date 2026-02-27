import { createFileRoute, Navigate } from "@tanstack/react-router";

import { useEnvironment } from "@/app/contexts/environment";
import { useProject } from "@/app/contexts/project";

function ProjectsRedirect() {
  const { orgSlug } = Route.useParams();
  const { selectedProject, isLoading: projectsLoading } = useProject();
  const { selectedEnvironment, isLoading: envsLoading } = useEnvironment();

  if (projectsLoading || envsLoading) return null;

  if (selectedProject && selectedEnvironment) {
    return (
      <Navigate
        to="/$orgSlug/projects/$projectSlug/$envSlug"
        params={{
          orgSlug,
          projectSlug: selectedProject.slug,
          envSlug: selectedEnvironment.slug,
        }}
        replace
      />
    );
  }

  // No project/env selected, go to org dashboard
  return <Navigate to="/$orgSlug" params={{ orgSlug }} replace />;
}

export const Route = createFileRoute("/$orgSlug/projects/")({
  component: ProjectsRedirect,
});
