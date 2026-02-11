import { Link, useRouterState } from "@tanstack/react-router";
import { Building2 } from "lucide-react";
import * as React from "react";

import { useOrganization } from "@/app/contexts/organization";
import { cn } from "@/app/lib/utils";

interface SettingsNavItem {
  label: string;
  sub: string;
  to: string;
  orgScoped: boolean;
  icon?: React.ReactNode;
}

const settingsNavItems: SettingsNavItem[] = [
  {
    label: "My Details",
    sub: "me",
    to: "/settings/me",
    orgScoped: false,
  },
  {
    label: "Organization",
    sub: "organization",
    to: "/settings/organizations/$orgSlug",
    orgScoped: true,
  },
  {
    label: "Team",
    sub: "team",
    to: "/settings/organizations/$orgSlug/team",
    orgScoped: true,
  },
  {
    label: "Project",
    sub: "projects",
    to: "/settings/organizations/$orgSlug/projects",
    orgScoped: true,
  },
  {
    label: "Claws",
    sub: "claws",
    to: "/settings/organizations/$orgSlug/claws",
    orgScoped: true,
  },
  {
    label: "API Keys",
    sub: "api-keys",
    to: "/settings/organizations/$orgSlug/api-keys",
    orgScoped: true,
  },
  {
    label: "Billing",
    sub: "billing",
    to: "/settings/organizations/$orgSlug/billing",
    orgScoped: true,
  },
];

export function SettingsSidebar() {
  const { selectedOrganization } = useOrganization();
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const orgSlug = selectedOrganization?.slug ?? "";

  const isActive = (item: SettingsNavItem) => {
    if (!item.orgScoped) {
      return currentPath === `/settings/${item.sub}`;
    }
    if (!orgSlug) return false;
    const orgPrefix = `/settings/organizations/${orgSlug}`;
    if (item.sub === "organization") {
      return currentPath === orgPrefix || currentPath === `${orgPrefix}/`;
    }
    return currentPath.startsWith(`${orgPrefix}/${item.sub}`);
  };

  const resolveTo = (item: SettingsNavItem) => {
    return item.to.replace("$orgSlug", orgSlug);
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
            to={resolveTo(item)}
            className={cn(
              "flex items-center gap-2 px-3 py-2 text-sm rounded-md transition-colors cursor-pointer",
              isActive(item)
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
