import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { FolderKanban, Loader2 } from "lucide-react";

import type { PublicProject } from "@/db/schema";

import { CloudLayout } from "@/app/components/cloud-layout";
import { ClawIcon } from "@/app/components/icons/claw-icon";
import { Protected } from "@/app/components/protected";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/app/components/ui/card";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

function CloudIndexPage() {
  const { selectedOrganization, isLoading: orgsLoading } = useOrganization();
  const {
    projects,
    setSelectedProject,
    isLoading: projectsLoading,
  } = useProject();
  const navigate = useNavigate();

  const handleProjectClick = (project: PublicProject) => {
    setSelectedProject(project);
    void navigate({ to: "/cloud/projects/dashboard" });
  };

  if (orgsLoading) {
    return (
      <Protected>
        <CloudLayout>
          <div className="flex h-64 items-center justify-center">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        </CloudLayout>
      </Protected>
    );
  }

  return (
    <Protected>
      <CloudLayout>
        <div className="p-6 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-semibold">
              {selectedOrganization?.name ?? "Dashboard"}
            </h1>
            <p className="text-muted-foreground">
              Manage your claws and projects
            </p>
          </div>

          {/* Cards Grid */}
          <div className="grid gap-6 md:grid-cols-2">
            {/* Claws Section */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <ClawIcon className="h-5 w-5 text-muted-foreground" />
                <h2 className="text-lg font-semibold">Claws</h2>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Deploy and manage AI-powered claws for your organization
              </p>
              <div className="flex h-24 items-center justify-center rounded-lg border border-dashed bg-muted/30">
                <p className="text-sm text-muted-foreground">Coming soon</p>
              </div>
            </div>

            {/* Projects Section */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <FolderKanban className="h-5 w-5 text-muted-foreground" />
                <h2 className="text-lg font-semibold">Projects</h2>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                Monitor traces, functions, and analytics for your LLM
                applications
              </p>
              {projectsLoading ? (
                <div className="flex h-24 items-center justify-center">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                </div>
              ) : projects.length === 0 ? (
                <div className="flex h-24 items-center justify-center rounded-lg border border-dashed bg-muted/30">
                  <p className="text-sm text-muted-foreground">
                    No projects yet
                  </p>
                </div>
              ) : (
                <div className="grid gap-3">
                  {projects.map((project) => (
                    <Card
                      key={project.id}
                      className="cursor-pointer transition-colors hover:bg-muted/50"
                      onClick={() => handleProjectClick(project)}
                    >
                      <CardHeader className="p-4">
                        <CardTitle className="text-base">
                          {project.name}
                        </CardTitle>
                        <CardDescription className="text-sm">
                          {project.slug}
                        </CardDescription>
                      </CardHeader>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </CloudLayout>
    </Protected>
  );
}

export const Route = createFileRoute("/cloud/")({
  component: CloudIndexPage,
});
