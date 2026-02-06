import { Link, useRouterState } from "@tanstack/react-router";
import { FolderKanban, Home } from "lucide-react";

import { AccountMenu } from "@/app/components/blocks/navigation/account-menu";
import { ClawIcon } from "@/app/components/icons/claw-icon";
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

  if (!isOpen) return null;

  // Helper function to check if a link is active
  const isLinkActive = (href: string) => {
    if (href === "/cloud") {
      return (
        currentPath === "/cloud" ||
        currentPath === "/cloud/" ||
        currentPath.startsWith("/cloud/settings")
      );
    }
    return currentPath === href || currentPath.startsWith(href + "/");
  };

  if (isCloudRoute) {
    const cloudLinks = [
      { to: "/cloud" as const, icon: Home, label: "Home" },
      { to: "/cloud/claws" as const, icon: ClawIcon, label: "Claws" },
      {
        to: "/cloud/projects/dashboard" as const,
        icon: FolderKanban,
        label: "Projects",
      },
    ];

    return (
      <div className={MOBILE_NAV_STYLES.container}>
        <div className={MOBILE_NAV_STYLES.content}>
          <AccountMenu />
          <div className="border-border border-t" />
          {cloudLinks.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={cn(
                NAV_LINK_STYLES.mobile,
                "flex items-center gap-2",
                isLinkActive(item.to) && NAV_LINK_STYLES.mobileActive,
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
          to="/cloud"
          className={cn(
            NAV_LINK_STYLES.mobile,
            isLinkActive("/cloud") && NAV_LINK_STYLES.mobileActive,
          )}
          onClick={onClose}
        >
          Cloud
        </Link>
      </div>
    </div>
  );
}
