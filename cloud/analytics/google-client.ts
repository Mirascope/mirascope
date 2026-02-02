/**
 * @fileoverview Effect-native Google Analytics service.
 *
 * This module provides the `GoogleAnalytics` service which supports both client-side
 * (browser) and server-side (Cloudflare Workers) tracking through automatic environment
 * detection.
 *
 * ## Architecture
 *
 * ```
 * GoogleAnalytics (Effect Context.Tag)
 *   ├── Client implementation (browser gtag.js)
 *   │   └── Script injection + window.gtag() calls
 *   └── Server implementation (GA4 Measurement Protocol)
 *       └── HTTP POST to Google Analytics API
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { GoogleAnalytics } from "@/analytics/google-client";
 *
 * const trackPageView = Effect.gen(function* () {
 *   const ga = yield* GoogleAnalytics;
 *
 *   yield* ga.initialize();
 *   yield* ga.trackPageView({ pagePath: "/dashboard", pageTitle: "Dashboard" });
 * });
 * ```
 *
 * ## Error Handling
 *
 * All operations return `Effect<void, never>` - errors are caught internally and
 * logged to console.error. Analytics failures never break the application.
 */

import { Effect, Layer, Context } from "effect";

import type { GoogleAnalyticsConfig } from "@/settings";

import {
  toGA4Properties,
  type BrowserContext,
} from "@/app/lib/browser-context";

/**
 * Parameters for tracking events.
 */
export interface TrackEventParams {
  /** Name of the event (e.g., "sign_up", "purchase") */
  eventName: string;
  /** Event parameters (e.g., { category: "user", value: 100 }) */
  eventParams?: Record<string, unknown>;
  /** Browser context for rich analytics data */
  browserContext?: BrowserContext;
}

/**
 * Parameters for tracking page views.
 */
export interface TrackPageViewParams {
  /** Page title */
  pageTitle?: string;
  /** Page path (e.g., "/dashboard") */
  pagePath?: string;
  /** Full page URL */
  pageLocation?: string;
  /** Browser context for rich analytics data */
  browserContext?: BrowserContext;
}

/**
 * Shared interface for both client and server implementations.
 */
export interface GoogleAnalyticsClient {
  /** Environment type indicator */
  readonly type: "client" | "server" | "noop";
  /** Initialize the analytics service (load scripts, prepare HTTP client) */
  initialize(): Effect.Effect<void, never>;
  /** Track a custom event */
  trackEvent(params: TrackEventParams): Effect.Effect<void, never>;
  /** Track a page view */
  trackPageView(params: TrackPageViewParams): Effect.Effect<void, never>;
  /** Set the user ID for tracking */
  setUserId(userId: string | null): Effect.Effect<void, never>;
}

/**
 * Creates a client-side (browser) implementation using gtag.js.
 */
function createClientImplementation(
  config: GoogleAnalyticsConfig,
): GoogleAnalyticsClient {
  let initialized = false;
  let initializePromise: Promise<void> | null = null;
  let currentUserId: string | null = null;

  // Declare global gtag function type
  type GtagFunction = (
    command: string,
    targetOrAction: string | Date,
    params?: Record<string, unknown>,
  ) => void;

  const loadScript = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      // Initialize dataLayer and gtag (window is guaranteed to exist in client implementation)
      window.dataLayer = window.dataLayer || [];
      window.gtag =
        window.gtag ||
        (function gtag(...args: unknown[]) {
          window.dataLayer.push(args);
        } as GtagFunction);
      window.gtag("js", new Date());
      window.gtag("config", config.measurementId, {
        send_page_view: false, // We'll manually trigger page views
      });

      // Check if script is already loaded
      const existingScript = document.querySelector(
        `script[src*="googletagmanager.com/gtag/js"]`,
      );
      if (existingScript) {
        resolve();
        return;
      }

      // Create and inject script
      const script = document.createElement("script");
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${config.measurementId}`;

      script.onload = () => resolve();
      script.onerror = () =>
        reject(new Error("Failed to load Google Analytics script"));

      document.head.appendChild(script);
    });
  };

  /**
   * Idempotent initialization helper.
   * - Returns immediately if already initialized
   * - Returns existing promise if initialization is in progress
   * - Creates new promise if not yet started
   */
  const ensureInitialized = async (): Promise<void> => {
    if (initialized) {
      return;
    }
    if (initializePromise) {
      return initializePromise;
    }
    initializePromise = loadScript()
      .then(() => {
        initialized = true;
      })
      .catch((error) => {
        initializePromise = null; // Reset to allow retry
        throw error;
      });
    return initializePromise;
  };

  return {
    type: "client",

    initialize: () =>
      Effect.tryPromise({
        try: () => ensureInitialized(),
        catch: (error) => {
          console.error("Google Analytics initialization failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    trackEvent: (params) =>
      Effect.tryPromise({
        try: async () => {
          await ensureInitialized();
          // window and gtag are guaranteed to exist in client implementation after init
          window.gtag("event", params.eventName, {
            ...params.eventParams,
            send_to: config.measurementId,
          });
        },
        catch: (error) => {
          console.error("Google Analytics trackEvent failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    trackPageView: (params) =>
      Effect.tryPromise({
        try: async () => {
          await ensureInitialized();
          // window and gtag are guaranteed to exist in client implementation after init
          window.gtag("config", config.measurementId, {
            page_title: params.pageTitle,
            page_path: params.pagePath,
            page_location: params.pageLocation || window.location.href,
            ...(currentUserId && { user_id: currentUserId }),
          });
        },
        catch: (error) => {
          console.error("Google Analytics trackPageView failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    setUserId: (userId) =>
      Effect.tryPromise({
        try: async () => {
          currentUserId = userId;
          if (userId) {
            await ensureInitialized();
            // window and gtag are guaranteed to exist in client implementation after init
            window.gtag("config", config.measurementId, {
              user_id: userId,
            });
          }
        },
        catch: (error) => {
          console.error("Google Analytics setUserId failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),
  };
}

/**
 * Creates a server-side implementation using GA4 Measurement Protocol.
 */
function createServerImplementation(
  config: GoogleAnalyticsConfig,
): GoogleAnalyticsClient {
  let currentUserId: string | null = null;

  const sendEvent = async (eventData: {
    name: string;
    params?: Record<string, unknown>;
    browserContext?: BrowserContext;
  }): Promise<void> => {
    const url = `https://www.google-analytics.com/mp/collect?measurement_id=${config.measurementId}&api_secret=${config.apiSecret}`;

    // Transform browser context to GA4 format
    const ga4Context = eventData.browserContext
      ? toGA4Properties(eventData.browserContext)
      : {};

    // Use anonymousId from browserContext, fallback to timestamp-based ID
    const clientId =
      eventData.browserContext?.anonymousId || "server_" + Date.now();

    const payload = {
      client_id: clientId,
      ...(currentUserId && { user_id: currentUserId }),
      events: [
        {
          name: eventData.name,
          params: {
            ...ga4Context, // Browser context (page_location, screen_resolution, etc.)
            ...eventData.params, // Event-specific params override
            engagement_time_msec: 100, // Required for engagement metrics
          },
        },
      ],
    };

    const response = await fetch(url, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new Error(
        `GA4 Measurement Protocol failed: ${response.status} ${response.statusText}`,
      );
    }
  };

  return {
    type: "server",

    initialize: () => Effect.succeed(void 0), // No initialization needed for server

    trackEvent: (params) =>
      Effect.tryPromise({
        try: () =>
          sendEvent({
            name: params.eventName,
            params: params.eventParams,
            browserContext: params.browserContext,
          }),
        catch: (error) => {
          console.error("Google Analytics server trackEvent failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    trackPageView: (params) =>
      Effect.tryPromise({
        try: () =>
          sendEvent({
            name: "page_view",
            params: {
              page_title: params.pageTitle,
              page_location: params.pageLocation || params.pagePath,
              page_path: params.pagePath,
            },
            browserContext: params.browserContext,
          }),
        catch: (error) => {
          console.error("Google Analytics server trackPageView failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    setUserId: (userId) =>
      Effect.sync(() => {
        currentUserId = userId;
      }),
  };
}

/**
 * Extend Window interface for gtag support.
 */
declare global {
  interface Window {
    dataLayer: unknown[];
    gtag: (
      command: string,
      targetOrAction: string | Date,
      params?: Record<string, unknown>,
    ) => void;
  }
}

/**
 * Effect-native Google Analytics service.
 *
 * Automatically detects environment (client/server) and provides the appropriate
 * implementation. Configuration errors result in a no-op implementation to ensure
 * analytics never breaks the application.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const ga = yield* GoogleAnalytics;
 *
 *   yield* ga.initialize();
 *   yield* ga.trackEvent({ eventName: "sign_up", eventParams: { method: "email" } });
 * });
 *
 * program.pipe(
 *   Effect.provide(GoogleAnalytics.layer({ measurementId: "G-XXXXXXXXXX" }))
 * );
 * ```
 */
export class GoogleAnalytics extends Context.Tag("GoogleAnalytics")<
  GoogleAnalytics,
  GoogleAnalyticsClient
>() {
  /**
   * Creates a Layer that provides the GoogleAnalytics service.
   *
   * Automatically detects the environment and provides client-side or server-side
   * implementation.
   *
   * Note: Config validation is handled by Settings at startup. The config
   * passed here is guaranteed to be complete and valid.
   *
   * @param config - Validated Google Analytics configuration from Settings
   * @returns A Layer providing GoogleAnalytics
   *
   * @example
   * ```ts
   * // Settings provides validated config
   * const settings = yield* Settings;
   * const GALive = GoogleAnalytics.layer(settings.googleAnalytics);
   *
   * program.pipe(Effect.provide(GALive));
   * ```
   */
  static layer = (config: GoogleAnalyticsConfig) => {
    // Environment detection
    const isBrowser = typeof window !== "undefined";

    const implementation = isBrowser
      ? createClientImplementation(config)
      : createServerImplementation(config);

    return Layer.succeed(GoogleAnalytics, implementation);
  };
}
