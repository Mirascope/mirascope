import { useOrganization } from "@/app/contexts/organization";

/**
 * Returns the appropriate "home" path — `/$orgSlug` when an org is selected,
 * falling back to `/` when outside the OrganizationProvider or no org exists.
 */
export function useHomeLink(): string {
  try {
    const { selectedOrganization } = useOrganization();
    if (selectedOrganization) {
      return `/${selectedOrganization.slug}`;
    }
  } catch {
    // Outside OrganizationProvider or context unavailable
  }
  return "/";
}
