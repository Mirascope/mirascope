/**
 * @fileoverview Effect-native PostHog service.
 *
 * This module provides the `PostHog` service which supports both client-side
 * (browser) and server-side (Cloudflare Workers) tracking through automatic environment
 * detection.
 *
 * ## Architecture
 *
 * ```
 * PostHog (Effect Context.Tag)
 *   ├── Client implementation (browser posthog-js)
 *   │   └── Script injection + window.posthog calls
 *   └── Server implementation (PostHog HTTP API)
 *       └── HTTP POST to PostHog events API
 * ```
 *
 * ## Usage
 *
 * ```ts
 * import { PostHog } from "@/analytics/posthog-client";
 *
 * const trackEvent = Effect.gen(function* () {
 *   const ph = yield* PostHog;
 *
 *   yield* ph.initialize();
 *   yield* ph.trackEvent({ event: "sign_up", properties: { method: "email" } });
 * });
 * ```
 *
 * ## Error Handling
 *
 * All operations return `Effect<void, never>` - errors are caught internally and
 * logged to console.error. Analytics failures never break the application.
 */

import { Effect, Layer, Context } from "effect";
import type { PostHogConfig } from "@/settings";

/**
 * Parameters for tracking events.
 */
export interface TrackEventParams {
  /** Name of the event (e.g., "sign_up", "purchase") */
  event: string;
  /** Optional distinct ID (user identifier) */
  distinctId?: string;
  /** Event properties */
  properties?: Record<string, unknown>;
}

/**
 * Parameters for tracking page views.
 */
export interface TrackPageViewParams {
  /** Optional distinct ID (user identifier) */
  distinctId?: string;
  /** Optional properties to include with page view */
  properties?: Record<string, unknown>;
}

/**
 * Parameters for identifying users.
 */
export interface IdentifyParams {
  /** User identifier */
  distinctId: string;
  /** User properties */
  properties?: Record<string, unknown>;
}

/**
 * Shared interface for both client and server implementations.
 */
export interface PostHogClient {
  /** Environment type indicator */
  readonly type: "client" | "server" | "noop";
  /** Initialize the analytics service (load scripts, prepare HTTP client) */
  initialize(): Effect.Effect<void, never>;
  /** Track a custom event */
  trackEvent(params: TrackEventParams): Effect.Effect<void, never>;
  /** Track a page view */
  trackPageView(params?: TrackPageViewParams): Effect.Effect<void, never>;
  /** Identify a user */
  identify(params: IdentifyParams): Effect.Effect<void, never>;
}

/**
 * Creates a client-side (browser) implementation using posthog-js.
 */
function createClientImplementation(config: PostHogConfig): PostHogClient {
  let initialized = false;
  let initializePromise: Promise<void> | null = null;

  const loadScript = (): Promise<void> => {
    return new Promise((resolve, reject) => {
      // Check if PostHog is already loaded
      if (typeof window !== "undefined" && window.posthog) {
        // Initialize if already loaded
        window.posthog.init(config.apiKey, {
          api_host: config.host,
          capture_pageview: false, // We'll manually trigger page views
          capture_pageleave: true,
          autocapture: true,
          person_profiles: "identified_only",
        });
        resolve();
        return;
      }

      // Check if script is already being loaded
      const existingScript = document.querySelector('script[src*="posthog"]');
      if (existingScript) {
        // Check if already loaded
        if (window.posthog) {
          window.posthog.init(config.apiKey, {
            api_host: config.host,
            capture_pageview: false,
            capture_pageleave: true,
            autocapture: true,
            person_profiles: "identified_only",
          });
          resolve();
          return;
        }
        // Wait for it to load if not yet loaded
        existingScript.addEventListener("load", () => {
          // posthog is guaranteed to exist after script loads
          window.posthog!.init(config.apiKey, {
            api_host: config.host,
            capture_pageview: false,
            capture_pageleave: true,
            autocapture: true,
            person_profiles: "identified_only",
          });
          resolve();
        });
        return;
      }

      // Create and inject script
      const script = document.createElement("script");
      script.async = true;
      script.src = "https://cdn.posthog.com/array.js";

      script.onload = () => {
        // Initialize PostHog after script loads
        if (window.posthog) {
          window.posthog.init(config.apiKey, {
            api_host: config.host,
            capture_pageview: false,
            capture_pageleave: true,
            autocapture: true,
            person_profiles: "identified_only",
          });
          resolve();
        } else {
          reject(new Error("PostHog script loaded but posthog not available"));
        }
      };

      script.onerror = () => reject(new Error("Failed to load PostHog script"));

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
          console.error("PostHog initialization failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    trackEvent: (params) =>
      Effect.tryPromise({
        try: async () => {
          await ensureInitialized();
          // posthog is guaranteed to exist in client implementation after init
          window.posthog!.capture(params.event, {
            ...params.properties,
            ...(params.distinctId && { distinct_id: params.distinctId }),
          });
        },
        catch: (error) => {
          console.error("PostHog trackEvent failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    trackPageView: (params) =>
      Effect.tryPromise({
        try: async () => {
          await ensureInitialized();
          // posthog is guaranteed to exist in client implementation after init
          window.posthog!.capture("$pageview", {
            ...params?.properties,
            ...(params?.distinctId && { distinct_id: params.distinctId }),
          });
        },
        catch: (error) => {
          console.error("PostHog trackPageView failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    identify: (params) =>
      Effect.tryPromise({
        try: async () => {
          await ensureInitialized();
          // posthog is guaranteed to exist in client implementation after init
          window.posthog!.identify(params.distinctId, params.properties);
        },
        catch: (error) => {
          console.error("PostHog identify failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),
  };
}

/**
 * Creates a server-side implementation using PostHog HTTP API.
 */
function createServerImplementation(config: PostHogConfig): PostHogClient {
  const sendEvent = async (eventData: {
    event: string;
    distinct_id?: string;
    properties?: Record<string, unknown>;
  }): Promise<void> => {
    const url = `${config.host}/capture/`;

    const payload = {
      api_key: config.apiKey,
      event: eventData.event,
      distinct_id: eventData.distinct_id || "anonymous",
      properties: eventData.properties || {},
      timestamp: new Date().toISOString(),
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
        `PostHog API failed: ${response.status} ${response.statusText}`,
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
            event: params.event,
            distinct_id: params.distinctId,
            properties: params.properties,
          }),
        catch: (error) => {
          console.error("PostHog server trackEvent failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    trackPageView: (params) =>
      Effect.tryPromise({
        try: () =>
          sendEvent({
            event: "$pageview",
            distinct_id: params?.distinctId,
            properties: params?.properties,
          }),
        catch: (error) => {
          console.error("PostHog server trackPageView failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),

    identify: (params) =>
      Effect.tryPromise({
        try: async () => {
          const url = `${config.host}/capture/`;

          const payload = {
            api_key: config.apiKey,
            event: "$identify",
            distinct_id: params.distinctId,
            properties: {
              $set: params.properties || {},
            },
            timestamp: new Date().toISOString(),
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
              `PostHog identify failed: ${response.status} ${response.statusText}`,
            );
          }
        },
        catch: (error) => {
          console.error("PostHog server identify failed:", error);
          return error;
        },
      }).pipe(Effect.catchAll(() => Effect.succeed(void 0))),
  };
}
/**
 * Extend Window interface for PostHog support.
 */
declare global {
  interface Window {
    posthog?: {
      init: (apiKey: string, options: Record<string, unknown>) => void;
      capture: (event: string, properties?: Record<string, unknown>) => void;
      identify: (
        distinctId: string,
        properties?: Record<string, unknown>,
      ) => void;
    };
  }
}

/**
 * Effect-native PostHog service.
 *
 * Automatically detects environment (client/server) and provides the appropriate
 * implementation. Configuration errors result in a no-op implementation to ensure
 * analytics never breaks the application.
 *
 * @example
 * ```ts
 * const program = Effect.gen(function* () {
 *   const ph = yield* PostHog;
 *
 *   yield* ph.initialize();
 *   yield* ph.trackEvent({ event: "sign_up", properties: { method: "email" } });
 * });
 *
 * program.pipe(
 *   Effect.provide(PostHog.layer({ apiKey: "phc_..." }))
 * );
 * ```
 */
export class PostHog extends Context.Tag("PostHog")<PostHog, PostHogClient>() {
  /**
   * Creates a Layer that provides the PostHog service.
   *
   * Automatically detects the environment and provides client-side or server-side
   * implementation.
   *
   * Note: Config validation is handled by Settings at startup. The config
   * passed here is guaranteed to be complete and valid.
   *
   * @param config - Validated PostHog configuration from Settings
   * @returns A Layer providing PostHog
   *
   * @example
   * ```ts
   * // Settings provides validated config
   * const settings = yield* Settings;
   * const PostHogLive = PostHog.layer(settings.posthog);
   *
   * program.pipe(Effect.provide(PostHogLive));
   * ```
   */
  static layer = (config: PostHogConfig) => {
    // Environment detection
    const isBrowser = typeof window !== "undefined";

    const implementation = isBrowser
      ? createClientImplementation(config)
      : createServerImplementation(config);

    return Layer.succeed(PostHog, implementation);
  };
}
