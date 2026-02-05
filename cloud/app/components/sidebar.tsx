import { Link, useRouterState } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import * as React from "react";
import { useState } from "react";

import { CreateEnvironmentModal } from "@/app/components/create-environment-modal";
import { CreateProjectModal } from "@/app/components/create-project-modal";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { useEnvironment } from "@/app/contexts/environment";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

const icons = {
  home: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
    />
  ),
  dashboard: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zm10 0a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"
    />
  ),
  traces: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
    />
  ),
  functions: (
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
    />
  ),
  annotationQueue: (
    <>
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
      />
    </>
  ),
};

function SidebarIcon({ children }: { children: React.ReactNode }) {
  return (
    <svg
      className="w-5 h-5 flex-shrink-0"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      {children}
    </svg>
  );
}

function SidebarLink({
  to,
  icon,
  label,
  isActive,
}: {
  to: string;
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
}) {
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-3 py-2 text-base rounded-md text-foreground font-handwriting-descent ${
        isActive ? "bg-primary/10 text-primary font-medium" : "hover:bg-muted"
      }`}
    >
      <SidebarIcon>{icon}</SidebarIcon>
      {label}
    </Link>
  );
}

export function Sidebar() {
  const { selectedOrganization } = useOrganization();
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

  const [showCreateProject, setShowCreateProject] = useState(false);
  const [showCreateEnvironment, setShowCreateEnvironment] = useState(false);

  const router = useRouterState();
  const currentPath = router.location.pathname;

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

  const isActive = (path: string) => {
    if (currentPath === path) return true;
    // For nested routes, also match child routes
    if (
      path === "/cloud/projects/traces" ||
      path === "/cloud/projects/functions" ||
      path === "/cloud/projects/annotation-queue"
    ) {
      return currentPath.startsWith(`${path}/`);
    }
    return false;
  };

  return (
    <aside className="w-48 h-full flex flex-col bg-background">
      {/* Home link */}
      <div className="px-2 pt-4 pb-2">
        <SidebarLink
          to="/cloud"
          icon={icons.home}
          label="Home"
          isActive={currentPath === "/cloud" || currentPath === "/cloud/"}
        />
      </div>

      <div className="mx-2 border-t border-border" />

      {/* Project selector */}
      {selectedOrganization && (
        <div className="px-2 pt-4 pb-2">
          <div className="text-xs font-medium text-muted-foreground mb-1 px-1">
            Project
          </div>
          {projectsLoading ? (
            <div className="flex justify-center py-2">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
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
          <div className="text-xs font-medium text-muted-foreground mb-1 px-1">
            Environment
          </div>
          {environmentsLoading ? (
            <div className="flex justify-center py-2">
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            </div>
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

      <div className="mx-2 border-t border-border" />

      {/* Dashboard link */}
      <div className="px-2 pt-4">
        <SidebarLink
          to="/cloud/projects/dashboard"
          icon={icons.dashboard}
          label="Dashboard"
          isActive={isActive("/cloud/projects/dashboard")}
        />
      </div>

      {/* Main navigation */}
      <div className="flex-1 overflow-y-auto px-2 pt-2 space-y-2">
        <SidebarLink
          to="/cloud/projects/traces"
          icon={icons.traces}
          label="Traces"
          isActive={isActive("/cloud/projects/traces")}
        />
        <SidebarLink
          to="/cloud/projects/functions"
          icon={icons.functions}
          label="Functions"
          isActive={isActive("/cloud/projects/functions")}
        />
        <SidebarLink
          to="/cloud/projects/annotation-queue"
          icon={icons.annotationQueue}
          label="Annotation Queue"
          isActive={isActive("/cloud/projects/annotation-queue")}
        />
      </div>

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
