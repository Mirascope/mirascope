/**
 * @fileoverview Tests for Analytics aggregator service.
 */

import { describe, it, expect } from "@effect/vitest";
import { Effect, Layer } from "effect";
import { vi } from "vitest";

import { GoogleAnalytics } from "@/analytics/google-client";
import { PostHog } from "@/analytics/posthog-client";
import { Analytics } from "@/analytics/service";
import { MockGoogleAnalytics, MockPostHog } from "@/tests/analytics";

describe("Analytics", () => {
  describe("service composition", () => {
    it("creates service with both providers", async () => {
      const layer = Analytics.Live({
        googleAnalytics: {
          measurementId: "G-TEST123",
          apiSecret: "test_secret",
        },
        postHog: { apiKey: "phc_test123", host: "https://us.i.posthog.com" },
      });

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;

        // Verify both providers are accessible
        expect(analytics.googleAnalytics).toBeDefined();
        expect(analytics.postHog).toBeDefined();
        expect(analytics.googleAnalytics.type).toBeDefined();
        expect(analytics.postHog.type).toBeDefined();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("provides direct access to GoogleAnalytics client", async () => {
      const layer = Analytics.Live({
        googleAnalytics: {
          measurementId: "G-TEST123",
          apiSecret: "test_secret",
        },
        postHog: { apiKey: "phc_test123", host: "https://us.i.posthog.com" },
      });

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;

        // Can access GoogleAnalytics client directly
        // In test environment (no window), GA will create server implementation
        expect(analytics.googleAnalytics.type).toBe("server");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("provides direct access to PostHog client", async () => {
      const layer = Analytics.Live({
        googleAnalytics: {
          measurementId: "G-TEST123",
          apiSecret: "test_secret",
        },
        postHog: { apiKey: "phc_test123", host: "https://us.i.posthog.com" },
      });

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;

        // Can access PostHog client directly
        expect(analytics.postHog.type).toBe("server"); // Server environment
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });
  });

  describe("initialize", () => {
    it("calls initialize on both providers", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.initialize();

        // Verify both providers were initialized
        expect(mockGA.initialize).toHaveBeenCalledTimes(1);
        expect(mockPH.initialize).toHaveBeenCalledTimes(1);
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });

    it("catches and logs errors from providers", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      // Make one provider fail
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      mockGA.initialize = vi.fn(() =>
        Effect.fail(new Error("GA init failed")),
      ) as any; // eslint-disable-line @typescript-eslint/no-explicit-any

      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.initialize();

        // Should still succeed (errors caught internally)
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          "Analytics initialize failed:",
          expect.any(Error),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
      consoleErrorSpy.mockRestore();
    });
  });

  describe("trackEvent", () => {
    it("calls trackEvent on both providers with correct parameters", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.trackEvent({
          name: "sign_up",
          properties: { method: "email" },
        });

        // Verify GA was called with correct parameters
        expect(mockGA.trackEvent).toHaveBeenCalledTimes(1);
        expect(mockGA.trackEvent).toHaveBeenCalledWith({
          eventName: "sign_up",
          eventParams: { method: "email" },
        });

        // Verify PostHog was called with correct parameters
        expect(mockPH.trackEvent).toHaveBeenCalledTimes(1);
        expect(mockPH.trackEvent).toHaveBeenCalledWith({
          event: "sign_up",
          properties: { method: "email" },
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });

    it("tracks events without properties", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.trackEvent({ name: "page_view" });

        expect(mockGA.trackEvent).toHaveBeenCalledWith({
          eventName: "page_view",
          eventParams: undefined,
        });
        expect(mockPH.trackEvent).toHaveBeenCalledWith({
          event: "page_view",
          properties: undefined,
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });

    it("catches and logs errors from providers", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      // Make one provider fail
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      mockPH.trackEvent = vi.fn(() =>
        Effect.fail(new Error("PH failed")),
      ) as any; // eslint-disable-line @typescript-eslint/no-explicit-any

      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.trackEvent({ name: "test_event" });

        // Should still succeed (errors caught internally)
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          "Analytics trackEvent failed:",
          expect.any(Error),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
      consoleErrorSpy.mockRestore();
    });
  });

  describe("trackPageView", () => {
    it("calls trackPageView on both providers", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.trackPageView({
          path: "/dashboard",
          title: "Dashboard",
        });

        // Verify GA was called with correct parameters
        expect(mockGA.trackPageView).toHaveBeenCalledTimes(1);
        expect(mockGA.trackPageView).toHaveBeenCalledWith({
          pagePath: "/dashboard",
          pageTitle: "Dashboard",
        });

        // Verify PostHog was called
        expect(mockPH.trackPageView).toHaveBeenCalledTimes(1);
        expect(mockPH.trackPageView).toHaveBeenCalledWith({
          distinctId: undefined,
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });

    it("tracks page views without parameters", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.trackPageView();

        expect(mockGA.trackPageView).toHaveBeenCalledWith({
          pagePath: undefined,
          pageTitle: undefined,
        });
        expect(mockPH.trackPageView).toHaveBeenCalledWith({
          distinctId: undefined,
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });

    it("catches and logs errors from providers", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      // Make one provider fail
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      mockGA.trackPageView = vi.fn(() =>
        Effect.fail(new Error("GA failed")),
      ) as any; // eslint-disable-line @typescript-eslint/no-explicit-any

      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.trackPageView();

        // Should still succeed (errors caught internally)
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          "Analytics trackPageView failed:",
          expect.any(Error),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
      consoleErrorSpy.mockRestore();
    });
  });

  describe("identify", () => {
    it("calls identify/setUserId on both providers", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.identify({
          userId: "user_123",
          properties: { email: "user@example.com" },
        });

        // Verify GA setUserId was called
        expect(mockGA.setUserId).toHaveBeenCalledTimes(1);
        expect(mockGA.setUserId).toHaveBeenCalledWith("user_123");

        // Verify PostHog identify was called
        expect(mockPH.identify).toHaveBeenCalledTimes(1);
        expect(mockPH.identify).toHaveBeenCalledWith({
          distinctId: "user_123",
          properties: { email: "user@example.com" },
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });

    it("identifies users without properties", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.identify({ userId: "user_123" });

        expect(mockGA.setUserId).toHaveBeenCalledWith("user_123");
        expect(mockPH.identify).toHaveBeenCalledWith({
          distinctId: "user_123",
          properties: undefined,
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });

    it("catches and logs errors from providers", async () => {
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      // Make one provider fail
      // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
      mockGA.setUserId = vi.fn(() =>
        Effect.fail(new Error("GA failed")),
      ) as any; // eslint-disable-line @typescript-eslint/no-explicit-any

      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;
        yield* analytics.identify({ userId: "user_123" });

        // Should still succeed (errors caught internally)
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          "Analytics identify failed:",
          expect.any(Error),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
      consoleErrorSpy.mockRestore();
    });
  });

  describe("error isolation", () => {
    it("both providers are called independently", async () => {
      // Note: Real providers catch errors internally and return Effect<void, never>
      // This test verifies that both providers are called in parallel
      const mockGA = MockGoogleAnalytics();
      const mockPH = MockPostHog();
      const analyticsLayer = Analytics.Default.pipe(
        Layer.provide(
          Layer.merge(
            Layer.succeed(GoogleAnalytics, mockGA),
            Layer.succeed(PostHog, mockPH),
          ),
        ),
      );

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;

        // Track event - both providers should be called
        yield* analytics.trackEvent({
          name: "test_event",
          properties: { test: true },
        });

        // Both providers should have been called
        expect(mockGA.trackEvent).toHaveBeenCalledTimes(1);
        expect(mockPH.trackEvent).toHaveBeenCalledTimes(1);

        // Track another type of event to verify independence
        yield* analytics.trackPageView({ path: "/test" });
        expect(mockGA.trackPageView).toHaveBeenCalledTimes(1);
        expect(mockPH.trackPageView).toHaveBeenCalledTimes(1);
      });

      await Effect.runPromise(program.pipe(Effect.provide(analyticsLayer)));
    });
  });

  describe("Analytics.Live", () => {
    it("creates complete layer with both providers", async () => {
      const layer = Analytics.Live({
        googleAnalytics: {
          measurementId: "G-TEST123",
          apiSecret: "test_secret",
        },
        postHog: { apiKey: "phc_test123", host: "https://us.i.posthog.com" },
      });

      const program = Effect.gen(function* () {
        const analytics = yield* Analytics;

        // Verify service is created
        expect(analytics).toBeDefined();
        expect(analytics.googleAnalytics).toBeDefined();
        expect(analytics.postHog).toBeDefined();

        // Verify methods are available
        expect(typeof analytics.initialize).toBe("function");
        expect(typeof analytics.trackEvent).toBe("function");
        expect(typeof analytics.trackPageView).toBe("function");
        expect(typeof analytics.identify).toBe("function");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });
  });
});
