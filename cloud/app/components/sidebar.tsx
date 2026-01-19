import { useState } from "react";
import { Link, useNavigate, useRouterState } from "@tanstack/react-router";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { CreateOrganizationModal } from "@/app/components/create-organization-modal";
import { CreateProjectModal } from "@/app/components/create-project-modal";
import { CreateEnvironmentModal } from "@/app/components/create-environment-modal";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";
import { useEnvironment } from "@/app/contexts/environment";
import { useAuth } from "@/app/contexts/auth";

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
    isLoading: environmentsLoading,
  } = useEnvironment();
  const { logout } = useAuth();
  const navigate = useNavigate();

  const [showCreateOrg, setShowCreateOrg] = useState(false);
  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showCreateEnvironment, setShowCreateEnvironment] = useState(false);

  const router = useRouterState();
  const currentPath = router.location.pathname;

  const handleSignOut = async () => {
    await logout();
    void navigate({ to: "/" });
  };

  const handleOrgSelectChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateOrg(true);
    } else {
      const org = organizations.find((o) => o.id === value);
      setSelectedOrganization(org || null);
    }
  };

  const handleProjectSelectChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateProject(true);
    } else {
      const project = projects.find((p) => p.id === value);
      setSelectedProject(project || null);
    }
  };

  const handleEnvironmentSelectChange = (value: string) => {
    if (value === "__create_new__") {
      setShowCreateEnvironment(true);
    } else {
      const environment = environments.find((e) => e.id === value);
      setSelectedEnvironment(environment || null);
    }
  };

  const isActive = (path: string) => currentPath === path;

  return (
    <aside className="w-48 h-full flex flex-col bg-background">
      {/* Project selector at top */}
      {selectedOrganization && (
        <div className="px-2 pt-4 pb-2">
          {projectsLoading ? (
            <div className="text-sm text-muted-foreground px-2">Loading...</div>
          ) : (
            <Select
              value={selectedProject?.id || ""}
              onValueChange={handleProjectSelectChange}
            >
              <SelectTrigger className="bg-background text-base">
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
      )}

      {/* Environment selector - shown when project is selected */}
      {selectedProject && (
        <div className="px-2 pb-2">
          {environmentsLoading ? (
            <div className="text-sm text-muted-foreground px-2">Loading...</div>
          ) : (
            <Select
              value={selectedEnvironment?.id || ""}
              onValueChange={handleEnvironmentSelectChange}
            >
              <SelectTrigger className="bg-background text-base">
                <SelectValue placeholder="Select environment" />
              </SelectTrigger>
              <SelectContent>
                {environments.map((environment) => (
                  <SelectItem key={environment.id} value={environment.id}>
                    {environment.name}
                  </SelectItem>
                ))}
                <SelectItem
                  value="__create_new__"
                  className="text-primary font-medium"
                >
                  + Create New Environment
                </SelectItem>
              </SelectContent>
            </Select>
          )}
        </div>
      )}

      {/* Dashboard link */}
      <div className="px-2 pt-4">
        <Link
          to="/cloud/dashboard"
          className={`relative flex items-center justify-center px-3 py-2 text-base rounded-md text-foreground font-handwriting-descent ${
            isActive("/cloud/dashboard")
              ? "bg-muted font-medium"
              : "hover:bg-muted"
          }`}
        >
          <svg
            className="w-5 h-5 absolute left-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
          Dashboard
        </Link>
      </div>

      {/* Main content area - empty for now */}
      <div className="flex-1 overflow-y-auto px-2">
        {/* Future: Navigation items will go here */}
      </div>

      {/* Settings link */}
      <div className="px-2 pb-2">
        <Link
          to="/cloud/settings"
          className={`relative flex items-center justify-center px-3 py-2 text-base rounded-md text-foreground font-handwriting-descent ${
            isActive("/cloud/settings")
              ? "bg-muted font-medium"
              : "hover:bg-muted"
          }`}
        >
          <svg
            className="w-5 h-5 absolute left-4"
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

      {/* Sign Out button */}
      <div className="px-2 pb-2">
        <button
          onClick={() => void handleSignOut()}
          className="relative flex items-center justify-center w-full px-3 py-2 text-base rounded-md text-foreground font-handwriting-descent hover:bg-muted"
        >
          <svg
            className="w-5 h-5 absolute left-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
            />
          </svg>
          Sign Out
        </button>
      </div>

      {/* Organization selector at bottom */}
      <div className="px-2 pb-3 pt-3">
        {orgsLoading ? (
          <div className="text-sm text-muted-foreground">Loading...</div>
        ) : (
          <Select
            value={selectedOrganization?.id || ""}
            onValueChange={handleOrgSelectChange}
          >
            <SelectTrigger className="bg-background text-base">
              <SelectValue placeholder="Select organization" />
            </SelectTrigger>
            <SelectContent>
              {organizations.map((org) => (
                <SelectItem key={org.id} value={org.id}>
                  {org.name}
                </SelectItem>
              ))}
              <SelectItem
                value="__create_new__"
                className="text-primary font-medium"
              >
                + Create New Organization
              </SelectItem>
            </SelectContent>
          </Select>
        )}
      </div>

      <CreateOrganizationModal
        open={showCreateOrg}
        onOpenChange={setShowCreateOrg}
      />
      <CreateProjectModal
        open={showCreateProject}
        onOpenChange={setShowCreateProject}
      />
      <CreateEnvironmentModal
        open={showCreateEnvironment}
        onOpenChange={setShowCreateEnvironment}
      />
    </aside>
  );
}
