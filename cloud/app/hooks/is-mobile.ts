import { useState, useEffect } from "react";

/**
 * Custom hook to detect if the current viewport is mobile size
 * Uses the 'sm' breakpoint (640px) from Tailwind as the threshold
 *
 * @returns boolean indicating if the viewport is mobile size
 */
export function useIsMobile(): boolean {
  // SM breakpoint in Tailwind is 640px
  const SM_BREAKPOINT = 640;

  // Initialize with a value based on window width if available
  // Otherwise default to false (assuming desktop) for SSR
  const [isMobile, setIsMobile] = useState<boolean>(() => {
    if (typeof window !== "undefined") {
      return window.innerWidth < SM_BREAKPOINT;
    }
    return false;
  });

  useEffect(() => {
    // Skip if not in browser environment
    if (typeof window === "undefined") return;

    // Function to check and update mobile status
    const checkMobile = () => {
      const mobile = window.innerWidth < SM_BREAKPOINT;
      if (mobile !== isMobile) {
        setIsMobile(mobile);
      }
    };

    // Run on mount and when window is resized
    checkMobile();
    window.addEventListener("resize", checkMobile);

    // Cleanup
    return () => window.removeEventListener("resize", checkMobile);
  }, [isMobile]);

  return isMobile;
}
