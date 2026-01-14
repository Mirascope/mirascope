/**
 * @fileoverview Tests for Google Analytics Effect-native service.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { Effect } from "effect";
import { GoogleAnalytics } from "@/analytics/google-client";

describe("GoogleAnalytics", () => {
  describe("client environment (browser)", () => {
    let mockScript: { onload?: () => void; onerror?: () => void };
    let mockDataLayer: unknown[];
    let mockGtag: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      // Reset all mocks
      vi.clearAllMocks();

      // Mock window object
      mockDataLayer = [];
      mockGtag = vi.fn((command, target, params) => {
        mockDataLayer.push([command, target, params]);
      });

      // Create mock script element
      mockScript = {};

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
              setTimeout(() => mockScript.onload?.(), 0);
            }
          }),
        },
      };

      // Mock window
      vi.stubGlobal("window", {
        dataLayer: mockDataLayer,
        gtag: mockGtag,
        location: { href: "https://example.com/test" },
      });
      vi.stubGlobal("document", mockDocument);
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("creates client implementation in browser environment", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        expect(ga.type).toBe("client");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("injects gtag script on initialization", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Verify script was created and appended
        expect(document.createElement).toHaveBeenCalledWith("script");
        expect(document.head.appendChild).toHaveBeenCalled();

        // Verify script properties
        expect(mockScript).toMatchObject({
          async: true,
          src: "https://www.googletagmanager.com/gtag/js?id=G-TEST123",
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("initializes dataLayer and gtag", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Verify gtag was called with js and config
        expect(mockGtag).toHaveBeenCalled();
        expect(mockDataLayer.length).toBeGreaterThan(0);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("only initializes once (caches initialization promise)", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Call initialize multiple times
        yield* ga.initialize();
        yield* ga.initialize();
        yield* ga.initialize();

        // Script should only be created once
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
          resolveScript = fn;
        },
        configurable: true,
      });

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Start multiple operations concurrently (they will all call ensureInitialized)
        const promise1 = Effect.runPromise(
          ga.trackEvent({ eventName: "event1" }),
        );
        const promise2 = Effect.runPromise(
          ga.trackPageView({ pagePath: "/page1" }),
        );
        const promise3 = Effect.runPromise(ga.setUserId("user1"));

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

    it("skips script injection if script already exists", async () => {
      // Mock querySelector to return an existing script
      const mockDocument = {
        createElement: vi.fn(),
        querySelector: vi.fn(() => ({
          src: "https://www.googletagmanager.com/gtag/js?id=G-TEST123",
        })),
        head: {
          appendChild: vi.fn(),
        },
      };
      vi.stubGlobal("document", mockDocument);

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Script creation should be skipped
        expect(mockDocument.createElement).not.toHaveBeenCalled();
        expect(mockDocument.head.appendChild).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("creates gtag function when not present", async () => {
      // Start with no gtag function
      const dataLayer: unknown[] = [];
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null),
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript && mockScript.onload) {
              setTimeout(() => mockScript.onload?.(), 0);
            }
          }),
        },
      };

      vi.stubGlobal("window", {
        dataLayer,
        // No gtag function initially
        location: { href: "https://example.com/test" },
      });
      vi.stubGlobal("document", mockDocument);

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Verify gtag was created
        expect(window.gtag).toBeDefined();

        // Verify gtag adds to dataLayer
        window.gtag("event", "test", { value: 1 });
        expect(dataLayer.length).toBeGreaterThan(0);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("preserves existing dataLayer when present", async () => {
      // Start with existing dataLayer
      const existingDataLayer = [["existing", "data"]];
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null),
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript && mockScript.onload) {
              setTimeout(() => mockScript.onload?.(), 0);
            }
          }),
        },
      };

      vi.stubGlobal("window", {
        dataLayer: existingDataLayer,
        location: { href: "https://example.com/test" },
      });
      vi.stubGlobal("document", mockDocument);

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Verify existing dataLayer was preserved
        expect(window.dataLayer[0]).toEqual(["existing", "data"]);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("initializes dataLayer when not present", async () => {
      // Start with no dataLayer (undefined)
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null),
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript && mockScript.onload) {
              setTimeout(() => mockScript.onload?.(), 0);
            }
          }),
        },
      };

      // Window without dataLayer
      vi.stubGlobal("window", {
        location: { href: "https://example.com/test" },
      });
      vi.stubGlobal("document", mockDocument);

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Verify dataLayer was created
        expect(window.dataLayer).toBeDefined();
        expect(Array.isArray(window.dataLayer)).toBe(true);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("tracks events via gtag", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Reset mock to clear initialization calls
        mockGtag.mockClear();

        yield* ga.trackEvent({
          eventName: "sign_up",
          eventParams: { method: "email", value: 100 },
        });

        // Verify gtag was called with correct parameters
        expect(mockGtag).toHaveBeenCalledWith("event", "sign_up", {
          method: "email",
          value: 100,
          send_to: "G-TEST123",
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("tracks page views", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        mockGtag.mockClear();

        yield* ga.trackPageView({
          pageTitle: "Dashboard",
          pagePath: "/dashboard",
        });

        // Verify gtag config call
        expect(mockGtag).toHaveBeenCalledWith(
          "config",
          "G-TEST123",
          expect.objectContaining({
            page_title: "Dashboard",
            page_path: "/dashboard",
          }),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("sets user ID and includes it in subsequent page views", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        mockGtag.mockClear();

        // Set user ID
        yield* ga.setUserId("user123");

        expect(mockGtag).toHaveBeenCalledWith("config", "G-TEST123", {
          user_id: "user123",
        });

        mockGtag.mockClear();

        // Track page view - should include user_id
        yield* ga.trackPageView({ pagePath: "/profile" });

        expect(mockGtag).toHaveBeenCalledWith(
          "config",
          "G-TEST123",
          expect.objectContaining({
            user_id: "user123",
            page_path: "/profile",
          }),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("clears user ID when set to null", async () => {
      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        yield* ga.setUserId("user123");
        mockGtag.mockClear();

        yield* ga.setUserId(null);

        // Should not call gtag when userId is null
        expect(mockGtag).not.toHaveBeenCalled();

        // Track page view - should NOT include user_id
        yield* ga.trackPageView({ pagePath: "/home" });

        expect(mockGtag).toHaveBeenCalledWith(
          "config",
          "G-TEST123",
          expect.not.objectContaining({
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            user_id: expect.anything(),
          }),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("handles script load errors gracefully", async () => {
      // Override appendChild to trigger error
      const mockDocument = {
        createElement: vi.fn(() => mockScript),
        querySelector: vi.fn(() => null), // No existing script
        head: {
          appendChild: vi.fn((node) => {
            if (node === mockScript && mockScript.onerror) {
              setTimeout(() => mockScript.onerror?.(), 0);
            }
          }),
        },
      };
      vi.stubGlobal("document", mockDocument);

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Should not throw
        yield* ga.initialize();

        // Error should be logged
        expect(consoleErrorSpy).toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
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
                setTimeout(() => mockScript.onload?.(), 0);
              }
            }
          }),
        },
      };
      vi.stubGlobal("document", mockDocument);

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // First attempt should fail
        yield* ga.initialize();
        expect(consoleErrorSpy).toHaveBeenCalled();

        // Verify script creation was attempted
        expect(mockDocument.createElement).toHaveBeenCalledTimes(1);

        consoleErrorSpy.mockClear();

        // Allow script to succeed on retry
        shouldFail = false;

        // Second attempt should succeed (retry after failure)
        yield* ga.trackEvent({ eventName: "test_retry" });

        // Verify script creation was attempted again (retry)
        expect(mockDocument.createElement).toHaveBeenCalledTimes(2);

        // Third attempt should use cached successful initialization
        yield* ga.trackPageView({ pagePath: "/test" });

        // Script should not be created again (already initialized)
        expect(mockDocument.createElement).toHaveBeenCalledTimes(2);
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles gtag errors gracefully during event tracking", async () => {
      // Mock gtag to throw error
      mockGtag.mockImplementation(() => {
        throw new Error("gtag error");
      });

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Should not throw
        yield* ga.trackEvent({ eventName: "test_event" });

        // Error should be logged
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("trackEvent failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles gtag errors gracefully during page view tracking", async () => {
      // Mock gtag to throw error
      mockGtag.mockImplementation(() => {
        throw new Error("gtag page view error");
      });

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Should not throw
        yield* ga.trackPageView({ pagePath: "/test" });

        // Error should be logged
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("trackPageView failed"),
          expect.anything(),
        );
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles gtag errors gracefully during setUserId", async () => {
      // Mock gtag to throw error
      mockGtag.mockImplementation(() => {
        throw new Error("gtag setUserId error");
      });

      const layer = GoogleAnalytics.layer({ measurementId: "G-TEST123" });
      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        yield* ga.initialize();

        // Should not throw
        yield* ga.setUserId("user123");

        // Error should be logged
        expect(consoleErrorSpy).toHaveBeenCalledWith(
          expect.stringContaining("setUserId failed"),
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
          status: 204,
          statusText: "No Content",
        }),
      );
      vi.stubGlobal("fetch", fetchMock);
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("creates server implementation in server environment", async () => {
      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;
        expect(ga.type).toBe("server");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("does not require initialization in server environment", async () => {
      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Should succeed immediately
        yield* ga.initialize();

        // No fetch calls should be made
        expect(fetchMock).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("sends events via Measurement Protocol", async () => {
      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        yield* ga.trackEvent({
          eventName: "purchase",
          eventParams: { currency: "USD", value: 50 },
        });

        // Verify fetch was called with correct URL and payload
        expect(fetchMock).toHaveBeenCalledWith(
          "https://www.google-analytics.com/mp/collect?measurement_id=G-TEST123&api_secret=secret123",
          expect.objectContaining({
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
            body: expect.stringContaining("purchase"),
          }),
        );

        // Parse and verify payload
        const callArgs = fetchMock.mock.calls[0] as [string, { body: string }];
        const body = JSON.parse(callArgs[1].body) as {
          client_id: string;
          events: Array<{ name: string; params: Record<string, unknown> }>;
        };

        expect(body).toMatchObject({
          // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment
          client_id: expect.stringMatching(/^server_\d+$/),
          events: [
            {
              name: "purchase",
              params: { currency: "USD", value: 50 },
            },
          ],
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("sends page view events", async () => {
      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        yield* ga.trackPageView({
          pageTitle: "Home",
          pagePath: "/",
        });

        const callArgs = fetchMock.mock.calls[0] as [string, { body: string }];
        const body = JSON.parse(callArgs[1].body) as {
          events: Array<{
            name: string;
            params: Record<string, unknown>;
          }>;
        };

        expect(body.events[0]).toMatchObject({
          name: "page_view",
          params: {
            page_title: "Home",
            page_location: "/",
          },
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("includes user ID in events when set", async () => {
      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        yield* ga.setUserId("user456");
        yield* ga.trackEvent({ eventName: "login" });

        const callArgs = fetchMock.mock.calls[0] as [string, { body: string }];
        const body = JSON.parse(callArgs[1].body) as {
          user_id: string;
          events: Array<{ name: string }>;
        };

        expect(body).toMatchObject({
          user_id: "user456",
          events: [{ name: "login" }],
        });
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("warns when apiSecret is missing", async () => {
      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        // apiSecret intentionally missing
      });

      const consoleWarnSpy = vi
        .spyOn(console, "warn")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        yield* ga.trackEvent({ eventName: "test" });

        // Should warn about missing API secret
        expect(consoleWarnSpy).toHaveBeenCalledWith(
          expect.stringContaining("API secret not configured"),
        );

        // Should not make fetch call
        expect(fetchMock).not.toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleWarnSpy.mockRestore();
    });

    it("handles HTTP errors gracefully", async () => {
      // Mock fetch to return error
      fetchMock.mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: "Bad Request",
      });

      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Should not throw
        yield* ga.trackEvent({ eventName: "test" });

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

      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Should not throw
        yield* ga.trackEvent({ eventName: "test" });

        expect(consoleErrorSpy).toHaveBeenCalled();
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));

      consoleErrorSpy.mockRestore();
    });

    it("handles errors during server trackPageView", async () => {
      // Mock fetch to throw error
      fetchMock.mockRejectedValueOnce(new Error("Server trackPageView error"));

      const layer = GoogleAnalytics.layer({
        measurementId: "G-TEST123",
        apiSecret: "secret123",
      });

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Should not throw
        yield* ga.trackPageView({ pagePath: "/test" });

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

    it("validates required measurementId", async () => {
      const layer = GoogleAnalytics.layer({
        // measurementId intentionally missing
      });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Should provide no-op implementation
        expect(ga.type).toBe("noop");
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("validates non-empty measurementId", async () => {
      const layer = GoogleAnalytics.layer({
        measurementId: "   ", // Empty/whitespace
      });

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        // Should provide no-op implementation
        expect(ga.type).toBe("noop");
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
      const layer = GoogleAnalytics.layer({});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        expect(ga.type).toBe("noop");

        // All methods should succeed without side effects
        yield* ga.initialize();
        yield* ga.trackEvent({ eventName: "test" });
        yield* ga.trackPageView({ pagePath: "/" });
        yield* ga.setUserId("user123");

        // No errors should be thrown
      });

      await Effect.runPromise(program.pipe(Effect.provide(layer)));
    });

    it("no-op implementation has no side effects", async () => {
      const layer = GoogleAnalytics.layer({});

      const fetchMock = vi.fn();
      vi.stubGlobal("fetch", fetchMock);

      const consoleErrorSpy = vi
        .spyOn(console, "error")
        .mockImplementation(() => {});

      const program = Effect.gen(function* () {
        const ga = yield* GoogleAnalytics;

        yield* ga.trackEvent({ eventName: "test" });

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
