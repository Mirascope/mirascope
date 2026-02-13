import { Link, useRouterState } from "@tanstack/react-router";
import { FolderKanban, Home } from "lucide-react";

import { AccountMenu } from "@/app/components/blocks/navigation/account-menu";
import { ClawIcon } from "@/app/components/icons/claw-icon";
import { useOrganization } from "@/app/contexts/organization";
import { useCurrentSection } from "@/app/hooks/use-current-section";
import { isCloudAppRoute } from "@/app/lib/route-utils";
import { cn } from "@/app/lib/utils";

import { MOBILE_NAV_STYLES, NAV_LINK_STYLES } from "./styles";

interface MobileNavigationProps {
  /**
   * Whether the mobile menu is open
   */
  isOpen: boolean;
  /**
   * Function to close the mobile menu
   */
  onClose: () => void;
  /**
   * Whether the current route is a cloud route
   */
  isCloudRoute?: boolean;
}

export default function MobileNavigation({
  isOpen,
  onClose,
  isCloudRoute,
}: MobileNavigationProps) {
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const { selectedOrganization } = useOrganization();
  const orgSlug = selectedOrganization?.slug ?? "";
  const section = useCurrentSection();

  if (!isOpen) return null;

  // Helper function to check if a link is active
  const isLinkActive = (href: string) => {
    if (href === "/org-redirect") {
      return isCloudAppRoute(currentPath);
    }
    return currentPath === href || currentPath.startsWith(href + "/");
  };

  if (isCloudRoute) {
    const cloudLinks = [
      {
        to: `/$orgSlug` as const,
        params: { orgSlug },
        icon: Home,
        label: "Home",
        active: !section || section === "settings",
      },
      {
        to: `/$orgSlug/claws` as const,
        params: { orgSlug },
        icon: ClawIcon,
        label: "Claws",
        active: section === "claws",
      },
      {
        to: `/$orgSlug/projects` as const,
        params: { orgSlug },
        icon: FolderKanban,
        label: "Projects",
        active: section === "projects",
      },
    ];

    return (
      <div className={MOBILE_NAV_STYLES.container}>
        <div className={MOBILE_NAV_STYLES.content}>
          <AccountMenu />
          <div className="border-border border-t" />
          {cloudLinks.map((item) => (
            <Link
              key={item.label}
              to={item.to}
              params={item.params}
              className={cn(
                NAV_LINK_STYLES.mobile,
                "flex items-center gap-2",
                item.active && NAV_LINK_STYLES.mobileActive,
              )}
              onClick={onClose}
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={MOBILE_NAV_STYLES.container}>
      <div className={MOBILE_NAV_STYLES.content}>
        <Link
          to="/docs"
          className={cn(
            NAV_LINK_STYLES.mobile,
            isLinkActive("/docs") && NAV_LINK_STYLES.mobileActive,
          )}
          onClick={onClose}
        >
          Docs
        </Link>

        <Link
          to="/blog"
          className={cn(
            NAV_LINK_STYLES.mobile,
            isLinkActive("/blog") && NAV_LINK_STYLES.mobileActive,
          )}
          onClick={onClose}
        >
          Blog
        </Link>

        <Link
          to="/pricing"
          className={cn(
            NAV_LINK_STYLES.mobile,
            isLinkActive("/pricing") && NAV_LINK_STYLES.mobileActive,
          )}
          onClick={onClose}
        >
          Pricing
        </Link>

        <Link
          to="/org-redirect"
          className={cn(
            NAV_LINK_STYLES.mobile,
            isLinkActive("/org-redirect") && NAV_LINK_STYLES.mobileActive,
          )}
          onClick={onClose}
        >
          Dashboard
        </Link>
      </div>
    </div>
  );
}
