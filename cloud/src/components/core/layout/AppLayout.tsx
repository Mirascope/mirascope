import type { ReactNode } from "react";
import { createContext, useContext, useEffect } from "react";
import { cn } from "@/src/lib/utils";
import { Button } from "@/mirascope-ui/ui/button";
import { ChevronLeft, ChevronRight, X, type LucideIcon } from "lucide-react";
import { useSidebar, isMobileView } from "./useSidebar";

// Shared positioning for sidebar toggle buttons
const SIDEBAR_TOGGLE_POSITION = "calc(var(--header-height) - 1.63rem)";

// Create a context to coordinate sidebar states
type SidebarContextType = {
  leftSidebar: ReturnType<typeof useSidebar>;
  rightSidebar: ReturnType<typeof useSidebar>;
};

const SidebarContext = createContext<SidebarContextType>({
  leftSidebar: {
    isOpen: false,
    setIsOpen: () => {},
    toggle: () => {},
    open: () => {},
    close: () => {},
    closeBtnRef: { current: null },
    previouslyFocusedElementRef: { current: null },
  },
  rightSidebar: {
    isOpen: false,
    setIsOpen: () => {},
    toggle: () => {},
    open: () => {},
    close: () => {},
    closeBtnRef: { current: null },
    previouslyFocusedElementRef: { current: null },
  },
});

/**
 * Toggle button for controlling sidebars with consistent styling
 */
interface SidebarToggleProps {
  isOpen: boolean;
  onClick: () => void;
  position: "left" | "right";
  className?: string;
  ariaLabel: string;
  ariaControls: string;
  buttonRef?: React.RefObject<HTMLButtonElement | null>;
}

const SidebarToggle = ({
  isOpen,
  onClick,
  position,
  className,
  ariaLabel,
  ariaControls,
  buttonRef,
}: SidebarToggleProps) => {
  // Choose icon based on position and state
  const getIcon = (): LucideIcon => {
    if (isOpen) return X;
    return position === "left" ? ChevronRight : ChevronLeft;
  };

  const Icon = getIcon();

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={onClick}
      className={cn(
        "z-80 rounded-full border-1 p-0 shadow-md",
        "h-6 w-6",
        isOpen ? "bg-muted" : "bg-background",
        className
      )}
      ref={buttonRef}
      aria-label={ariaLabel}
      aria-expanded={isOpen}
      aria-controls={ariaControls}
    >
      <Icon className="h-5 w-5" />
    </Button>
  );
};

/**
 * AppLayout - Comprehensive layout component with composable parts
 *
 * Provides a consistent page structure with main content area and
 * optional sidebars. Sidebars use fixed positioning for scrolling behavior.
 * Manages responsive behavior for both left and right sidebars.
 * Header spacing is handled by the root layout.
 *
 * Usage example:
 * ```tsx
 * <AppLayout>
 *   <AppLayout.LeftSidebar>Left sidebar content</AppLayout.LeftSidebar>
 *   <AppLayout.Content>Main content</AppLayout.Content>
 *   <AppLayout.RightSidebar>Right sidebar content</AppLayout.RightSidebar>
 * </AppLayout>
 * ```
 */
const AppLayout = ({ children }: { children: ReactNode }) => {
  // Create sidebar controllers with coordinated behavior
  // The hook now handles only mobile behavior
  const leftSidebar = useSidebar({
    onOpen: () => rightSidebar.close(),
  });

  const rightSidebar = useSidebar({
    onOpen: () => leftSidebar.close(),
  });

  // Manage body scroll lock when sidebars are open on mobile
  useEffect(() => {
    if (isMobileView() && (leftSidebar.isOpen || rightSidebar.isOpen)) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }

    return () => {
      document.body.style.overflow = "";
    };
  }, [leftSidebar.isOpen, rightSidebar.isOpen]);

  return (
    <SidebarContext.Provider
      value={{
        leftSidebar,
        rightSidebar,
      }}
    >
      <div className="flex justify-center">
        <div className="mx-auto flex w-full max-w-7xl">{children}</div>
      </div>
    </SidebarContext.Provider>
  );
};

interface SidebarProps {
  children: ReactNode;
  className?: string;
  collapsible?: boolean;
}

interface RightSidebarProps extends SidebarProps {
  mobileCollapsible?: boolean;
  mobileTitle?: string;
}

/**
 * Shared backdrop component for mobile sidebar overlays
 */
const SidebarBackdrop = ({ isOpen, onClick }: { isOpen: boolean; onClick: () => void }) => (
  <div
    className={`bg-background/30 fixed inset-0 backdrop-blur-sm transition-all duration-300 ${
      isOpen ? "z-40 opacity-100" : "pointer-events-none -z-10 opacity-0"
    }`}
    onClick={onClick}
    aria-hidden="true"
    role="presentation"
  />
);

/**
 * Left sidebar component with fixed positioning and collapsible behavior
 *
 * Handles responsive collapsing on small screens with CSS media queries.
 * Sidebar content scrolls independently from main content.
 */
AppLayout.LeftSidebar = ({ children, className, collapsible = true }: SidebarProps) => {
  const { leftSidebar } = useContext(SidebarContext);
  const isOpen = leftSidebar.isOpen;

  const { rightSidebar } = useContext(SidebarContext);
  const rightSidebarIsOpen = rightSidebar.isOpen;

  // Determine whether to show the left sidebar toggle as an X
  // Show X if:
  // 1. The left sidebar is open, OR
  // 2. The right sidebar is open
  const showAsX = isOpen || rightSidebarIsOpen;

  // Determine what action to take when the toggle is clicked
  const handleToggleClick = () => {
    if (rightSidebarIsOpen) {
      // If right sidebar is open, clicking the X should close it
      rightSidebar.close();
    } else {
      // Otherwise, toggle the left sidebar as usual
      leftSidebar.toggle();
    }
  };

  return (
    <>
      {/* Container div - fixed size on desktop (CSS-driven), zero width on mobile */}
      <div className="w-0 flex-shrink-0 md:w-64">
        {/* Mobile backdrop - only visible when sidebar is open */}
        <div className="md:hidden">
          <SidebarBackdrop isOpen={isOpen} onClick={() => leftSidebar.close()} />
        </div>

        {/* Toggle button - only visible on mobile when collapsible */}
        {collapsible && (
          <div
            className={cn(
              "fixed left-4 z-80 md:hidden",
              rightSidebarIsOpen && "hidden" // Hide when right sidebar is open
            )}
            style={{ top: SIDEBAR_TOGGLE_POSITION }}
          >
            <SidebarToggle
              isOpen={showAsX}
              onClick={handleToggleClick}
              position="left"
              ariaLabel={
                showAsX
                  ? rightSidebarIsOpen
                    ? "Close right sidebar"
                    : "Close sidebar"
                  : "Open sidebar"
              }
              ariaControls={rightSidebarIsOpen ? "right-sidebar-content" : "left-sidebar-content"}
              buttonRef={leftSidebar.closeBtnRef}
            />
          </div>
        )}

        {/* Sidebar content panel - always visible on desktop (via CSS), mobile-controlled */}
        <div
          id="left-sidebar-content"
          className={cn(
            // Base styles
            "fixed top-[var(--header-height)] z-40 overflow-hidden",
            // Update height to account for footer
            "h-[calc(100vh-var(--header-height)-var(--footer-height,40px))]",
            "bg-background/95 border-border/40 backdrop-blur-sm",
            // Responsive behavior split between mobile/desktop
            // Mobile: controlled by JS state via transform
            "md:translate-x-0", // Always visible on desktop
            !isOpen && "translate-x-[-110%] md:translate-x-0", // Hidden on mobile when closed
            // Size and appearance
            "w-[calc(100vw-20px)] max-w-xs sm:w-[85vw] md:w-64",
            "rounded-r-md",
            // Always display on desktop, unless non-collapsible on mobile
            !collapsible && "md:block",
            // Animation
            "transition-transform duration-300 ease-in-out"
          )}
          style={{
            boxShadow: isOpen && isMobileView() ? "0 8px 16px rgba(0, 0, 0, 0.08)" : "none",
          }}
          aria-hidden={!isOpen && isMobileView()}
          role="navigation"
        >
          {/* Padding is responsive via CSS - more padding on mobile to match right sidebar */}
          <div className="h-full overflow-y-auto p-5 md:px-4 md:py-0">
            <div className={cn("h-full overflow-y-auto", className)}>{children}</div>
          </div>
        </div>
      </div>
    </>
  );
};

/**
 * Main content area
 *
 * Expands to fill available space between sidebars and scrolls independently.
 */
AppLayout.Content = ({ children, className }: SidebarProps) => {
  return <div className={cn("min-w-0 flex-1", className)}>{children}</div>;
};

/**
 * Right sidebar component with fixed positioning
 *
 * Provides a consistent container for right sidebar content that
 * remains fixed while the main content scrolls.
 *
 * When mobileCollapsible is true, the sidebar will be accessible on mobile
 * devices via a toggle button that shows a slide-in panel.
 */
AppLayout.RightSidebar = ({
  children,
  className,
  mobileCollapsible = false,
}: RightSidebarProps) => {
  const { leftSidebar, rightSidebar } = useContext(SidebarContext);
  const isOpen = rightSidebar.isOpen;
  const leftIsOpen = leftSidebar.isOpen;

  return (
    <>
      {/* Desktop version - always visible on large screens via CSS */}
      <div className="hidden w-56 flex-shrink-0 lg:block">
        {children && (
          <div
            className={cn(
              "fixed top-[var(--header-height)]",
              "h-[calc(100vh-var(--header-height)-var(--footer-height,40px))]",
              "w-56 max-w-[14rem] overflow-y-auto",
              className
            )}
          >
            {children}
          </div>
        )}
      </div>

      {/* Mobile version - only render if mobileCollapsible is true */}
      {mobileCollapsible && children && (
        <>
          {/* Mobile toggle button - hidden when left sidebar is open or on large screens */}
          <div
            className={cn("fixed right-4 z-80 lg:hidden", leftIsOpen && "hidden")}
            style={{ top: SIDEBAR_TOGGLE_POSITION }}
          >
            <SidebarToggle
              isOpen={isOpen}
              onClick={rightSidebar.toggle}
              position="right"
              ariaLabel={isOpen ? "Close table of contents" : "Open table of contents"}
              ariaControls="right-sidebar-content"
              buttonRef={rightSidebar.closeBtnRef}
            />
          </div>

          {/* Mobile backdrop overlay */}
          <div className="lg:hidden">
            <SidebarBackdrop isOpen={isOpen} onClick={() => rightSidebar.close()} />
          </div>

          {/* Mobile slide-in panel */}
          <div
            id="right-sidebar-content"
            className={cn(
              "bg-background border-border fixed top-[var(--header-height)] right-0 z-40",
              "h-[calc(100vh-var(--header-height)-var(--footer-height,40px))] w-72 rounded-md border-l shadow-lg",
              "transition-transform duration-300 ease-in-out lg:hidden",
              isOpen ? "translate-x-0" : "translate-x-full"
            )}
            aria-hidden={!isOpen}
            role="complementary"
          >
            <div className="flex h-full flex-col">
              {/* Simple padding on top instead of the header bar with X button */}
              <div className="flex-grow overflow-y-auto p-5">{children}</div>
            </div>
          </div>
        </>
      )}
    </>
  );
};

export default AppLayout;
