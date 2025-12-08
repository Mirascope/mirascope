import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
import type { OrganizationWithRole } from "@/api/api";
import { useOrganizations } from "@/src/api/organizations";
import { useAuth } from "@/src/contexts/auth";

type OrganizationContextType = {
  /** The currently selected organization, or null if none selected */
  organization: OrganizationWithRole | null;
  /** All organizations the user belongs to */
  organizations: readonly OrganizationWithRole[];
  /** Whether organizations are loading */
  isLoading: boolean;
  /** Error if organizations failed to load */
  error: Error | null;
  /** Select an organization as active */
  selectOrganization: (org: OrganizationWithRole) => void;
  /** Refresh the organizations list */
  refetch: () => void;
};

const OrganizationContext = createContext<OrganizationContextType | null>(null);

export function OrganizationProvider({ children }: { children: ReactNode }) {
  const { user, isLoading: isAuthLoading } = useAuth();
  const [selectedOrg, setSelectedOrg] = useState<OrganizationWithRole | null>(
    null,
  );

  const {
    data: organizations = [],
    isLoading: isOrgsLoading,
    error,
    refetch,
  } = useOrganizations({ enabled: !!user });

  // Only show loading when auth is loading OR (user is logged in AND orgs are loading)
  const isLoading = isAuthLoading || (!!user && isOrgsLoading);

  // Auto-select first organization when organizations load
  useEffect(() => {
    if (!isLoading && organizations.length > 0 && !selectedOrg) {
      setSelectedOrg(organizations[0]);
    }
  }, [isLoading, organizations, selectedOrg]);

  // Clear selection when user logs out
  useEffect(() => {
    if (!user) {
      setSelectedOrg(null);
    }
  }, [user]);

  // Update selected org if it changes in the list (e.g., after refresh)
  useEffect(() => {
    if (selectedOrg) {
      const updated = organizations.find((org) => org.id === selectedOrg.id);
      if (updated && updated !== selectedOrg) {
        setSelectedOrg(updated);
      } else if (!updated && organizations.length > 0) {
        // Selected org was deleted, select first available
        setSelectedOrg(organizations[0]);
      } else if (!updated && organizations.length === 0) {
        // No orgs left
        setSelectedOrg(null);
      }
    }
  }, [organizations, selectedOrg]);

  const selectOrganization = (org: OrganizationWithRole) => {
    setSelectedOrg(org);
  };

  const value: OrganizationContextType = {
    organization: selectedOrg,
    organizations,
    isLoading,
    error: error instanceof Error ? error : null,
    selectOrganization,
    refetch: () => void refetch(),
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
