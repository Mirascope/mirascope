import { Link, useRouterState } from "@tanstack/react-router";

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
}

export default function MobileNavigation({
  isOpen,
  onClose,
}: MobileNavigationProps) {
  const router = useRouterState();
  const currentPath = router.location.pathname;

  if (!isOpen) return null;

  // Helper function to check if a link is active
  const isLinkActive = (href: string) => {
    if (href === "/cloud") {
      return currentPath === "/cloud" || currentPath.startsWith("/cloud/");
    }
    return currentPath === href || currentPath.startsWith(href + "/");
  };

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
