import { Link } from "@tanstack/react-router";
import React from "react";
import { cn } from "@/app/lib/utils";
import { NAV_LINK_STYLES, DESKTOP_NAV_STYLES } from "./styles";
import { useAuth } from "@/app/contexts/auth";

// Reusable navigation link component
interface NavLinkProps {
  href: string;
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

const NavLink = ({ href, children, className, onClick }: NavLinkProps) => {
  return (
    <Link
      to={href}
      className={cn(NAV_LINK_STYLES.base, className)}
      onClick={onClick}
    >
      {children}
    </Link>
  );
};

interface DesktopNavigationProps {
  /**
   * Whether the search bar is open, affecting navigation visibility
   */
  isSearchOpen: boolean;
}

export default function DesktopNavigation({
  isSearchOpen,
}: DesktopNavigationProps) {
  const { user, isLoading, logout } = useAuth();

  return (
    <div className={DESKTOP_NAV_STYLES.container(isSearchOpen)}>
      {/* Products Menu */}
      <NavLink href="/docs/v1">Docs</NavLink>
      <NavLink href="/blog">Blog</NavLink>
      <NavLink href="/pricing">Pricing</NavLink>
      {!isLoading && (
        <>
          {user ? (
            <button
              onClick={() => void logout()}
              className={cn(NAV_LINK_STYLES.base)}
            >
              Logout
            </button>
          ) : (
            <NavLink href="/login">Login</NavLink>
          )}
        </>
      )}
    </div>
  );
}
