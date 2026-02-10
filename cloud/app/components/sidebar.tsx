import { useRouterState } from "@tanstack/react-router";

import { ClawsSidebar } from "@/app/components/claws-sidebar";
import { ProjectsSidebar } from "@/app/components/projects-sidebar";
import { isCloudAppRoute } from "@/app/lib/route-utils";

export function Sidebar() {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  if (!isCloudAppRoute(currentPath)) return null;

  // Parse path: /{orgSlug}/claws/... or /{orgSlug}/projects/...
  const segments = currentPath.split("/").filter(Boolean);
  const section = segments[1]; // "claws", "projects", "settings", etc.

  const showProjectsSidebar = section === "projects";
  const showClawsSidebar = section === "claws";

  if (!showProjectsSidebar && !showClawsSidebar) return null;

  return (
    <div className="flex h-full">
      {showProjectsSidebar && <ProjectsSidebar />}
      {showClawsSidebar && <ClawsSidebar />}
    </div>
  );
}
