import { createFileRoute, Navigate } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useState } from "react";

import { CreateProjectModal } from "@/app/components/create-project-modal";
import { Button } from "@/app/components/ui/button";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

function ProjectsIndexRedirect() {
  const { orgSlug } = Route.useParams();
  const { selectedOrganization } = useOrganization();
  const { projects, selectedProject, isLoading } = useProject();
  const [showCreateModal, setShowCreateModal] = useState(false);

  if (!selectedOrganization || isLoading) {
    return (
      <div className="flex justify-center pt-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  const defaultProject = selectedProject || projects[0];
  if (defaultProject) {
    return (
      <Navigate
        to="/settings/organizations/$orgSlug/projects/$projectSlug"
        params={{ orgSlug, projectSlug: defaultProject.slug }}
        replace
      />
    );
  }

  return (
    <div className="max-w-3xl">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold">Project</h1>
        <p className="text-muted-foreground mt-1">
          Manage your project settings
        </p>
      </div>
      <div className="flex flex-col items-center gap-4 pt-12">
        <p className="text-muted-foreground">
          No projects yet. Create one to get started!
        </p>
        <Button onClick={() => setShowCreateModal(true)}>Create Project</Button>
      </div>
      <CreateProjectModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
    </div>
  );
}

export const Route = createFileRoute(
  "/settings/organizations/$orgSlug/projects/",
)({
  component: ProjectsIndexRedirect,
});
