import { useState, type FormEvent } from "react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/src/components/ui/button";
import { Select } from "@/src/components/ui/select";
import { useOrganization } from "@/src/contexts/organization";
import { useProject } from "@/src/contexts/project";
import { useCreateOrganization } from "@/src/api/organizations";
import { useCreateProject } from "@/src/api/projects";

function CreateOrganizationDialog({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createOrganization = useCreateOrganization();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Organization name is required");
      return;
    }

    try {
      await createOrganization.mutateAsync({ name: name.trim() });
      onClose();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create organization",
      );
    }
  };

  return (
    <div className="p-3 border-t border-sidebar-border">
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Organization name"
          className="w-full px-2 py-1.5 text-sm border border-input rounded-md bg-background"
          autoFocus
        />
        {error && <p className="text-xs text-destructive">{error}</p>}
        <div className="flex gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="sm"
            disabled={createOrganization.isPending}
            className="flex-1"
          >
            {createOrganization.isPending ? "..." : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}

function CreateProjectDialog({
  organizationId,
  onClose,
}: {
  organizationId: string;
  onClose: () => void;
}) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createProject = useCreateProject();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Project name is required");
      return;
    }

    try {
      await createProject.mutateAsync({
        name: name.trim(),
        orgOwnerId: organizationId,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create project");
    }
  };

  return (
    <div className="p-3 border-b border-sidebar-border">
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Project name"
          className="w-full px-2 py-1.5 text-sm border border-input rounded-md bg-background"
          autoFocus
        />
        {error && <p className="text-xs text-destructive">{error}</p>}
        <div className="flex gap-2">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="flex-1"
          >
            Cancel
          </Button>
          <Button
            type="submit"
            size="sm"
            disabled={createProject.isPending}
            className="flex-1"
          >
            {createProject.isPending ? "..." : "Create"}
          </Button>
        </div>
      </form>
    </div>
  );
}

export function Sidebar() {
  const {
    organizations,
    selectedOrganization,
    setSelectedOrganization,
    isLoading: orgsLoading,
  } = useOrganization();
  const {
    projects,
    selectedProject,
    setSelectedProject,
    isLoading: projectsLoading,
  } = useProject();

  const [showCreateOrg, setShowCreateOrg] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);

  return (
    <aside className="w-64 h-screen flex flex-col bg-sidebar border-r border-sidebar-border">
      {/* Project selector at top */}
      <div className="p-3 border-b border-sidebar-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-sidebar-foreground/70">
            Project
          </span>
          {selectedOrganization && (
            <button
              onClick={() => setShowCreateProject(!showCreateProject)}
              className="text-xs text-sidebar-foreground/50 hover:text-sidebar-foreground"
            >
              {showCreateProject ? "×" : "+"}
            </button>
          )}
        </div>
        {projectsLoading ? (
          <div className="text-sm text-sidebar-foreground/50">Loading...</div>
        ) : projects.length === 0 ? (
          <div className="text-sm text-sidebar-foreground/50">No projects</div>
        ) : (
          <Select
            value={selectedProject?.id || ""}
            onChange={(e) => {
              const project = projects.find((p) => p.id === e.target.value);
              setSelectedProject(project || null);
            }}
            className="bg-sidebar"
          >
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </Select>
        )}
      </div>

      {showCreateProject && selectedOrganization && (
        <CreateProjectDialog
          organizationId={selectedOrganization.id}
          onClose={() => setShowCreateProject(false)}
        />
      )}

      {/* Main content area - empty for now, will be used for navigation */}
      <div className="flex-1 overflow-y-auto p-3">
        {/* Future: Navigation items will go here */}
      </div>

      {/* Settings link */}
      <div className="p-3 border-t border-sidebar-border">
        <Link
          to="/dashboard/settings"
          className="flex items-center gap-2 px-2 py-1.5 text-sm rounded-md hover:bg-sidebar-accent text-sidebar-foreground"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
          Settings
        </Link>
      </div>

      {/* Organization selector at bottom */}
      <div className="p-3 border-t border-sidebar-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-sidebar-foreground/70">
            Organization
          </span>
          <button
            onClick={() => setShowCreateOrg(!showCreateOrg)}
            className="text-xs text-sidebar-foreground/50 hover:text-sidebar-foreground"
          >
            {showCreateOrg ? "×" : "+"}
          </button>
        </div>
        {orgsLoading ? (
          <div className="text-sm text-sidebar-foreground/50">Loading...</div>
        ) : organizations.length === 0 ? (
          <div className="text-sm text-sidebar-foreground/50">
            No organizations
          </div>
        ) : (
          <Select
            value={selectedOrganization?.id || ""}
            onChange={(e) => {
              const org = organizations.find((o) => o.id === e.target.value);
              setSelectedOrganization(org || null);
            }}
            className="bg-sidebar"
          >
            {organizations.map((org) => (
              <option key={org.id} value={org.id}>
                {org.name}
              </option>
            ))}
          </Select>
        )}
      </div>

      {showCreateOrg && (
        <CreateOrganizationDialog onClose={() => setShowCreateOrg(false)} />
      )}
    </aside>
  );
}
