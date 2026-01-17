import { Link, useRouterState } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Menu, X } from "lucide-react";
import GitHubMirascopeButton from "@/app/components/blocks/branding/github-mirascope-button";
import DiscordLink from "@/app/components/blocks/branding/discord-link";
import MirascopeLogo from "@/app/components/blocks/branding/mirascope-logo";
import ThemeSwitcher from "@/app/components/blocks/navigation/theme-switcher";
import DesktopNavigation from "@/app/components/blocks/navigation/desktop-navigation";
import MobileNavigation from "@/app/components/blocks/navigation/mobile-navigation";
import ResponsiveSearchWrapper from "@/app/components/blocks/navigation/responsive-search-wrapper";
import {
  useIsLandingPage,
  useIsRouterWaitlistPage,
} from "@/app/components/blocks/theme-provider";
import { HEADER_STYLES } from "./styles";
import { cn } from "@/app/lib/utils";

export default function Header() {
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Determine if we're in cloud routes based on the current path
  const router = useRouterState();
  const currentPath = router.location.pathname;
  const isCloudRoute =
    currentPath === "/cloud" || currentPath.startsWith("/cloud/");

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
      <nav className={HEADER_STYLES.nav(isCloudRoute)}>
        <Link
          to="/"
          className={HEADER_STYLES.logo(isLandingPage || isRouterWaitlistPage)}
        >
          <MirascopeLogo
            size="small"
            withText={true}
            textClassName={cn(HEADER_STYLES.logoText(isSearchOpen))}
          />
        </Link>
        <DesktopNavigation isSearchOpen={isSearchOpen} />
        {/* Adding a grow spacer to push elements to edges */}
        <div className="grow"></div>

        {/* Search bar in the middle with ability to grow/shrink */}
        <ResponsiveSearchWrapper
          onOpenChange={(isOpen: boolean) => {
            setIsSearchOpen(isOpen);
          }}
        />
        {/* Right section with fixed controls */}
        <div className={HEADER_STYLES.controls}>
          {/* Desktop: GitHub + Theme buttons */}
          <div className={HEADER_STYLES.githubContainer}>
            <GitHubMirascopeButton />
          </div>

          <div className={HEADER_STYLES.discordContainer}>
            <DiscordLink />
          </div>

          {/* Theme switcher - visible on all screen sizes */}
          <ThemeSwitcher />

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

      {/* Mobile Menu */}
      <MobileNavigation
        isOpen={isMobileNavOpen}
        onClose={() => setIsMobileNavOpen(false)}
      />
    </header>
  );
}
