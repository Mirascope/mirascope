/**
 * @fileoverview Analytics service layer.
 *
 * This module provides the `Analytics` service which aggregates Google Analytics
 * and PostHog, providing a unified interface for tracking events, page views,
 * and user identification across both platforms.
 *
 * ## Architecture
 *
 * ```
 * Analytics (aggregator service)
 *   ├── googleAnalytics: GoogleAnalyticsClient
 *   ├── postHog: PostHogClient
 *   ├── trackEvent() → calls both in parallel
 *   ├── trackPageView() → calls both in parallel
 *   ├── identify() → calls both in parallel
 *   └── initialize() → calls both in parallel
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { Analytics } from "@/analytics";
 *
 * const program = Effect.gen(function* () {
 *   const analytics = yield* Analytics;
 *
 *   // Initialize both providers
 *   yield* analytics.initialize();
 *
 *   // Track events across both platforms
 *   yield* analytics.trackEvent({
 *     name: "sign_up",
 *     properties: { method: "email" }
 *   });
 *
 *   // Track page views
 *   yield* analytics.trackPageView({
 *     path: "/dashboard",
 *     title: "Dashboard"
 *   });
 *
 *   // Identify users
 *   yield* analytics.identify({
 *     userId: "user_123",
 *     properties: { email: "user@example.com" }
 *   });
 * });
 *
 * // Provide the Analytics layer
 * program.pipe(
 *   Effect.provide(Analytics.Live({
 *     googleAnalytics: { measurementId: "G-XXXXXXXXXX" },
 *     postHog: { apiKey: "phc_..." }
 *   }))
 * );
 * ```
 *
 * ## Error Handling
 *
 * All operations return `Effect<void, never>` - errors are caught internally by
 * the underlying providers and logged. Analytics failures never break the application.
 */

import { Effect, Layer, Context } from "effect";
import {
  GoogleAnalytics,
  type GoogleAnalyticsClient,
  type GoogleAnalyticsConfig,
} from "@/analytics/google-client";
import {
  PostHog,
  type PostHogClient,
  type PostHogConfig,
} from "@/analytics/posthog-client";

/**
 * Analytics service configuration options.
 */
export interface AnalyticsConfig {
  /** Google Analytics configuration */
  googleAnalytics: Partial<GoogleAnalyticsConfig>;
  /** PostHog configuration */
  postHog: Partial<PostHogConfig>;
}

/**
 * Parameters for tracking events.
 */
export interface TrackEventParams {
  /** Name of the event (e.g., "sign_up", "purchase") */
  name: string;
  /** Event properties */
  properties?: Record<string, unknown>;
}

/**
 * Parameters for tracking page views.
 */
export interface TrackPageViewParams {
  /** Page path (e.g., "/dashboard") */
  path?: string;
  /** Page title */
  title?: string;
}

/**
 * Parameters for identifying users.
 */
export interface IdentifyParams {
  /** User identifier */
  userId: string;
  /** User properties */
  properties?: Record<string, unknown>;
}

/**
 * Analytics service interface.
 */
export interface AnalyticsService {
  /** Direct access to GoogleAnalytics client */
  readonly googleAnalytics: GoogleAnalyticsClient;
  /** Direct access to PostHog client */
  readonly postHog: PostHogClient;
  /** Initialize both analytics providers */
  initialize(): Effect.Effect<void, never>;
  /** Track a custom event across both platforms */
  trackEvent(params: TrackEventParams): Effect.Effect<void, never>;
  /** Track a page view across both platforms */
  trackPageView(params?: TrackPageViewParams): Effect.Effect<void, never>;
  /** Identify a user across both platforms */
  identify(params: IdentifyParams): Effect.Effect<void, never>;
}

/**
 * Analytics service.
 *
 * Aggregates Google Analytics and PostHog, providing a unified interface for
 * tracking analytics events. All methods call both providers in parallel.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const analytics = yield* Analytics;
 *
 *   yield* analytics.initialize();
 *   yield* analytics.trackEvent({
 *     name: "purchase",
 *     properties: { currency: "USD", value: 50 }
 *   });
 * });
 *
 * program.pipe(
 *   Effect.provide(Analytics.Live({
 *     googleAnalytics: { measurementId: "G-XXXXXXXXXX" },
 *     postHog: { apiKey: "phc_..." }
 *   }))
 * );
 * ```
 */
export class Analytics extends Context.Tag("Analytics")<
  Analytics,
  AnalyticsService
>() {
  /**
   * Default layer that creates the Analytics service.
   *
   * Requires GoogleAnalytics and PostHog to be provided. This layer composes
   * the two analytics providers and provides a unified interface.
   */
  static Default = Layer.effect(
    Analytics,
    Effect.gen(function* () {
      const googleAnalytics = yield* GoogleAnalytics;
      const postHog = yield* PostHog;

      return {
        googleAnalytics,
        postHog,

        initialize: () =>
          Effect.all([googleAnalytics.initialize(), postHog.initialize()], {
            concurrency: "unbounded",
          }).pipe(Effect.map(() => undefined)),

        trackEvent: (params: TrackEventParams) =>
          Effect.all(
            [
              googleAnalytics.trackEvent({
                eventName: params.name,
                eventParams: params.properties,
              }),
              postHog.trackEvent({
                event: params.name,
                properties: params.properties,
              }),
            ],
            { concurrency: "unbounded" },
          ).pipe(Effect.map(() => undefined)),

        trackPageView: (params?: TrackPageViewParams) =>
          Effect.all(
            [
              googleAnalytics.trackPageView({
                pagePath: params?.path,
                pageTitle: params?.title,
              }),
              postHog.trackPageView(),
            ],
            { concurrency: "unbounded" },
          ).pipe(Effect.map(() => undefined)),

        identify: (params: IdentifyParams) =>
          Effect.all(
            [
              googleAnalytics.setUserId(params.userId),
              postHog.identify({
                distinctId: params.userId,
                properties: params.properties,
              }),
            ],
            { concurrency: "unbounded" },
          ).pipe(Effect.map(() => undefined)),
      };
    }),
  );

  /**
   * Creates a fully configured Analytics layer.
   *
   * Automatically creates and provides both GoogleAnalytics and PostHog layers
   * based on the provided configuration. Falls back to no-op implementations
   * if configuration is invalid.
   *
   * @param config - Analytics configuration for both providers
   * @returns A Layer providing Analytics
   *
   * @example
   * ```ts
   * const AnalyticsLive = Analytics.Live({
   *   googleAnalytics: {
   *     measurementId: process.env.GOOGLE_ANALYTICS_MEASUREMENT_ID,
   *     apiSecret: process.env.GOOGLE_ANALYTICS_API_SECRET,
   *   },
   *   postHog: {
   *     apiKey: process.env.POSTHOG_API_KEY,
   *     host: process.env.POSTHOG_HOST,
   *   },
   * });
   *
   * program.pipe(Effect.provide(AnalyticsLive));
   * ```
   */
  static Live = (config: AnalyticsConfig) => {
    const googleAnalyticsLayer = GoogleAnalytics.layer(config.googleAnalytics);
    const postHogLayer = PostHog.layer(config.postHog);

    return Analytics.Default.pipe(
      Layer.provide(Layer.merge(googleAnalyticsLayer, postHogLayer)),
    );
  };
}
