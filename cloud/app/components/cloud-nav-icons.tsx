import { Link, useRouterState } from "@tanstack/react-router";
import { FolderKanban, Home } from "lucide-react";

import { ClawIcon } from "@/app/components/icons/claw-icon";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/app/components/ui/tooltip";
import { useOrganization } from "@/app/contexts/organization";
import { cn } from "@/app/lib/utils";

export function CloudNavIcons() {
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const { selectedOrganization } = useOrganization();
  const orgSlug = selectedOrganization?.slug ?? "";

  // Parse path: /{orgSlug}/section/...
  const segments = currentPath.split("/").filter(Boolean);
  const section = segments[1]; // "claws", "projects", "settings", etc.

  const isHome = !section || section === "settings";
  const isClaws = section === "claws";
  const isProjects = section === "projects";

  const items = [
    {
      to: "/$orgSlug" as const,
      params: { orgSlug },
      icon: Home,
      label: "Home",
      active: isHome,
    },
    {
      to: "/$orgSlug/claws" as const,
      params: { orgSlug },
      icon: ClawIcon,
      label: "Claws",
      active: isClaws,
    },
    {
      to: "/$orgSlug/projects" as const,
      params: { orgSlug },
      icon: FolderKanban,
      label: "Projects",
      active: isProjects,
    },
  ];

  return (
    <div className="flex items-center gap-1">
      {items.map((item) => (
        <Tooltip key={item.to}>
          <TooltipTrigger asChild>
            <Link
              to={item.to}
              params={item.params}
              className={cn(
                "flex items-center justify-center rounded-md p-2 transition-colors",
                item.active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <item.icon className="h-5 w-5" />
            </Link>
          </TooltipTrigger>
          <TooltipContent side="bottom" className="z-[110]">
            {item.label}
          </TooltipContent>
        </Tooltip>
      ))}
    </div>
  );
}
