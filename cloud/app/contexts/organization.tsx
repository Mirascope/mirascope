import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import type { PublicOrganizationWithMembership } from "@/db/schema";
import { useOrganizations } from "@/app/api/organizations";

const STORAGE_KEY = "mirascope:selectedOrganizationId";

type OrganizationContextType = {
  organizations: readonly PublicOrganizationWithMembership[];
  selectedOrganization: PublicOrganizationWithMembership | null;
  setSelectedOrganization: (
    org: PublicOrganizationWithMembership | null,
  ) => void;
  isLoading: boolean;
};

const OrganizationContext = createContext<OrganizationContextType | null>(null);

export function OrganizationProvider({ children }: { children: ReactNode }) {
  const { data: organizations = [], isLoading } = useOrganizations();
  const [selectedOrganization, setSelectedOrganizationState] =
    useState<PublicOrganizationWithMembership | null>(null);

  const setSelectedOrganization = (
    org: PublicOrganizationWithMembership | null,
  ) => {
    setSelectedOrganizationState(org);
    if (org) {
      localStorage.setItem(STORAGE_KEY, org.id);
    } else {
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  // Load selected organization from localStorage on mount
  useEffect(() => {
    const storedId = localStorage.getItem(STORAGE_KEY);
    if (storedId && organizations.length > 0) {
      const org = organizations.find((o) => o.id === storedId);
      if (org) {
        setSelectedOrganizationState(org);
      } else {
        // If stored org doesn't exist, select first one
        setSelectedOrganization(organizations[0]);
      }
    } else if (organizations.length > 0 && !selectedOrganization) {
      // Auto-select first org if none selected
      setSelectedOrganization(organizations[0]);
    }
  }, [organizations, selectedOrganization]);

  const value = {
    organizations,
    selectedOrganization,
    setSelectedOrganization,
    isLoading,
  };

  return (
    <OrganizationContext.Provider value={value}>
      {children}
    </OrganizationContext.Provider>
  );
}

export function useOrganization() {
  const context = useContext(OrganizationContext);
  if (!context) {
    throw new Error(
      "useOrganization must be used within an OrganizationProvider",
    );
  }
  return context;
}
