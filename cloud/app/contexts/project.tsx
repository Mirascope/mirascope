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

const STORAGE_KEY = "mirascope:selectedProjectId";

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
    if (project) {
      localStorage.setItem(STORAGE_KEY, project.id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  // Load selected project from localStorage on mount or when projects change
  useEffect(() => {
    // Don't do anything while loading
    if (isLoading) return;

    const storedId = localStorage.getItem(STORAGE_KEY);
    if (storedId && projects.length > 0) {
      const project = projects.find((p) => p.id === storedId);
      if (project) {
        setSelectedProjectState(project);
      } else {
        // If stored project doesn't exist in current org, select first one
        setSelectedProject(projects[0]);
      }
    } else if (projects.length > 0 && !selectedProject) {
      // Auto-select first project if none selected
      setSelectedProject(projects[0]);
    } else if (projects.length === 0) {
      // Clear selection if no projects (and not loading)
      setSelectedProject(null);
    }
  }, [projects, selectedProject, isLoading]);

  // Reset project selection when organization changes
  useEffect(() => {
    setSelectedProject(null);
  }, [selectedOrganization?.id]);

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
