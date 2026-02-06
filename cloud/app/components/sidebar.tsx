import { useRouterState } from "@tanstack/react-router";

import { ClawsSidebar } from "@/app/components/claws-sidebar";
import { ProjectsSidebar } from "@/app/components/projects-sidebar";

export function Sidebar() {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const showProjectsSidebar = currentPath.startsWith("/cloud/projects");
  const showClawsSidebar = currentPath.startsWith("/cloud/claws");

  if (!showProjectsSidebar && !showClawsSidebar) return null;

  return (
    <div className="flex h-full">
      {showProjectsSidebar && <ProjectsSidebar />}
      {showClawsSidebar && <ClawsSidebar />}
    </div>
  );
}
