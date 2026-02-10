import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";

import { useGetProjectMember } from "@/app/api/project-memberships";
import { ApiKeysSection } from "@/app/components/api-keys-section";
import { CreateProjectModal } from "@/app/components/create-project-modal";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { useAuth } from "@/app/contexts/auth";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

function ApiKeysSettingsPage() {
  const { user } = useAuth();
  const { selectedOrganization } = useOrganization();
  const { projects, selectedProject, setSelectedProject, isLoading } =
    useProject();
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { data: projectMembership } = useGetProjectMember(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
    user?.id ?? null,
  );

  // Organization OWNER/ADMIN have implicit project ADMIN access to all projects
  const orgRole = selectedOrganization?.role;
  const projectRole = projectMembership?.role;
  const canManageApiKeys =
    orgRole === "OWNER" ||
    orgRole === "ADMIN" ||
    projectRole === "ADMIN" ||
    projectRole === "DEVELOPER";

  const handleProjectChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateModal(true);
    } else {
      const project = projects.find((p) => p.id === value);
      setSelectedProject(project || null);
    }
  };

  const header = (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-semibold">API Keys</h1>
        <p className="text-muted-foreground mt-1">
          Manage API keys for accessing your projects and environments
        </p>
      </div>
      {selectedOrganization && !isLoading && (
        <Select
          value={selectedProject?.id || ""}
          onValueChange={handleProjectChange}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select project" />
          </SelectTrigger>
          <SelectContent>
            {projects.map((project) => (
              <SelectItem key={project.id} value={project.id}>
                {project.name}
              </SelectItem>
            ))}
            <SelectItem
              value="__create_new__"
              className="text-primary font-medium"
            >
              + Create New Project
            </SelectItem>
          </SelectContent>
        </Select>
      )}
    </div>
  );

  if (!selectedOrganization) {
    return (
      <div className="max-w-4xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization first
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="max-w-4xl space-y-6">
        {header}

        <ApiKeysSection
          organizationId={selectedOrganization.id}
          canManageApiKeys={canManageApiKeys}
        />
      </div>

      <CreateProjectModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
    </>
  );
}

export const Route = createFileRoute("/$orgSlug/settings/api-keys")({
  component: ApiKeysSettingsPage,
});
