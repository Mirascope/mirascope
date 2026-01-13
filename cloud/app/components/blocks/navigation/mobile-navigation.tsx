import { Link } from "@tanstack/react-router";
import { MOBILE_NAV_STYLES, NAV_LINK_STYLES } from "./styles";
import { useAuth } from "@/app/contexts/auth";
import { cn } from "@/app/lib/utils";

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
  const { user, isLoading, logout } = useAuth();

  if (!isOpen) return null;

  const handleLogout = async () => {
    await logout();
    onClose();
  };

  return (
    <div className={MOBILE_NAV_STYLES.container}>
      <div className={MOBILE_NAV_STYLES.content}>
        <Link to="/docs" className={NAV_LINK_STYLES.mobile} onClick={onClose}>
          Docs
        </Link>

        <Link to="/blog" className={NAV_LINK_STYLES.mobile} onClick={onClose}>
          Blog
        </Link>

        <Link
          to="/pricing"
          className={NAV_LINK_STYLES.mobile}
          onClick={onClose}
        >
          Pricing
        </Link>

        {!isLoading && (
          <>
            {user ? (
              <button
                onClick={() => void handleLogout()}
                className={cn(NAV_LINK_STYLES.mobile)}
              >
                Logout
              </button>
            ) : (
              <Link
                to="/login"
                className={NAV_LINK_STYLES.mobile}
                onClick={onClose}
              >
                Login
              </Link>
            )}
          </>
        )}
      </div>
    </div>
  );
}
