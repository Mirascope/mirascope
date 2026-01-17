import { cn } from "@/app/lib/utils";

/**
 * Animation timing configuration
 * All durations in milliseconds
 */
export const ANIMATION_TIMING = {
  // Phase 1: Logo and text fade out
  logoFade: {
    duration: 100,
  },
  // Phase 2: Search bar expansion
  searchExpand: {
    delay: 0, // Wait for logo to fade
    duration: 400,
  },
  // Phase 3: Search results appearance
  resultsAppear: {
    delay: 100,
    duration: 300,
  },
  // Computed total animation duration (for JS timers)
  getTotalDuration: () =>
    ANIMATION_TIMING.logoFade.duration +
    ANIMATION_TIMING.searchExpand.delay +
    ANIMATION_TIMING.searchExpand.duration,
  // For results timing
  getResultsDelay: () =>
    ANIMATION_TIMING.logoFade.duration +
    ANIMATION_TIMING.searchExpand.delay +
    Math.floor(ANIMATION_TIMING.searchExpand.duration / 2),
};

/**
 * Header styles for main site header
 */
export const HEADER_STYLES = {
  // Container styles for the header with conditional appearance based on landing page and scroll
  container: (isLandingPage: boolean, scrolled: boolean) =>
    cn(
      // Fixed positioning and layout
      "fixed top-0 right-0 left-0 z-[100] mb-2 flex w-full flex-col items-center justify-center px-3 py-2 md:px-6",
      // Text styling for landing page
      "font-handwriting",
      // Background color (only on non-landing pages)
      isLandingPage ? "" : "bg-background",
      // Bottom border and shadow when scrolled (only on non-landing pages)
      scrolled && !isLandingPage ? "border-border border-b shadow-sm" : "",
    ),

  // Navigation container - expands to full width when in cloud routes
  nav: (isCloudRoute: boolean = false) =>
    cn(
      "mx-auto flex w-full flex-row items-center space-x-2",
      // Only constrain width when not in cloud routes
      !isCloudRoute && "max-w-7xl",
    ),

  // Logo link container
  logo: (isLandingPage: boolean) =>
    cn(
      "relative z-10 flex items-center flex-shrink-0 px-1 mr-2",
      isLandingPage ? "invisible" : "visible",
    ),

  // Logo text container with fade transition
  logoText: (isSearchOpen: boolean) =>
    cn(
      // Use timing from central configuration
      `transition-all duration-[${ANIMATION_TIMING.logoFade.duration}ms] ease-in-out`,
      // On small screens when search is open, fade out the text but maintain position
      isSearchOpen
        ? "opacity-0 md:opacity-100 w-0 md:w-auto overflow-hidden md:overflow-visible pointer-events-none md:pointer-events-auto translate-x-0"
        : "opacity-100 w-auto overflow-visible pointer-events-auto translate-x-0",
    ),

  // Right section with controls
  controls: cn(
    "flex items-center gap-2 md:gap-3 flex-shrink-0",
    // Keep controls at the right edge but prevent shrinking
    "justify-end",
  ),

  // GitHub button container - show at lg breakpoint to match nav tabs
  githubContainer: "hidden items-center gap-3 lg:flex",

  // Discord link button container - show at lg breakpoint to match nav tabs
  discordContainer: "hidden items-center gap-3 lg:flex",

  // Mobile nav toggle button - hide at lg breakpoint to match nav tabs
  mobileNavButton: () => cn("p-2 lg:hidden", "nav-icon"),

  // Product selector container
  productSelector: "mx-auto flex w-full max-w-7xl pt-3 pb-1",
};

/**
 * Shared navigation link styles for desktop and mobile
 */
export const NAV_LINK_STYLES = {
  // Base styles for desktop navigation links
  base: cn(
    // Layout and typography
    "relative flex cursor-pointer items-center px-2 py-2 text-xl font-medium",
    // Uses the nav-text utility for consistent text styling based on page type
    "nav-text",
  ),

  // Active state for desktop navigation links
  active: cn(
    // Highlight the active link - use !important to override nav-text utility
    "!text-primary font-semibold",
  ),

  // Styles for mobile navigation links
  mobile: cn(
    // Base styles
    "relative flex cursor-pointer items-center py-2 text-xl font-medium",
    // Transitions
    "transition-colors duration-300 ease-in-out",
    // Interactive states
    "hover:text-primary",
  ),

  // Active state for mobile navigation links
  mobileActive: cn(
    // Highlight the active link - use !important to override any base styles
    "!text-primary font-semibold",
  ),
};

/**
 * Product card/link styles for both desktop and mobile
 */
export const PRODUCT_LINK_STYLES = {
  // Desktop product card styles in dropdown menu
  desktop: {
    container: cn(
      // Base styles
      "bg-background block space-y-1.5 rounded-md p-4",
      // Transition properties
      "transition-colors duration-300 ease-in-out",
      // Interactive states
      "hover:bg-primary/20 focus:bg-primary/20",
      "active:bg-primary/60 active:scale-[0.98]",
      // Selected state via data attribute
      "data-[active=true]:bg-primary/50 data-[active=true]:hover:bg-primary/60",
    ),
    title: "text-primary text-xl font-medium",
    description: "text-foreground text-base",
  },

  // Mobile product link styles
  mobile: {
    container: cn(
      // Base styles
      "bg-background text-primary rounded-md p-3 font-medium",
      // Transitions
      "transition-colors duration-300 ease-in-out",
      // Interactive states
      "hover:bg-primary/20 focus:bg-primary/20",
      "active:bg-primary/60 active:scale-[0.98]",
    ),
  },
};

/**
 * Mobile nav styles for dropdown navigation
 * Note: Using lg:hidden to match desktop nav lg:flex breakpoint
 */
export const MOBILE_NAV_STYLES = {
  // Container for the entire mobile navigation
  container: cn(
    // Positioning and layout - z-index higher than header (z-[100])
    "absolute top-full right-4 z-[110] mt-2 max-w-xs lg:hidden",
    // Appearance
    "bg-background text-foreground rounded-lg p-6 shadow-lg",
    // Reset text shadow from parent header
    "[text-shadow:none]",
  ),

  // Content container
  content: "flex flex-col space-y-4",

  // Section title (e.g. "Docs")
  sectionTitle: "my-2 text-xl font-medium",

  // Divider between sections
  divider: "my-2",
};

/**
 * Theme switcher component styles
 */
export const THEME_SWITCHER_STYLES = {
  // Button trigger styles
  trigger: cn(
    // Base styles
    "rounded-md p-2 cursor-pointer",
    // Transitions
    "transition-colors duration-300 ease-in-out",
    // Focus state
    "focus:outline-none focus:ring-2 focus:ring-primary",
    // Icon styling from nav (includes default color)
    "nav-icon",
    // Hover color change (similar to nav links)
    "hover:text-primary",
  ),

  // Dropdown content - z-index higher than header (z-[100])
  content: (isLandingPage: boolean) =>
    cn(
      // Base styling comes from the UI component
      // z-index to appear above header, mt-2 for spacing from trigger
      "z-[110] mt-2",
      // Apply textured background on landing page
      isLandingPage && "textured-bg-absolute",
    ),

  // Radio items (inherited from dropdown menu component)
  radioItem: cn(
    // Added styles for consistent interaction
    "transition-colors",
    "focus:bg-primary/20 data-[highlighted]:bg-primary/20",
  ),
};

/**
 * Search state styles for coordinated animations
 * Note: Using xl breakpoint (1280px) instead of lg (1024px) to accommodate Cloud tab
 */
export const SEARCH_STATE_STYLES = {
  closed: {
    container: "w-9 xl:w-36 flex-shrink-0",
    input: "w-0 opacity-0 xl:w-28 xl:pr-3 xl:pl-10 xl:opacity-80",
    icon: "mx-auto xl:absolute xl:left-3",
  },
  open: {
    container: "w-[40rem] flex-shrink min-w-[200px] max-w-full",
    input: "w-full pr-9 pl-10 opacity-100",
    icon: "absolute left-3",
  },
};

/**
 * Desktop navigation styles
 * Note: Using lg breakpoint (1024px) instead of md (768px) to accommodate Cloud tab
 */
export const DESKTOP_NAV_STYLES = {
  // Container styles
  container: (isSearchOpen: boolean) =>
    cn(
      // Base styles - always centered, show at lg breakpoint for Cloud tab space
      "absolute left-1/2 z-20 hidden -translate-x-1/2 transform items-center gap-6 lg:flex",
      // Transitions
      "transition-opacity duration-300 ease-in-out",
      // Only hide when search is open
      isSearchOpen ? "pointer-events-none opacity-0" : "opacity-100",
    ),

  // Mobile nav trigger styles
  mobileNavTrigger: cn(
    // Base styles
    "flex cursor-pointer items-center !bg-transparent p-0 text-xl font-medium",
    // Transitions
    "transition-colors duration-300 ease-in-out",
    // Interactive states - maintaining transparency
    "hover:!bg-transparent focus:!bg-transparent data-[state=open]:!bg-transparent data-[state=open]:hover:!bg-transparent",
    // Text styling consistent with nav
    "nav-text",
  ),

  // Mobile nav content styles
  mobileNavContent: (isLandingPage: boolean) =>
    cn(
      // Base styles
      "bg-background p-2 [text-shadow:none]",
      // Conditional textured background
      isLandingPage ? "textured-bg-absolute" : "",
    ),

  // Product grid styles
  productGrid: "grid w-[300px] grid-cols-1 gap-2 sm:w-[480px] sm:grid-cols-2",

  // Trigger text container
  triggerText: "px-2 py-2",
};

/**
 * Search bar component styles
 */
export const SEARCH_BAR_STYLES = {
  // Container styles - responsible for overall width
  container: (isOpen: boolean) =>
    cn(
      "search-container",
      "relative flex items-center",
      // Add transitions using centralized timing config
      `transition-all duration-[${ANIMATION_TIMING.searchExpand.duration}ms] ease-in-out delay-[${ANIMATION_TIMING.searchExpand.delay}ms]`,
      // Simplified width approach - set ideal width with flex-shrink to respect space
      isOpen
        ? SEARCH_STATE_STYLES.open.container
        : SEARCH_STATE_STYLES.closed.container,
    ),

  // Mobile search button
  mobileSearchButton: (isLandingPage: boolean) =>
    cn(
      "relative flex items-center justify-center w-9 h-9 rounded-full",
      "transition-colors duration-300",
      isLandingPage
        ? "border-0 bg-white/10 hover:bg-white/20"
        : "bg-background/20 hover:bg-primary/10 hover:border-primary/80 border",
    ),

  // Mobile search overlay container
  mobileOverlay: (isOpen: boolean) =>
    cn(
      // Positioning and layout - cover entire screen
      "fixed inset-0 z-[90] flex flex-col",
      // More transparent background with subtle blur effect
      "bg-background/10 mr-0 backdrop-blur-[2px]",
      // Transition properties
      `transition-all duration-[${ANIMATION_TIMING.searchExpand.duration}ms] ease-in-out`,
      // Visibility based on search state
      isOpen
        ? "opacity-100 pointer-events-auto"
        : "opacity-0 pointer-events-none",
    ),

  // Mobile search inner container
  mobileSearchContainer: cn("w-full px-3 py-2 flex items-center"),

  // Close button for mobile overlay
  closeButton: (isLandingPage: boolean) =>
    cn(
      "absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full",
      "transition-colors duration-300",
      "cursor-pointer",
      isLandingPage ? "text-white" : "text-foreground",
    ),

  // Input container styles - matches parent width
  inputContainer: (isLandingPage: boolean, isMobile: boolean) =>
    cn(
      "search-input-container",
      // Base styles
      "h-9 rounded-full relative flex items-center overflow-visible w-full",
      // Conditional styles based on page type
      isLandingPage
        ? "border-0 bg-white/10 hover:bg-white/20"
        : "border-border bg-background/20 hover:bg-primary/10 hover:border-primary/80 border",
      isMobile && !isLandingPage ? "bg-background hover:bg-background" : "",
    ),

  // Inline styles for input container based on landing page
  getInputContainerStyles: (isLandingPage: boolean) =>
    isLandingPage
      ? {
          boxShadow:
            "0 1px 5px rgba(0, 0, 0, 0.15), 0 2px 10px rgba(0, 0, 0, 0.1)",
        }
      : undefined,

  // Search icon styles
  icon: (isOpen: boolean) =>
    cn(
      // Transitions from central config - match container timing
      `transition-all duration-[${ANIMATION_TIMING.searchExpand.duration}ms] ease-in-out delay-[${ANIMATION_TIMING.searchExpand.delay}ms]`,
      // Icon styling
      "nav-icon",
      // Position based on open state
      isOpen ? SEARCH_STATE_STYLES.open.icon : SEARCH_STATE_STYLES.closed.icon,
    ),

  // Input field styles
  input: (isOpen: boolean, isLandingPage: boolean, isMobile: boolean = false) =>
    cn(
      // Base styles
      "cursor-pointer overflow-visible bg-transparent py-0 outline-none",
      "!text-[16px] leading-normal", // Use 16px font to avoid zoom on mobile
      "h-auto min-h-full",
      // Transitions from central config - match container timing
      `transition-all duration-[${ANIMATION_TIMING.searchExpand.duration}ms] ease-in-out delay-[${ANIMATION_TIMING.searchExpand.delay}ms]`,
      // Text color based on page type
      isLandingPage
        ? "text-white placeholder:text-white/90"
        : "text-foreground placeholder:text-foreground",
      // Visibility and spacing based on open state - add extra right padding in mobile mode for close button
      isOpen
        ? isMobile
          ? "w-full pr-8 pl-10 opacity-100"
          : SEARCH_STATE_STYLES.open.input
        : SEARCH_STATE_STYLES.closed.input,
    ),

  // Keyboard shortcut badge
  kbd: (isLandingPage: boolean, isOpen: boolean = false) =>
    cn(
      "font-small absolute top-1/2 right-3 h-5 -translate-y-1/2 items-center gap-1 rounded border px-1.5 font-mono text-[10px]",
      // Make it always hidden on mobile
      "hidden lg:flex",
      // Add transition with a slight delay to let search bar expand first
      `transition-all duration-[300ms] ease-in-out delay-[${ANIMATION_TIMING.searchExpand.delay + 200}ms]`,
      // Dynamic appearance based on search state
      isOpen
        ? "opacity-80 translate-x-0 scale-100"
        : "opacity-0 translate-x-4 scale-90 pointer-events-none",
      // Background color based on page type
      isLandingPage
        ? "bg-white/10 text-white"
        : "border-border bg-muted text-foreground",
    ),

  // Results container - matches parent container width
  resultsContainer: (
    isLandingPage: boolean,
    isMobile: boolean = false,
    isVisible: boolean = false,
  ) =>
    cn(
      // Base styles
      "search-results overflow-hidden rounded-lg shadow-2xl [text-shadow:none]",
      "bg-background border-border border",
      "transition-opacity duration-300 ease-in-out",
      "font-sans",
      // Use Tailwind's animation utilities for better control with a subtle slide effect
      isVisible
        ? "pointer-events-auto opacity-100"
        : "pointer-events-none opacity-0",
      // Match width to parent container (container manages actual width constraints)
      "w-full",
      // Mobile vs desktop positioning
      isMobile
        ? "absolute top-full mt-4 left-0 right-0 z-[90] max-h-[calc(100vh-var(--header-height-base)*1.2)]" // Mobile: now part of the overlay
        : "absolute top-full z-50 mt-2 right-0 lg:right-auto lg:left-0", // Desktop: dropdown below
      // Conditional textured background
      isLandingPage ? "textured-bg-absolute" : "",
    ),

  // Inline styles for results container based on page type
  // No longer controlling opacity here since it's handled by classes
  getResultsContainerStyles: (isLandingPage: boolean) => {
    if (isLandingPage) {
      return {
        boxShadow:
          "0 1px 5px rgba(0, 0, 0, 0.15), 0 2px 10px rgba(0, 0, 0, 0.1)",
      };
    }

    return {};
  },

  // Search result styles
  result: (isSelected: boolean) =>
    cn(
      // Base styles
      "border-border/40 flex border-t px-5 py-4 text-sm first:border-0",
      // Transitions
      "transition-colors duration-150",
      // Selected state
      isSelected ? "bg-accent/50" : "",
    ),

  // Search footer styles
  footer:
    "border-border bg-muted/40 text-muted-foreground flex items-center justify-between border-t p-2 text-xs font-handwriting",

  // Loading indicator
  loadingIndicator:
    "border-primary h-6 w-6 animate-spin rounded-full border-t-2 border-b-2",
};
