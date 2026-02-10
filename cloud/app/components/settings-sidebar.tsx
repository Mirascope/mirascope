import { Link, useRouterState } from "@tanstack/react-router";
import { Building2 } from "lucide-react";
import * as React from "react";

import { useOrganization } from "@/app/contexts/organization";
import { cn } from "@/app/lib/utils";

type SettingsRoute =
  | "/$orgSlug/settings/me"
  | "/$orgSlug/settings/organization"
  | "/$orgSlug/settings/team"
  | "/$orgSlug/settings/project"
  | "/$orgSlug/settings/claws"
  | "/$orgSlug/settings/api-keys"
  | "/$orgSlug/settings/billing";

interface SettingsNavItem {
  label: string;
  sub: string;
  to: SettingsRoute;
  icon?: React.ReactNode;
}

const settingsNavItems: SettingsNavItem[] = [
  { label: "My Details", sub: "me", to: "/$orgSlug/settings/me" },
  {
    label: "Organization",
    sub: "organization",
    to: "/$orgSlug/settings/organization",
  },
  { label: "Team", sub: "team", to: "/$orgSlug/settings/team" },
  { label: "Project", sub: "project", to: "/$orgSlug/settings/project" },
  { label: "Claws", sub: "claws", to: "/$orgSlug/settings/claws" },
  { label: "API Keys", sub: "api-keys", to: "/$orgSlug/settings/api-keys" },
  { label: "Billing", sub: "billing", to: "/$orgSlug/settings/billing" },
];

export function SettingsSidebar() {
  const { selectedOrganization } = useOrganization();
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const orgSlug = selectedOrganization?.slug ?? "";

  const isActive = (sub: string) => {
    if (!orgSlug) return false;
    return currentPath === `/${orgSlug}/settings/${sub}`;
  };

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
            key={item.sub}
            to={item.to}
            params={{ orgSlug }}
            className={cn(
              "flex items-center gap-2 px-3 py-2 text-sm rounded-md transition-colors cursor-pointer",
              isActive(item.sub)
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
