import { Link, useRouterState } from "@tanstack/react-router";
import { FolderKanban, Home } from "lucide-react";

import { ClawIcon } from "@/app/components/icons/claw-icon";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/app/components/ui/tooltip";
import { cn } from "@/app/lib/utils";

export function CloudNavIcons() {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const isHome =
    currentPath === "/cloud" ||
    currentPath === "/cloud/" ||
    currentPath.startsWith("/cloud/settings");
  const isClaws = currentPath.startsWith("/cloud/claws");
  const isProjects = currentPath.startsWith("/cloud/projects");

  const items = [
    { to: "/cloud" as const, icon: Home, label: "Home", active: isHome },
    {
      to: "/cloud/claws" as const,
      icon: ClawIcon,
      label: "Claws",
      active: isClaws,
    },
    {
      to: "/cloud/projects/dashboard" as const,
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
