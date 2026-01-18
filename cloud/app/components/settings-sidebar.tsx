import * as React from "react";
import { Link, useRouterState } from "@tanstack/react-router";
import { Building2 } from "lucide-react";
import { useOrganization } from "@/app/contexts/organization";
import { cn } from "@/app/lib/utils";

interface SettingsNavItem {
  label: string;
  path: string;
  icon?: React.ReactNode;
}

const settingsNavItems: SettingsNavItem[] = [
  {
    label: "Organization",
    path: "/cloud/settings/organization",
  },
  {
    label: "Team",
    path: "/cloud/settings/team",
  },
  {
    label: "Project",
    path: "/cloud/settings/project",
  },
];

export function SettingsSidebar() {
  const { selectedOrganization } = useOrganization();
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const isActive = (path: string) => currentPath === path;

  return (
    <aside className="w-48 h-full flex flex-col pt-6 pl-4">
      {/* Organization header */}
      <div className="pb-4">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg bg-muted/50">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-background">
            <Building2 className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-xs text-muted-foreground">Organization</span>
            <span className="text-sm font-medium truncate">
              {selectedOrganization?.name ?? "Select an organization"}
            </span>
          </div>
        </div>
      </div>

      {/* Navigation items */}
      <nav className="flex-1 space-y-1">
        {settingsNavItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center gap-2 px-3 py-2 text-sm rounded-md transition-colors cursor-pointer",
              isActive(item.path)
                ? "bg-muted font-medium text-foreground"
                : "text-muted-foreground hover:bg-muted hover:text-foreground",
            )}
          >
            {item.icon}
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
