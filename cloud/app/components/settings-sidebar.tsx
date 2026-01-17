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
];

export function SettingsSidebar() {
  const { selectedOrganization } = useOrganization();
  const router = useRouterState();
  const currentPath = router.location.pathname;

  const isActive = (path: string) => currentPath === path;

  return (
    <aside className="w-56 h-full flex flex-col border-r border-border bg-muted/30">
      {/* Organization header */}
      <div className="px-3 pt-4 pb-3">
        <div className="flex items-center gap-3 px-3 py-2 rounded-lg border border-border bg-background">
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted">
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
      <nav className="flex-1 px-3 py-2">
        {settingsNavItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              "flex items-center gap-2 px-3 py-2 text-sm rounded-md transition-colors",
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
