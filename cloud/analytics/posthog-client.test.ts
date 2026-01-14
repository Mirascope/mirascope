/**
 * @fileoverview Tests for PostHog Effect-native service.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { Effect } from "effect";
import { PostHog } from "@/analytics/posthog-client";

describe("PostHog", () => {
  describe("client environment (browser)", () => {
    let mockScript: { onload?: () => void; onerror?: () => void };
    let mockPostHog: {
      init: ReturnType<typeof vi.fn>;
      capture: ReturnType<typeof vi.fn>;
      identify: ReturnType<typeof vi.fn>;
    };

    beforeEach(() => {
      // Reset all mocks
      vi.clearAllMocks();

      // Create mock script element
      mockScript = {};

      // Mock PostHog
      mockPostHog = {
        init: vi.fn(),
        capture: vi.fn(),
        identify: vi.fn(),
      };

      // Mock document
      const mockDocument = {
        createElement: vi.fn((tag: string) => {
          if (tag === "script") return mockScript;
          return {};
        }),
        querySelector: vi.fn(() => null), // No existing script
        head: {
          appendChild: vi.fn((node) => {
            // Simulate successful script load
            if (node === mockScript && mockScript.onload) {
              // Set posthog before calling onload
              window.posthog = mockPostHog as unknown as typeof window.posthog;
              setTimeout(() => mockScript.onload?.(), 0);
            }
          }),
        },
      };

      // Mock window (no posthog initially)
      vi.stubGlobal("window", {});
      vi.stubGlobal("document", mockDocument);
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("creates client implementation in browser environment", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        expect(ph.type).toBe("client");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("loads PostHog script on initialization", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        // Verify script was created and appended
        // eslint-disable-next-line @typescript-eslint/unbound-method
        expect(document.createElement).toHaveBeenCalledWith("script");
        // eslint-disable-next-line @typescript-eslint/unbound-method
        expect(document.head.appendChild).toHaveBeenCalled();

        // Verify script properties
        expect(mockScript).toMatchObject({
          async: true,
          src: "https://cdn.posthog.com/array.js",
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("initializes PostHog with correct options", async () => {
      const layer = PostHog.layer({
        apiKey: "phc_test123",
        host: "https://custom.posthog.com",
      });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        // Verify posthog.init was called with correct parameters
        expect(mockPostHog.init).toHaveBeenCalledWith("phc_test123", {
          api_host: "https://custom.posthog.com",
          capture_pageview: false,
          capture_pageleave: true,
          autocapture: true,
          person_profiles: "identified_only",
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("uses default host when not specified", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        expect(mockPostHog.init).toHaveBeenCalledWith(
          "phc_test123",
          expect.objectContaining({
            api_host: "https://us.i.posthog.com",
          }),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("only initializes once (caches initialization promise)", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Call initialize multiple times
        yield* ph.initialize();
        yield* ph.initialize();
        yield* ph.initialize();

        // Script should only be created once
        // eslint-disable-next-line @typescript-eslint/unbound-method
        expect(document.createElement).toHaveBeenCalledTimes(1);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("skips script injection if PostHog already loaded", async () => {
      // Pre-load PostHog
      vi.stubGlobal("window", { posthog: mockPostHog });

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        // Should initialize existing PostHog, not create new script
        expect(mockPostHog.init).toHaveBeenCalled();
        // eslint-disable-next-line @typescript-eslint/unbound-method
        expect(document.createElement).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("waits for existing script to load", async () => {
      const existingScript = {
        addEventListener: vi.fn((event: string, handler: () => void) => {
          if (event === "load") {
            // Simulate script load
            window.posthog = mockPostHog as unknown as typeof window.posthog;
            setTimeout(() => handler(), 0);
          }
        }),
      };

      const mockDocument = {
        createElement: vi.fn(),
        querySelector: vi.fn(() => existingScript),
        head: { appendChild: vi.fn() },
      };

      vi.stubGlobal("document", mockDocument);

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        // Should wait for existing script
        expect(existingScript.addEventListener).toHaveBeenCalledWith(
          "load",
          expect.any(Function),
        );
        // Should not create new script
        expect(mockDocument.createElement).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("handles existing script that already finished loading", async () => {
      const existingScript = {
        addEventListener: vi.fn(),
      };

      const mockDocument = {
        createElement: vi.fn(),
        querySelector: vi.fn(() => existingScript),
        head: { appendChild: vi.fn() },
      };

      // Setup: window.posthog doesn't exist initially, but script tag exists
      // Then posthog becomes available (race condition - script finished loading between checks)
      const mockWindow: { posthog?: typeof mockPostHog } = {};
      vi.stubGlobal("window", mockWindow);
      vi.stubGlobal("document", mockDocument);

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Set up posthog to exist when querySelector is called
        // This simulates the race condition where the script loads between
        // the first check and the querySelector call
        mockDocument.querySelector = vi.fn(() => {
          // By the time we find the existing script, posthog has loaded
          mockWindow.posthog = mockPostHog as typeof mockWindow.posthog;
          return existingScript;
        });

        yield* ph.initialize();

        // Should initialize existing PostHog immediately
        expect(mockPostHog.init).toHaveBeenCalledWith("phc_test123", {
          api_host: "https://us.i.posthog.com",
          capture_pageview: false,
          capture_pageleave: true,
          autocapture: true,
          person_profiles: "identified_only",
        });
        // Should NOT add event listener since already loaded
        expect(existingScript.addEventListener).not.toHaveBeenCalled();
        // Should not create new script
        expect(mockDocument.createElement).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("handles concurrent initialization calls", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Run initialize calls concurrently using Effect.all
        yield* Effect.all([ph.initialize(), ph.initialize(), ph.initialize()], {
          concurrency: "unbounded",
        });

        // Script should only be created once even with concurrent calls
        // eslint-disable-next-line @typescript-eslint/unbound-method
        expect(document.createElement).toHaveBeenCalledTimes(1);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("returns existing promise when initialization is in progress", async () => {
      let resolveScript: (() => void) | undefined;

      // Mock document with delayed script loading
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null),
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript) {
              // Don't call onload immediately - store it for manual control
              // This keeps initialization in progress
            }
          }),
        },
      };
      vi.stubGlobal("document", mockDocument);

      // Override mockScript to capture the onload callback
      mockScript.onload = undefined;
      Object.defineProperty(mockScript, "onload", {
        set: (fn: () => void) => {
          resolveScript = () => {
            window.posthog = mockPostHog as unknown as typeof window.posthog;
            fn();
          };
        },
        configurable: true,
      });

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Start multiple operations concurrently (they will all call ensureInitialized)
        const promise1 = Effect.runPromise(ph.trackEvent({ event: "event1" }));
        const promise2 = Effect.runPromise(
          ph.trackPageView({ properties: {} }),
        );
        const promise3 = Effect.runPromise(
          ph.identify({ distinctId: "user1" }),
        );

        // All three should be waiting on the same initialization promise
        // Script should only be created once even with concurrent calls
        expect(mockDocument.createElement).toHaveBeenCalledTimes(1);

        // Now resolve the script loading
        if (resolveScript) {
          resolveScript();
        }

        // Wait for all operations to complete
        yield* Effect.promise(() =>
          Promise.all([promise1, promise2, promise3]),
        );

        // Verify still only one script creation
        expect(mockDocument.createElement).toHaveBeenCalledTimes(1);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("allows retry after failed initialization", async () => {
      let shouldFail = true;

      // Mock document with conditional success/failure
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null),
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript) {
              if (shouldFail && mockScript.onerror) {
                setTimeout(() => mockScript.onerror?.(), 0);
              } else if (!shouldFail && mockScript.onload) {
                window.posthog =
                  mockPostHog as unknown as typeof window.posthog;
                setTimeout(() => mockScript.onload?.(), 0);
              }
            }
          }),
        },
      };
      vi.stubGlobal("document", mockDocument);

      const layer = PostHog.layer({ apiKey: "phc_test123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // First attempt should fail
        yield* ph.initialize();
        expect(consoleErrorSpy).toHaveBeenCalled();

        // Verify script creation was attempted
        expect(mockDocument.createElement).toHaveBeenCalledTimes(1);

        consoleErrorSpy.mockClear();

        // Allow script to succeed on retry
        shouldFail = false;

        // Second attempt should succeed (retry after failure)
        yield* ph.trackEvent({ event: "test_retry" });

        // Verify script creation was attempted again (retry)
        expect(mockDocument.createElement).toHaveBeenCalledTimes(2);

        // Third attempt should use cached successful initialization
        yield* ph.trackPageView();

        // Script should not be created again (already initialized)
        expect(mockDocument.createElement).toHaveBeenCalledTimes(2);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("auto-initializes when calling trackEvent without explicit initialize", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Call trackEvent WITHOUT calling initialize first
        yield* ph.trackEvent({ event: "test_event" });

        // Script should have been created automatically
        // eslint-disable-next-line @typescript-eslint/unbound-method
        expect(document.createElement).toHaveBeenCalledWith("script");
        // PostHog should be initialized
        expect(mockPostHog.init).toHaveBeenCalled();
        // Event should be captured
        expect(mockPostHog.capture).toHaveBeenCalledWith("test_event", {});
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("tracks events via posthog.capture", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        mockPostHog.capture.mockClear();

        yield* ph.trackEvent({
          event: "sign_up",
          properties: { method: "email", value: 100 },
        });

        expect(mockPostHog.capture).toHaveBeenCalledWith("sign_up", {
          method: "email",
          value: 100,
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("includes distinctId in event properties", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        mockPostHog.capture.mockClear();

        yield* ph.trackEvent({
          event: "purchase",
          distinctId: "user123",
          properties: { currency: "USD" },
        });

        expect(mockPostHog.capture).toHaveBeenCalledWith("purchase", {
          currency: "USD",
          distinct_id: "user123",
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("tracks page views with $pageview event", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        mockPostHog.capture.mockClear();

        yield* ph.trackPageView();

        expect(mockPostHog.capture).toHaveBeenCalledWith("$pageview", {});
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("includes properties in page view tracking", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        mockPostHog.capture.mockClear();

        yield* ph.trackPageView({
          distinctId: "user456",
          properties: { path: "/dashboard" },
        });

        expect(mockPostHog.capture).toHaveBeenCalledWith("$pageview", {
          path: "/dashboard",
          distinct_id: "user456",
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("identifies users with properties", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        mockPostHog.identify.mockClear();

        yield* ph.identify({
          distinctId: "user789",
          properties: { email: "user@example.com", name: "Test User" },
        });

        expect(mockPostHog.identify).toHaveBeenCalledWith("user789", {
          email: "user@example.com",
          name: "Test User",
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("handles script load errors gracefully", async () => {
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null),
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript && mockScript.onerror) {
              setTimeout(() => mockScript.onerror?.(), 0);
            }
          }),
        },
      };
      vi.stubGlobal("document", mockDocument);

      const layer = PostHog.layer({ apiKey: "phc_test123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Should not throw
        yield* ph.initialize();

        // Error should be logged
        expect(consoleErrorSpy).toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles case where script loads but posthog is unavailable", async () => {
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null),
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript && mockScript.onload) {
              // Don't set window.posthog before calling onload
              setTimeout(() => mockScript.onload?.(), 0);
            }
          }),
        },
      };
      vi.stubGlobal("document", mockDocument);

      const layer = PostHog.layer({ apiKey: "phc_test123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Should not throw
        yield* ph.initialize();

        // Error should be logged
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("initialization failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles posthog.capture errors gracefully", async () => {
      mockPostHog.capture.mockImplementation(() => {
        throw new Error("capture error");
      });

      const layer = PostHog.layer({ apiKey: "phc_test123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        // Should not throw
        yield* ph.trackEvent({ event: "test_event" });

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("trackEvent failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles posthog.identify errors gracefully", async () => {
      mockPostHog.identify.mockImplementation(() => {
        throw new Error("identify error");
      });

      const layer = PostHog.layer({ apiKey: "phc_test123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        // Should not throw
        yield* ph.identify({ distinctId: "user123" });

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("identify failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles posthog.capture errors for page views", async () => {
      mockPostHog.capture.mockImplementation(() => {
        throw new Error("capture pageview error");
      });

      const layer = PostHog.layer({ apiKey: "phc_test123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        yield* ph.initialize();

        // Should not throw
        yield* ph.trackPageView();

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("trackPageView failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });
  });

  describe("server environment", () => {
    let fetchMock: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      // Remove window to simulate server environment
      vi.stubGlobal("window", undefined);

      // Mock fetch
      fetchMock = vi.fn(() =>
        Promise.resolve({
          ok: true,
          status: 200,
          statusText: "OK",
        }),
      );
      vi.stubGlobal("fetch", fetchMock);
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("creates server implementation in server environment", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;
        expect(ph.type).toBe("server");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("does not require initialization in server environment", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Should succeed immediately
        yield* ph.initialize();

        // No fetch calls should be made
        expect(fetchMock).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("sends events via HTTP API", async () => {
      const layer = PostHog.layer({
        apiKey: "phc_test123",
        host: "https://us.i.posthog.com",
      });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.trackEvent({
          event: "purchase",
          distinctId: "user123",
          properties: { currency: "USD", value: 50 },
        });

        // Verify fetch was called with correct URL and payload
        expect(fetchMock).toHaveBeenCalledWith(
          "https://us.i.posthog.com/capture/",
          expect.objectContaining({
            method: "POST",
            headers: { "Content-Type": "application/json" },
          }),
        );

        // Parse and verify payload
        const callArgs = fetchMock.mock.calls[0] as [string, { body: string }];
        const body = JSON.parse(callArgs[1].body) as {
          api_key: string;
          event: string;
          distinct_id: string;
          properties: Record<string, unknown>;
          timestamp: string;
        };

        expect(body).toMatchObject({
          api_key: "phc_test123",
          event: "purchase",
          distinct_id: "user123",
          properties: { currency: "USD", value: 50 },
        });
        expect(body.timestamp).toBeDefined();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("uses anonymous distinct_id when not provided", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.trackEvent({
          event: "page_load",
        });

        const callArgs = fetchMock.mock.calls[0] as [string, { body: string }];
        const body = JSON.parse(callArgs[1].body) as {
          distinct_id: string;
        };

        expect(body.distinct_id).toBe("anonymous");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("sends page view events", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.trackPageView({
          distinctId: "user456",
          properties: { path: "/home" },
        });

        const callArgs = fetchMock.mock.calls[0] as [string, { body: string }];
        const body = JSON.parse(callArgs[1].body) as {
          event: string;
          distinct_id: string;
          properties: Record<string, unknown>;
        };

        expect(body).toMatchObject({
          event: "$pageview",
          distinct_id: "user456",
          properties: { path: "/home" },
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("sends identify events with $set properties", async () => {
      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.identify({
          distinctId: "user789",
          properties: { email: "user@example.com", name: "Test" },
        });

        const callArgs = fetchMock.mock.calls[0] as [string, { body: string }];
        const body = JSON.parse(callArgs[1].body) as {
          event: string;
          distinct_id: string;
          properties: { $set: Record<string, unknown> };
        };

        expect(body).toMatchObject({
          event: "$identify",
          distinct_id: "user789",
          properties: {
            $set: { email: "user@example.com", name: "Test" },
          },
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("handles HTTP errors gracefully", async () => {
      // Mock fetch to return error
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: "Bad Request",
      });

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Should not throw
        yield* ph.trackEvent({ event: "test" });

        // Error should be logged
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("server trackEvent failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles network errors gracefully", async () => {
      // Mock fetch to throw error
      fetchMock.mockRejectedValueOnce(new Error("Network error"));

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Should not throw
        yield* ph.trackEvent({ event: "test" });

        expect(consoleErrorSpy).toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles errors during identify", async () => {
      fetchMock.mockRejectedValueOnce(new Error("Identify error"));

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.identify({ distinctId: "user123" });

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("server identify failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles HTTP errors during identify", async () => {
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: "Internal Server Error",
      });

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.identify({ distinctId: "user123" });

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("server identify failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles errors during server trackPageView", async () => {
      fetchMock.mockRejectedValueOnce(new Error("PageView error"));

      const layer = PostHog.layer({ apiKey: "phc_test123" });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.trackPageView();

        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("server trackPageView failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });
  });

  describe("configuration validation", () => {
    beforeEach(() => {
      // Ensure we're in a defined environment (server)
      vi.stubGlobal("window", undefined);
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("validates required apiKey", async () => {
      const layer = PostHog.layer({
        // apiKey intentionally missing
      });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Should provide no-op implementation
        expect(ph.type).toBe("noop");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("validates non-empty apiKey", async () => {
      const layer = PostHog.layer({
        apiKey: "   ", // Empty/whitespace
      });

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        // Should provide no-op implementation
        expect(ph.type).toBe("noop");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });
  });

  describe("no-op implementation", () => {
    beforeEach(() => {
      vi.stubGlobal("window", undefined);
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("provides no-op implementation for invalid config", async () => {
      const layer = PostHog.layer({});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        expect(ph.type).toBe("noop");

        // All methods should succeed without side effects
        yield* ph.initialize();
        yield* ph.trackEvent({ event: "test" });
        yield* ph.trackPageView();
        yield* ph.identify({ distinctId: "user123" });

        // No errors should be thrown
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("no-op implementation has no side effects", async () => {
      const layer = PostHog.layer({});

      const fetchMock = vi.fn();
      vi.stubGlobal("fetch", fetchMock);

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ph = yield* PostHog;

        yield* ph.trackEvent({ event: "test" });

        // Should not make any network calls
        expect(fetchMock).not.toHaveBeenCalled();

        // Should not log errors
        expect(consoleErrorSpy).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });
  });
});
