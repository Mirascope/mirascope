import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Loader2, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

import { CreateProjectModal } from "@/app/components/create-project-modal";
import { DeleteProjectModal } from "@/app/components/delete-project-modal";
import { EnvironmentsSection } from "@/app/components/environments-section";
import { ClawIcon } from "@/app/components/icons/claw-icon";
import { ProjectMembersSection } from "@/app/components/project-members-section";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { Input } from "@/app/components/ui/input";
import { Label } from "@/app/components/ui/label";
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

function ProjectSettingsPage() {
  const { orgSlug, projectSlug } = Route.useParams();
  const navigate = useNavigate();
  const { selectedOrganization } = useOrganization();
  const { projects, selectedProject, setSelectedProject, isLoading } =
    useProject();
  const { user } = useAuth();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const project = projects.find((p) => p.slug === projectSlug);

  // If project was deleted (optimistic removal), redirect to projects list
  useEffect(() => {
    if (!isLoading && !project) {
      setShowDeleteModal(false);
      void navigate({
        to: "/settings/organizations/$orgSlug/projects",
        params: { orgSlug },
      });
    }
  }, [project, isLoading, navigate, orgSlug]);

  // Sync URL project to context
  useEffect(() => {
    if (project && selectedProject?.id !== project.id) {
      setSelectedProject(project);
    }
  }, [project, selectedProject?.id, setSelectedProject]);

  const orgRole = selectedOrganization?.role;
  const canManageMembers = orgRole === "OWNER" || orgRole === "ADMIN";

  const handleProjectChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateModal(true);
    } else {
      const target = projects.find((p) => p.id === value);
      if (target) {
        void navigate({
          to: "/settings/organizations/$orgSlug/projects/$projectSlug",
          params: { orgSlug, projectSlug: target.slug },
        });
      }
    }
  };

  const header = (
    <div className="mb-6 flex items-start justify-between">
      <div>
        <h1 className="text-2xl font-semibold">Project</h1>
        <p className="text-muted-foreground mt-1">
          Manage your project settings
        </p>
      </div>
      {selectedOrganization && !isLoading && (
        <Select value={project?.id || ""} onValueChange={handleProjectChange}>
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select project" />
          </SelectTrigger>
          <SelectContent>
            {projects.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.name}
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
          onCreated={(p) => {
            void navigate({
              to: "/settings/organizations/$orgSlug/projects/$projectSlug",
              params: { orgSlug, projectSlug: p.slug },
            });
          }}
        />
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="max-w-2xl">
        {header}
        <div className="flex justify-center pt-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
        <CreateProjectModal
          open={showCreateModal}
          onOpenChange={setShowCreateModal}
          onCreated={(p) => {
            void navigate({
              to: "/settings/organizations/$orgSlug/projects/$projectSlug",
              params: { orgSlug, projectSlug: p.slug },
            });
          }}
        />
      </div>
    );
  }

  // Don't render settings for a project that no longer exists
  // (redirect effect above will navigate away)
  if (!project) {
    return null;
  }

  return (
    <div className="max-w-3xl space-y-6">
      {header}

      <Card>
        <CardHeader>
          <div className="flex items-center gap-2">
            <CardTitle>Project Details</CardTitle>
            {project.type === "claw_home" && (
              <Badge
                variant="outline"
                size="sm"
                pill
                className="border-primary/40 text-primary"
              >
                <ClawIcon className="size-3.5" />
              </Badge>
            )}
          </div>
          <CardDescription>
            Basic information about your project
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="project-name">Name</Label>
            <Input
              id="project-name"
              value={project.name}
              readOnly
              className="bg-muted"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="project-slug">Slug</Label>
            <Input
              id="project-slug"
              value={project.slug}
              readOnly
              className="bg-muted"
            />
          </div>
        </CardContent>
      </Card>

      <ProjectMembersSection
        organizationId={selectedOrganization.id}
        projectId={project.id}
        currentUserId={user?.id ?? ""}
        canManageMembers={canManageMembers}
      />

      <EnvironmentsSection
        organizationId={selectedOrganization.id}
        projectId={project.id}
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
        onCreated={(p) => {
          void navigate({
            to: "/settings/organizations/$orgSlug/projects/$projectSlug",
            params: { orgSlug, projectSlug: p.slug },
          });
        }}
      />
      <DeleteProjectModal
        open={showDeleteModal}
        onOpenChange={setShowDeleteModal}
        onDeleted={() => {
          void navigate({
            to: "/settings/organizations/$orgSlug/projects",
            params: { orgSlug },
          });
        }}
      />
    </div>
  );
}

export const Route = createFileRoute(
  "/settings/organizations/$orgSlug/projects/$projectSlug",
)({
  component: ProjectSettingsPage,
});
