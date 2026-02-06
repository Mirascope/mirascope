import { Link, useRouterState } from "@tanstack/react-router";
import { Menu, X } from "lucide-react";
import { useState, useEffect } from "react";

import DiscordLink from "@/app/components/blocks/branding/discord-link";
import GitHubMirascopeButton from "@/app/components/blocks/branding/github-mirascope-button";
import MirascopeLogo from "@/app/components/blocks/branding/mirascope-logo";
import { AccountMenu } from "@/app/components/blocks/navigation/account-menu";
import DesktopNavigation from "@/app/components/blocks/navigation/desktop-navigation";
import DocsSubNavbar from "@/app/components/blocks/navigation/docs-sub-navbar";
import MobileNavigation from "@/app/components/blocks/navigation/mobile-navigation";
import ResponsiveSearchWrapper from "@/app/components/blocks/navigation/responsive-search-wrapper";
import ThemeSwitcher from "@/app/components/blocks/navigation/theme-switcher";
import {
  useIsLandingPage,
  useIsRouterWaitlistPage,
} from "@/app/components/blocks/theme-provider";
import { CloudNavIcons } from "@/app/components/cloud-nav-icons";
import { NavbarCredits } from "@/app/components/navbar-credits";
import { cn } from "@/app/lib/utils";

import { HEADER_STYLES } from "./styles";

export default function Header() {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Determine if we're in cloud routes based on the current path
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const isCloudRoute =
    currentPath === "/cloud" || currentPath.startsWith("/cloud/");

  // Check if we're on docs pages (to show the section sub-navbar)
  const isDocsRoute =
    currentPath === "/docs" || currentPath.startsWith("/docs/");

  // Use the isLandingPage hook instead of router
  const isLandingPage = useIsLandingPage();

  // Use the isRouterWaitlistPage hook instead of router
  const isRouterWaitlistPage = useIsRouterWaitlistPage();

  // State to track scroll position
  const [scrolled, setScrolled] = useState(false);

  // Effect to handle scroll position
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };

    window.addEventListener("scroll", handleScroll);

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, [scrolled]);

  return (
    <header
      className={HEADER_STYLES.container(
        isLandingPage || isRouterWaitlistPage,
        scrolled,
        isCloudRoute,
      )}
    >
      <nav className={HEADER_STYLES.nav()}>
        <Link to="/" className={HEADER_STYLES.logo()}>
          <MirascopeLogo
            size="small"
            withText={true}
            textClassName={cn(HEADER_STYLES.logoText(isSearchOpen))}
            lightText={isLandingPage}
          />
        </Link>
        <DesktopNavigation isSearchOpen={isSearchOpen} />
        {/* Adding a grow spacer to push elements to edges */}
        <div className="grow"></div>

        {/* Search bar - hide on cloud routes */}
        {!isCloudRoute && (
          <ResponsiveSearchWrapper
            onOpenChange={(isOpen: boolean) => {
              setIsSearchOpen(isOpen);
            }}
          />
        )}
        {/* Right section with fixed controls */}
        <div className={HEADER_STYLES.controls}>
          {/* Desktop: GitHub + Discord buttons - hide on cloud routes */}
          {!isCloudRoute && (
            <div className={HEADER_STYLES.githubContainer}>
              <GitHubMirascopeButton />
            </div>
          )}

          {!isCloudRoute && (
            <div className={HEADER_STYLES.discordContainer}>
              <DiscordLink />
            </div>
          )}

          {/* Cloud nav icons + credits - show only on cloud routes */}
          {isCloudRoute && <CloudNavIcons />}
          {isCloudRoute && <NavbarCredits />}

          {/* Theme switcher - visible on all screen sizes */}
          <ThemeSwitcher />

          {/* Account menu - show at lg breakpoint */}
          <div className="hidden lg:flex">
            <AccountMenu />
          </div>

          {/* Mobile nav button - hidden on desktop */}
          <button
            className={HEADER_STYLES.mobileNavButton()}
            onClick={() => setIsMobileNavOpen(!isMobileNavOpen)}
            aria-label="Toggle mobile navigation"
          >
            {isMobileNavOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </nav>

      {/* Docs section sub-navbar - shows section links for docs pages */}
      {isDocsRoute && <DocsSubNavbar />}

      {/* Mobile Menu */}
      <MobileNavigation
        isOpen={isMobileNavOpen}
        onClose={() => setIsMobileNavOpen(false)}
      />
    </header>
  );
}
