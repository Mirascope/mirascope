/**
 * @fileoverview Analytics proxy API endpoint.
 *
 * This endpoint acts as a server-side proxy for analytics events, allowing
 * the frontend to send events to our own domain instead of directly to
 * third-party analytics services. This bypasses ad blockers and provides
 * better reliability.
 *
 * ## Flow
 * ```
 * Frontend → /api/analytics → Google Analytics + PostHog
 * ```
 *
 * All analytics calls are fire-and-forget - errors are logged but never
 * fail the request (always returns 200).
 */

import { createFileRoute } from "@tanstack/react-router";
import { Effect, Layer } from "effect";

import type { BrowserContext } from "@/app/lib/browser-context";

import { Analytics } from "@/analytics";
import { settingsLayer } from "@/server-entry";
import { Settings } from "@/settings";

/**
 * Analytics event request payload from the frontend.
 */
type AnalyticsEventRequest = {
  /** Type of analytics event */
  type: "event" | "pageview" | "identify";
  /** Event name (for trackEvent) */
  name?: string;
  /** Event or user properties */
  properties?: Record<string, unknown>;
  /** Page path (for trackPageView) */
  path?: string;
  /** Page title (for trackPageView) */
  title?: string;
  /** User ID (for identify) */
  userId?: string;
  /** PostHog distinct ID for user attribution */
  distinctId?: string;
  /** Browser context for rich analytics data */
  browserContext?: BrowserContext;
};

export const Route = createFileRoute("/api/analytics")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        try {
          const body: AnalyticsEventRequest = await request.json();

          await Effect.runPromise(
            Effect.gen(function* () {
              const analytics = yield* Analytics;

              switch (body.type) {
                case "event":
                  if (body.name) {
                    yield* analytics.trackEvent({
                      name: body.name,
                      properties: body.properties,
                      distinctId: body.distinctId,
                      browserContext: body.browserContext,
                    });
                  }
                  break;
                case "pageview":
                  yield* analytics.trackPageView({
                    path: body.path,
                    title: body.title,
                    distinctId: body.distinctId,
                    browserContext: body.browserContext,
                  });
                  break;
                case "identify":
                  if (body.userId) {
                    yield* analytics.identify({
                      userId: body.userId,
                      properties: body.properties,
                      browserContext: body.browserContext,
                    });
                  }
                  break;
              }
            }).pipe(
              Effect.provide(
                Layer.unwrapEffect(
                  Effect.gen(function* () {
                    const settings = yield* Settings;
                    return Layer.mergeAll(
                      Layer.succeed(Settings, settings),
                      Analytics.Live({
                        googleAnalytics: settings.googleAnalytics,
                        postHog: settings.posthog,
                      }),
                    );
                  }).pipe(Effect.provide(settingsLayer)),
                ),
              ),
            ),
          );

          return Response.json({ success: true });
        } catch (error) {
          // Never fail on analytics errors
          console.error("Analytics proxy error:", error);
          return Response.json({ success: false }, { status: 200 }); // Return 200 anyway
        }
      },
    },
  },
});
