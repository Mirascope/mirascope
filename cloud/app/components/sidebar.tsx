import { useState, type FormEvent } from "react";
import { Link } from "@tanstack/react-router";
import { Button } from "@/app/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useCreateOrganization } from "@/app/api/organizations";
import { useCreateProject } from "@/app/api/projects";
import { useEnvironment } from "@/app/contexts/environment";
import { useCreateEnvironment } from "@/app/api/environments";
import { generateSlug } from "@/db/slug";

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
      await createOrganization.mutateAsync({
        name: name.trim(),
        slug: generateSlug(name.trim()),
      });
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
        organizationId: organizationId,
        name: name.trim(),
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

function CreateEnvironmentDialog({
  organizationId,
  projectId,
  onClose,
}: {
  organizationId: string;
  projectId: string;
  onClose: () => void;
}) {
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createEnvironment = useCreateEnvironment();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Environment name is required");
      return;
    }

    try {
      await createEnvironment.mutateAsync({
        organizationId,
        projectId,
        data: { name: name.trim(), slug: generateSlug(name.trim()) },
      });
      onClose();
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to create environment",
      );
    }
  };

  return (
    <div className="p-3 border-b border-sidebar-border">
      <form onSubmit={(e) => void handleSubmit(e)} className="space-y-2">
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Environment name"
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
            disabled={createEnvironment.isPending}
            className="flex-1"
          >
            {createEnvironment.isPending ? "..." : "Create"}
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
  const {
    environments,
    selectedEnvironment,
    setSelectedEnvironment,
    isLoading: envsLoading,
  } = useEnvironment();

  const [showCreateOrg, setShowCreateOrg] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showCreateEnv, setShowCreateEnv] = useState(false);

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
            onValueChange={(value) => {
              const project = projects.find((p) => p.id === value);
              setSelectedProject(project || null);
            }}
          >
            <SelectTrigger className="bg-sidebar">
              <SelectValue placeholder="Select project" />
            </SelectTrigger>
            <SelectContent>
              {projects.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  {project.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {showCreateProject && selectedOrganization && (
        <CreateProjectDialog
          organizationId={selectedOrganization.id}
          onClose={() => setShowCreateProject(false)}
        />
      )}

      {/* Environment selector */}
      <div className="p-3 border-b border-sidebar-border">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium text-sidebar-foreground/70">
            Environment
          </span>
          {selectedOrganization && selectedProject && (
            <button
              onClick={() => setShowCreateEnv(!showCreateEnv)}
              className="text-xs text-sidebar-foreground/50 hover:text-sidebar-foreground"
            >
              {showCreateEnv ? "×" : "+"}
            </button>
          )}
        </div>
        {envsLoading ? (
          <div className="text-sm text-sidebar-foreground/50">Loading...</div>
        ) : environments.length === 0 ? (
          <div className="text-sm text-sidebar-foreground/50">
            No environments
          </div>
        ) : (
          <Select
            value={selectedEnvironment?.id || ""}
            onValueChange={(value) => {
              const env = environments.find((e) => e.id === value);
              setSelectedEnvironment(env || null);
            }}
          >
            <SelectTrigger className="bg-sidebar">
              <SelectValue placeholder="Select environment" />
            </SelectTrigger>
            <SelectContent>
              {environments.map((env) => (
                <SelectItem key={env.id} value={env.id}>
                  {env.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {showCreateEnv && selectedOrganization && selectedProject && (
        <CreateEnvironmentDialog
          organizationId={selectedOrganization.id}
          projectId={selectedProject.id}
          onClose={() => setShowCreateEnv(false)}
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
            onValueChange={(value) => {
              const org = organizations.find((o) => o.id === value);
              setSelectedOrganization(org || null);
            }}
          >
            <SelectTrigger className="bg-sidebar">
              <SelectValue placeholder="Select organization" />
            </SelectTrigger>
            <SelectContent>
              {organizations.map((org) => (
                <SelectItem key={org.id} value={org.id}>
                  {org.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {showCreateOrg && (
        <CreateOrganizationDialog onClose={() => setShowCreateOrg(false)} />
      )}
    </aside>
  );
}
