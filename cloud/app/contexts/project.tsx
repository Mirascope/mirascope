import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";

import type { PublicProject } from "@/db/schema";

import { useProjects } from "@/app/api/projects";
import { useOrganization } from "@/app/contexts/organization";

const STORAGE_KEY_PREFIX = "mirascope:selectedProjectSlug";
const getStorageKey = (organizationId: string) =>
  `${STORAGE_KEY_PREFIX}:${organizationId}`;

type ProjectContextType = {
  projects: readonly PublicProject[];
  selectedProject: PublicProject | null;
  setSelectedProject: (project: PublicProject | null) => void;
  isLoading: boolean;
};

const ProjectContext = createContext<ProjectContextType | null>(null);

export function ProjectProvider({ children }: { children: ReactNode }) {
  const { selectedOrganization } = useOrganization();
  const { data: projects = [], isLoading } = useProjects(
    selectedOrganization?.id ?? null,
  );
  const [selectedProject, setSelectedProjectState] =
    useState<PublicProject | null>(null);

  const setSelectedProject = (project: PublicProject | null) => {
    setSelectedProjectState(project);
    if (selectedOrganization) {
      const storageKey = getStorageKey(selectedOrganization.id);
      if (project) {
        localStorage.setItem(storageKey, project.slug);
      } else {
        localStorage.removeItem(storageKey);
      }
    }
  };

  // Load selected project from localStorage on mount or when projects/organization change
  useEffect(() => {
    // Don't do anything while loading or if no organization selected
    if (isLoading || !selectedOrganization) return;

    const storageKey = getStorageKey(selectedOrganization.id);
    const storedSlug = localStorage.getItem(storageKey);
    if (storedSlug && projects.length > 0) {
      const project = projects.find((p) => p.slug === storedSlug);
      if (project) {
        setSelectedProjectState(project);
      } else {
        // If stored project doesn't exist in current org, select first one
        setSelectedProjectState(projects[0]);
        localStorage.setItem(storageKey, projects[0].slug);
      }
    } else if (projects.length > 0 && !selectedProject) {
      // Auto-select first project if none selected
      setSelectedProjectState(projects[0]);
      localStorage.setItem(storageKey, projects[0].slug);
    } else if (projects.length === 0) {
      // Clear selection if no projects (and not loading)
      setSelectedProjectState(null);
    }
  }, [projects, selectedProject, selectedOrganization, isLoading]);

  const value = {
    projects,
    selectedProject,
    setSelectedProject,
    isLoading,
  };

  return (
    <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>
  );
}

export function useProject() {
  const context = useContext(ProjectContext);
  if (!context) {
    throw new Error("useProject must be used within a ProjectProvider");
  }
  return context;
}
