import { useRouterState } from "@tanstack/react-router";

import { ClawsSidebar } from "@/app/components/claws-sidebar";
import { IconSidebar } from "@/app/components/icon-sidebar";
import { ProjectsSidebar } from "@/app/components/projects-sidebar";

export function Sidebar() {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const showProjectsSidebar = currentPath.startsWith("/cloud/projects");
  const showClawsSidebar = currentPath.startsWith("/cloud/claws");

  return (
    <div className="flex h-full">
      <IconSidebar />
      {showProjectsSidebar && <ProjectsSidebar />}
      {showClawsSidebar && <ClawsSidebar />}
    </div>
  );
}
