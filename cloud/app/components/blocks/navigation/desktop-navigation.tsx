import { Link } from "@tanstack/react-router";
import React from "react";
import { cn } from "@/app/lib/utils";
import { NAV_LINK_STYLES, DESKTOP_NAV_STYLES } from "./styles";

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
  return (
    <div className={DESKTOP_NAV_STYLES.container(isSearchOpen)}>
      {/* Products Menu */}
      <NavLink href="/docs">Docs</NavLink>
      <NavLink href="/blog">Blog</NavLink>
      <NavLink href="/pricing">Pricing</NavLink>
      <NavLink href="/cloud">Cloud</NavLink>
    </div>
  );
}
