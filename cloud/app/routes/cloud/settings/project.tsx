import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { Plus, Trash2 } from "lucide-react";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useAuth } from "@/app/contexts/auth";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { CreateProjectModal } from "@/app/components/create-project-modal";
import { DeleteProjectModal } from "@/app/components/delete-project-modal";
import { ProjectMembersSection } from "@/app/components/project-members-section";
import { EnvironmentsSection } from "@/app/components/environments-section";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";

function ProjectsSettingsPage() {
  const { selectedOrganization } = useOrganization();
  const { selectedProject, isLoading } = useProject();
  const { user } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Organization OWNER/ADMIN have implicit project ADMIN access
  const orgRole = selectedOrganization?.role;
  const canManageMembers = orgRole === "OWNER" || orgRole === "ADMIN";

  const header = (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-semibold">Project</h1>
        <p className="text-muted-foreground mt-1">
          Manage your project settings
        </p>
      </div>
      <Button onClick={() => setShowCreateModal(true)}>
        <Plus className="h-4 w-4 mr-2" />
        New Project
      </Button>
    </div>
  );

  if (!selectedOrganization) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">
            Please select an organization first
          </div>
        </div>
        <CreateProjectModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">Loading...</div>
        </div>
        <CreateProjectModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  if (!selectedProject) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <div className="text-muted-foreground">Please select a project</div>
        </div>
        <CreateProjectModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
        />
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-6">
      {header}

      <Card>
        <CardHeader>
          <CardTitle>Project Details</CardTitle>
          <CardDescription>
            Basic information about your project
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="project-name">Name</Label>
            <Input
              id="project-name"
              value={selectedProject.name}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="project-slug">Slug</Label>
            <Input
              id="project-slug"
              value={selectedProject.slug}
              readOnly
              className="bg-muted"
            />
          </div>
        </CardContent>
      </Card>

      <ProjectMembersSection
        organizationId={selectedOrganization.id}
        projectId={selectedProject.id}
        currentUserId={user?.id ?? ""}
        canManageMembers={canManageMembers}
      />

      <EnvironmentsSection
        organizationId={selectedOrganization.id}
        projectId={selectedProject.id}
        canManageEnvironments={canManageMembers}
      />

      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="text-destructive">Danger Zone</CardTitle>
          <CardDescription>
            Irreversible and destructive actions
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Delete this project</p>
              <p className="text-sm text-muted-foreground">
                Once you delete a project, there is no going back. Please be
                certain.
              </p>
            </div>
            <Button
              variant="destructive"
              onClick={() => setShowDeleteModal(true)}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </CardContent>
      </Card>

      <CreateProjectModal
        open={showCreateModal}
        onOpenChange={setShowCreateModal}
      />
      <DeleteProjectModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
      />
    </div>
  );
}

export const Route = createFileRoute("/cloud/settings/project")({
  component: ProjectsSettingsPage,
});
