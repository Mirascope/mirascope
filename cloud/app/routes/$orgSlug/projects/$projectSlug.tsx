import { createFileRoute, Outlet } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useEffect } from "react";

import { useProject } from "@/app/contexts/project";

function ProjectLayout() {
  const { projectSlug } = Route.useParams();
  const { projects, setSelectedProject, isLoading } = useProject();

  // Sync project from URL slug
  useEffect(() => {
    if (isLoading) return;
    const project = projects.find((p) => p.slug === projectSlug);
    if (project) {
      setSelectedProject(project);
    }
  }, [projectSlug, projects, isLoading, setSelectedProject]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const project = projects.find((p) => p.slug === projectSlug);
  if (!project) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Not Found</h1>
          <p className="text-muted-foreground mt-2">Project not found.</p>
        </div>
      </div>
    );
  }

  return <Outlet />;
}

export const Route = createFileRoute("/$orgSlug/projects/$projectSlug")({
  component: ProjectLayout,
});
