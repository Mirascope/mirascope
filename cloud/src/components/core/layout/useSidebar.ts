import { useEffect, useRef, useState } from "react";
import { useRouter } from "@tanstack/react-router";

// Breakpoint definitions - matching Tailwind's defaults
export const BREAKPOINTS = {
  md: 768, // Medium breakpoint (tablet)
  sm: 640, // Small breakpoint
  lg: 1024, // Large breakpoint
};

// Shared media query strings
export const MEDIA_QUERIES = {
  mdAndUp: `(min-width: ${BREAKPOINTS.md}px)`,
  mdAndDown: `(max-width: ${BREAKPOINTS.md - 1}px)`,
};

// Helper functions for responsive checks
export const isMobileView = (): boolean => {
  return typeof window !== "undefined" && window.matchMedia(MEDIA_QUERIES.mdAndDown).matches;
};

export const isDesktopView = (): boolean => {
  return typeof window !== "undefined" && window.matchMedia(MEDIA_QUERIES.mdAndUp).matches;
};

export interface UseSidebarOptions {
  /**
   * Function to call when this sidebar opens (to close another one)
   */
  onOpen?: () => void;

  /**
   * Whether to close the sidebar when the route changes
   * @default true
   */
  closeOnRouteChange?: boolean;
}

/**
 * Simple hook for managing mobile sidebar state
 * Desktop visibility is handled purely with CSS
 */
export function useSidebar({ onOpen, closeOnRouteChange = true }: UseSidebarOptions = {}) {
  // Only tracks the mobile state - desktop visibility is CSS-driven
  const [isOpen, setIsOpen] = useState(false);

  // Refs for focus management
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const previouslyFocusedElementRef = useRef<HTMLElement | null>(null);

  // Router for navigation tracking
  const router = useRouter();

  // Close on route change (mobile only)
  useEffect(() => {
    if (!closeOnRouteChange) return;

    const unsubscribe = router.subscribe("onResolved", () => {
      // Always close on navigation, but only on mobile
      if (isMobileView() && isOpen) {
        setIsOpen(false);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [router, isOpen, closeOnRouteChange]);

  // Handle toggling with focus management
  const toggle = () => {
    // Save the currently focused element when opening
    if (!isOpen) {
      previouslyFocusedElementRef.current = document.activeElement as HTMLElement;

      // Notify when opening
      if (onOpen) {
        onOpen();
      }
    }

    const newState = !isOpen;
    setIsOpen(newState);

    // Manage focus
    if (newState) {
      // Focus the close button when sidebar opens
      setTimeout(() => {
        closeBtnRef.current?.focus();
      }, 100);
    } else {
      // Restore focus when sidebar closes
      setTimeout(() => {
        previouslyFocusedElementRef.current?.focus();
      }, 100);
    }
  };

  // Force open/close functions
  const open = () => {
    if (!isOpen) toggle();
  };

  const close = () => {
    if (isOpen) setIsOpen(false);
  };

  // Auto-close on ESC key (mobile only)
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape" && isOpen) {
        setIsOpen(false);
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [isOpen]);

  return {
    isOpen,
    setIsOpen,
    toggle,
    open,
    close,
    closeBtnRef,
    previouslyFocusedElementRef,
  };
}
