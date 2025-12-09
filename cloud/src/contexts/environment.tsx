import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import type { PublicEnvironment } from "@/db/schema";
import { useEnvironments } from "@/src/api/environments";
import { useOrganization } from "@/src/contexts/organization";
import { useProject } from "@/src/contexts/project";

const STORAGE_KEY = "mirascope:selectedEnvironmentId";

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
    const storedId = localStorage.getItem(STORAGE_KEY);
    if (storedId && environments.length > 0) {
      const environment = environments.find((e) => e.id === storedId);
      if (environment) {
        setSelectedEnvironmentState(environment);
      } else {
        // If stored environment doesn't exist in current project, select first one
        setSelectedEnvironmentState(environments[0]);
        localStorage.setItem(STORAGE_KEY, environments[0].id);
      }
    } else if (environments.length > 0 && !selectedEnvironment) {
      // Auto-select first environment if none selected
      setSelectedEnvironmentState(environments[0]);
      localStorage.setItem(STORAGE_KEY, environments[0].id);
    } else if (environments.length === 0) {
      // Clear selection if no environments
      setSelectedEnvironmentState(null);
    }
  }, [environments, selectedEnvironment]);

  // Reset environment selection when project changes
  useEffect(() => {
    setSelectedEnvironmentState(null);
  }, [selectedProject?.id]);

  const setSelectedEnvironment = (environment: PublicEnvironment | null) => {
    setSelectedEnvironmentState(environment);
    if (environment) {
      localStorage.setItem(STORAGE_KEY, environment.id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
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
