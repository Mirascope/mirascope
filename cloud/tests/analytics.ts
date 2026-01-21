/**
 * @fileoverview Mock analytics providers for unit testing.
 *
 * Provides factory functions for creating mock GoogleAnalytics and PostHog
 * clients with vi.fn() spies for testing the Analytics service.
 */

import { vi } from "vitest";
import { Effect } from "effect";
import type { GoogleAnalyticsClient } from "@/analytics/google-client";
import type { PostHogClient } from "@/analytics/posthog-client";

/**
 * Creates a mock GoogleAnalytics client with vi.fn() spies.
 *
 * All methods return successful Effects by default.
 * Reassign methods to simulate failures.
 */
export function MockGoogleAnalytics(): GoogleAnalyticsClient {
  return {
    type: "noop" as const,
    initialize: vi.fn(() => Effect.succeed(void 0)),
    trackEvent: vi.fn(() => Effect.succeed(void 0)),
    trackPageView: vi.fn(() => Effect.succeed(void 0)),
    setUserId: vi.fn(() => Effect.succeed(void 0)),
  };
}

/**
 * Creates a mock PostHog client with vi.fn() spies.
 *
 * All methods return successful Effects by default.
 * Reassign methods to simulate failures.
 */
export function MockPostHog(): PostHogClient {
  return {
    type: "noop" as const,
    initialize: vi.fn(() => Effect.succeed(void 0)),
    trackEvent: vi.fn(() => Effect.succeed(void 0)),
    trackPageView: vi.fn(() => Effect.succeed(void 0)),
    identify: vi.fn(() => Effect.succeed(void 0)),
  };
}
