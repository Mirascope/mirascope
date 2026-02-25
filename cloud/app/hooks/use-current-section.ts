import { useRouterState } from "@tanstack/react-router";

/**
 * Returns the current "section" segment from the URL path.
 *
 * Given a path like `/{orgSlug}/{section}/...`, this returns the section
 * string (e.g. "projects", "settings") or `undefined` if there
 * is no second segment.
 */
export function useCurrentSection(): string | undefined {
  const router = useRouterState();
  const segments = router.location.pathname.split("/").filter(Boolean);
  return segments[1]; // "projects", "settings", etc.
}
