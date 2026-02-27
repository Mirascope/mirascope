/**
 * @fileoverview Client-side analytics context.
 *
 * Provides a simple React context for tracking analytics events from
 * the frontend. All events are sent to our `/api/analytics` proxy endpoint
 * which forwards them to Google Analytics and PostHog server-side.
 *
 * This approach bypasses ad blockers since everything happens under our domain.
 *
 * ## Usage
 *
 * ```tsx
 * import { useAnalytics } from "@/app/contexts/analytics";
 *
 * function MyComponent() {
 *   const analytics = useAnalytics();
 *   const { user } = useAuth();
 *
 *   const handleClick = () => {
 *     analytics.trackEvent("button_clicked", { buttonId: "submit" }, user?.id);
 *   };
 *
 *   return <button onClick={handleClick}>Submit</button>;
 * }
 * ```
 */

import {
  createContext,
  useContext,
  useMemo,
  useRef,
  type ReactNode,
} from "react";

import {
  collectBrowserContext,
  type BrowserContext,
} from "@/app/lib/browser-context";

type AnalyticsContextType = {
  /**
   * Track a custom event.
   *
   * @param name - Event name (e.g., "button_clicked", "form_submitted")
   * @param properties - Optional event properties
   * @param distinctId - Optional PostHog distinct ID (user ID) for attribution
   */
  trackEvent: (
    name: string,
    properties?: Record<string, unknown>,
    distinctId?: string,
  ) => void;

  /**
   * Track a page view.
   *
   * @param params - Page path and title
   * @param distinctId - Optional PostHog distinct ID (user ID) for attribution
   */
  trackPageView: (
    params?: { path?: string; title?: string },
    distinctId?: string,
  ) => void;

  /**
   * Identify a user.
   *
   * @param userId - User identifier
   * @param properties - Optional user properties
   */
  identify: (userId: string, properties?: Record<string, unknown>) => void;
};

const AnalyticsContext = createContext<AnalyticsContextType | null>(null);

/**
 * Send analytics events to our proxy endpoint.
 *
 * This bypasses ad blockers by sending events to our own domain first,
 * which then forwards them to external analytics services server-side.
 *
 * Errors are silently caught - analytics should never break the app.
 */
async function sendToProxy(data: {
  type: "event" | "pageview" | "identify";
  name?: string;
  properties?: Record<string, unknown>;
  path?: string;
  title?: string;
  userId?: string;
  distinctId?: string;
  browserContext?: BrowserContext;
}) {
  // Only track real users in browsers, not prerender builds
  if (typeof document === "undefined") return;

  try {
    // Collect browser context for rich analytics data
    const browserContext = collectBrowserContext();

    await fetch("/api/analytics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...data,
        browserContext,
      }),
    });
  } catch (error) {
    // Silently fail - analytics should never break the app
    if (process.env.NODE_ENV === "development") {
      console.error("Analytics proxy request failed:", error);
    }
  }
}

/**
 * Provides analytics tracking functionality to the app.
 *
 * This provider should wrap AuthProvider since auth context needs to
 * track login/logout events.
 */
export function AnalyticsProvider({ children }: { children: ReactNode }) {
  /**
   * Store the last known user ID to automatically include it in subsequent
   * events. This ensures PostHog properly attributes all events to the user
   * even if the distinctId isn't explicitly passed to each tracking call.
   *
   * Updated when identify() is called.
   */
  const lastDistinctIdRef = useRef<string | undefined>(undefined);

  const contextValue = useMemo<AnalyticsContextType>(
    () => ({
      trackEvent: (name, properties, distinctId) => {
        // Only track real users in browsers, not prerender builds
        if (typeof document === "undefined") return;
        const id = distinctId || lastDistinctIdRef.current;
        void sendToProxy({ type: "event", name, properties, distinctId: id });
      },

      trackPageView: (params, distinctId) => {
        // Only track real users in browsers, not prerender builds
        if (typeof document === "undefined") return;
        const id = distinctId || lastDistinctIdRef.current;
        void sendToProxy({
          type: "pageview",
          path: params?.path,
          title: params?.title,
          distinctId: id,
        });
      },

      identify: (userId, properties) => {
        // Only track real users in browsers, not prerender builds
        if (typeof document === "undefined") return;
        // Remember this user ID for future events
        lastDistinctIdRef.current = userId;
        void sendToProxy({
          type: "identify",
          userId,
          properties,
          distinctId: userId,
        });
      },
    }),
    [], // Empty deps - these functions don't depend on any props or state
  );

  return (
    <AnalyticsContext.Provider value={contextValue}>
      {children}
    </AnalyticsContext.Provider>
  );
}

export function useAnalytics() {
  const context = useContext(AnalyticsContext);
  if (!context) {
    throw new Error("useAnalytics must be used within an AnalyticsProvider");
  }
  return context;
}
