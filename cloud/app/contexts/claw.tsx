import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";

import type { Claw } from "@/api/claws.schemas";

import { useClaws } from "@/app/api/claws";
import { useOrganization } from "@/app/contexts/organization";

const STORAGE_KEY_PREFIX = "mirascope:selectedClawId";
const getStorageKey = (organizationId: string) =>
  `${STORAGE_KEY_PREFIX}:${organizationId}`;

type ClawContextType = {
  claws: readonly Claw[];
  selectedClaw: Claw | null;
  setSelectedClaw: (claw: Claw | null) => void;
  isLoading: boolean;
};

const ClawContext = createContext<ClawContextType | null>(null);

export function ClawProvider({ children }: { children: ReactNode }) {
  const { selectedOrganization } = useOrganization();
  const { data: claws = [], isLoading } = useClaws(
    selectedOrganization?.id ?? null,
  );
  const [selectedClaw, setSelectedClawState] = useState<Claw | null>(null);

  const setSelectedClaw = (claw: Claw | null) => {
    setSelectedClawState(claw);
    if (selectedOrganization) {
      const storageKey = getStorageKey(selectedOrganization.id);
      if (claw) {
        localStorage.setItem(storageKey, claw.id);
      } else {
        localStorage.removeItem(storageKey);
      }
    }
  };

  // Load selected claw from localStorage on mount or when claws/organization change
  useEffect(() => {
    // Don't do anything while loading or if no organization selected
    if (isLoading || !selectedOrganization) return;

    const storageKey = getStorageKey(selectedOrganization.id);
    const storedId = localStorage.getItem(storageKey);
    if (storedId && claws.length > 0) {
      const claw = claws.find((c) => c.id === storedId);
      if (claw) {
        setSelectedClawState(claw);
      } else {
        // If stored claw doesn't exist in current org, select first one
        setSelectedClawState(claws[0]);
        localStorage.setItem(storageKey, claws[0].id);
      }
    } else if (claws.length > 0 && !selectedClaw) {
      // Auto-select first claw if none selected
      setSelectedClawState(claws[0]);
      localStorage.setItem(storageKey, claws[0].id);
    } else if (claws.length === 0) {
      // Clear selection if no claws (and not loading)
      setSelectedClawState(null);
    }
  }, [claws, selectedClaw, selectedOrganization, isLoading]);

  const value = {
    claws,
    selectedClaw,
    setSelectedClaw,
    isLoading,
  };

  return <ClawContext.Provider value={value}>{children}</ClawContext.Provider>;
}

export function useClaw() {
  const context = useContext(ClawContext);
  if (!context) {
    throw new Error("useClaw must be used within a ClawProvider");
  }
  return context;
}
