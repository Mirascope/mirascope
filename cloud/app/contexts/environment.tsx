import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";

import type { PublicEnvironment } from "@/db/schema";

import { useEnvironments } from "@/app/api/environments";
import { useOrganization } from "@/app/contexts/organization";
import { useProject } from "@/app/contexts/project";

const STORAGE_KEY_PREFIX = "mirascope:selectedEnvironmentId";
const getStorageKey = (projectId: string) =>
  `${STORAGE_KEY_PREFIX}:${projectId}`;

type EnvironmentContextType = {
  environments: readonly PublicEnvironment[];
  selectedEnvironment: PublicEnvironment | null;
  setSelectedEnvironment: (environment: PublicEnvironment | null) => void;
  isLoading: boolean;
};

const EnvironmentContext = createContext<EnvironmentContextType | null>(null);

export function EnvironmentProvider({ children }: { children: ReactNode }) {
  const { selectedOrganization } = useOrganization();
  const { selectedProject } = useProject();
  const { data: environments = [], isLoading } = useEnvironments(
    selectedOrganization?.id ?? null,
    selectedProject?.id ?? null,
  );
  const [selectedEnvironment, setSelectedEnvironmentState] =
    useState<PublicEnvironment | null>(null);

  // Load selected environment from localStorage on mount or when project changes
  useEffect(() => {
    // Don't do anything if no project selected
    if (!selectedProject) return;

    const storageKey = getStorageKey(selectedProject.id);
    const storedId = localStorage.getItem(storageKey);
    if (storedId && environments.length > 0) {
      const environment = environments.find((e) => e.id === storedId);
      if (environment) {
        setSelectedEnvironmentState(environment);
      } else {
        // If stored environment doesn't exist in current project, select first one
        setSelectedEnvironmentState(environments[0]);
        localStorage.setItem(storageKey, environments[0].id);
      }
    } else if (environments.length > 0 && !selectedEnvironment) {
      // Auto-select first environment if none selected
      setSelectedEnvironmentState(environments[0]);
      localStorage.setItem(storageKey, environments[0].id);
    } else if (environments.length === 0) {
      // Clear selection if no environments
      setSelectedEnvironmentState(null);
    }
  }, [environments, selectedProject, selectedEnvironment]);

  const setSelectedEnvironment = (environment: PublicEnvironment | null) => {
    setSelectedEnvironmentState(environment);
    if (selectedProject) {
      const storageKey = getStorageKey(selectedProject.id);
      if (environment) {
        localStorage.setItem(storageKey, environment.id);
      } else {
        localStorage.removeItem(storageKey);
      }
    }
  };

  const value = {
    environments,
    selectedEnvironment,
    setSelectedEnvironment,
    isLoading,
  };

  return (
    <EnvironmentContext.Provider value={value}>
      {children}
    </EnvironmentContext.Provider>
  );
}

export function useEnvironment() {
  const context = useContext(EnvironmentContext);
  if (!context) {
    throw new Error(
      "useEnvironment must be used within an EnvironmentProvider",
    );
  }
  return context;
}
