/**
 * @fileoverview Automatic page view tracking hook.
 *
 * Provides a simple hook to automatically track page views whenever the
 * route changes. Includes user attribution if the user is logged in.
 */

import { useEffect } from "react";
import { useLocation } from "@tanstack/react-router";
import { useAnalytics } from "@/app/contexts/analytics";
import { useAuth } from "@/app/contexts/auth";

/**
 * Automatically tracks page views when the route changes.
 *
 * Call this hook once at the root of your app to track all route changes.
 * If a user is logged in, their ID will be included for proper attribution
 * in PostHog.
 *
 * @example
 * ```tsx
 * function AppContent() {
 *   usePageView(); // Tracks all route changes
 *
 *   return (
 *     <div>
 *       <Header />
 *       <Outlet />
 *     </div>
 *   );
 * }
 * ```
 */
export function usePageView() {
  const location = useLocation();
  const analytics = useAnalytics();
  const { user } = useAuth();

  useEffect(() => {
    // Only track page views on the client
    if (typeof window === "undefined") return;

    analytics.trackPageView(
      {
        path: location.pathname,
        title: document.title,
      },
      user?.id, // Pass user ID for PostHog distinct_id
    );
  }, [location.pathname, analytics, user?.id]);
}
