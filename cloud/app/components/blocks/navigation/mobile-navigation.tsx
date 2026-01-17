import { Link } from "@tanstack/react-router";
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
  if (!isOpen) return null;

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

        <Link to="/cloud" className={NAV_LINK_STYLES.mobile} onClick={onClose}>
          Cloud
        </Link>
      </div>
    </div>
  );
}
