import { useCallback, useMemo } from "react";
import { useOrganizations } from "@/app/api/organizations";

const STORAGE_KEY = "mirascope:onboardingComplete";

/**
 * Generates a default organization name with a random suffix.
 * Format: "Workspace XXXXXX" where XXXXXX is 6 hex characters from a UUID.
 *
 * With 16^6 = 16,777,216 combinations, collision probability stays under 1%
 * until ~4,800 organizations (birthday paradox).
 */
export function generateDefaultOrgName(): string {
  const suffix = crypto.randomUUID().slice(0, 6).toUpperCase();
  return `Workspace ${suffix}`;
}

/**
 * Hook to track and manage onboarding state.
 *
 * Determines if a user needs onboarding based on:
 * 1. localStorage flag (tracks if they've completed onboarding)
 * 2. Whether they have any organizations
 *
 * A user needs onboarding if they haven't completed it AND have no organizations.
 */
export function useOnboarding() {
  const { data: organizations, isLoading: isLoadingOrgs } = useOrganizations();

  /**
   * Check if onboarding has been marked as complete in localStorage.
   */
  const isOnboardingComplete = useMemo(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem(STORAGE_KEY) === "true";
  }, []);

  /**
   * Whether the user needs to complete onboarding.
   *
   * A user needs onboarding if:
   * - They haven't completed onboarding (no localStorage flag)
   * - AND they have no organizations
   *
   * Once they have at least one organization, onboarding is no longer required
   * (handles both completion and edge cases like organizations created elsewhere).
   */
  const needsOnboarding = useMemo(() => {
    // Still loading, can't determine yet
    if (isLoadingOrgs) return false;

    // If they already completed onboarding, no need
    if (isOnboardingComplete) return false;

    // If they have organizations, no need for onboarding
    if (organizations && organizations.length > 0) return false;

    // No organizations and haven't completed onboarding - they need it
    return true;
  }, [isLoadingOrgs, isOnboardingComplete, organizations]);

  /**
   * Mark onboarding as complete in localStorage.
   * Call this after the user finishes the onboarding flow.
   */
  const completeOnboarding = useCallback(() => {
    if (typeof window !== "undefined") {
      localStorage.setItem(STORAGE_KEY, "true");
    }
  }, []);

  return {
    needsOnboarding,
    isLoadingOrgs,
    completeOnboarding,
    defaultOrgName: generateDefaultOrgName(),
  };
}
