import { Link, useRouterState } from "@tanstack/react-router";
import { Bot, FolderKanban, Home } from "lucide-react";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/app/components/ui/tooltip";
import { cn } from "@/app/lib/utils";

export function IconSidebar() {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const isHome = currentPath === "/cloud" || currentPath === "/cloud/";
  const isClaws = currentPath.startsWith("/cloud/claws");
  const isProjects = currentPath.startsWith("/cloud/projects");

  const items = [
    { to: "/cloud", icon: Home, label: "Home", active: isHome },
    { to: "/cloud/claws", icon: Bot, label: "Lobsters", active: isClaws },
    {
      to: "/cloud/projects/dashboard",
      icon: FolderKanban,
      label: "Projects",
      active: isProjects,
    },
  ];

  return (
    <aside className="flex h-full w-12 flex-col items-center border-r border-border bg-background pt-4 gap-2">
      {items.map((item) => (
        <Tooltip key={item.to}>
          <TooltipTrigger asChild>
            <Link
              to={item.to}
              className={cn(
                "flex h-9 w-9 items-center justify-center rounded-md transition-colors",
                item.active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground",
              )}
            >
              <item.icon className="h-5 w-5" />
            </Link>
          </TooltipTrigger>
          <TooltipContent side="right">{item.label}</TooltipContent>
        </Tooltip>
      ))}
    </aside>
  );
}
