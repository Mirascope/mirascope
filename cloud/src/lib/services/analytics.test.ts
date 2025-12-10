/// <reference lib="dom" />

import {
  describe,
  test,
  expect,
  beforeEach,
  afterEach,
  mock,
  spyOn,
} from "bun:test";
import { AnalyticsManager } from "./analytics";

describe("AnalyticsManager", () => {
  let analyticsManager: AnalyticsManager;
  const originalNodeEnv = process.env.NODE_ENV;
  let originalIsBrowser: boolean;
  let originalConsoleLog: any;
  let originalConsoleError: any;
  let originalDocumentCreateElement: any;
  let originalHeadAppendChild: any;

  beforeEach(() => {
    // Suppress console output during tests
    originalConsoleLog = console.log;
    originalConsoleError = console.error;
    console.log = mock(() => {});
    console.error = mock(() => {});

    // Store original isBrowser value
    originalIsBrowser = (global as any).isBrowser;

    // Set to browser environment for testing
    (global as any).isBrowser = true;

    // Mock document.createElement to prevent actual script creation
    originalDocumentCreateElement = document.createElement;
    originalHeadAppendChild = document.head.appendChild;

    // Mock script creation and injection
    const mockCreateElement = spyOn(document, "createElement");
    mockCreateElement.mockImplementation((tagName: string) => {
      const element = originalDocumentCreateElement.call(document, tagName);

      // Mock script element behavior to prevent actual script execution
      if (tagName === "script") {
        // Prevent the script's innerHTML from being evaluated
        Object.defineProperty(element, "innerHTML", {
          set: function (value) {
            // Store the value but don't evaluate it
            this._innerHTML = value;
          },
          get: function () {
            return this._innerHTML || "";
          },
        });
      }

      return element;
    });

    // Mock appendChild to track but not actually append scripts
    const mockAppendChild = spyOn(document.head, "appendChild");
    mockAppendChild.mockImplementation((node: Node) => {
      // If it's a script, don't actually append it
      if (node.nodeName === "SCRIPT") {
        // Mark as "appended" for tracking
        return node;
      }

      // For non-scripts, use the original behavior
      return originalHeadAppendChild.call(document.head, node);
    });

    // Add necessary properties that aren't in happy-dom by default
    window.dataLayer = window.dataLayer || [];
    window.gtag =
      window.gtag ||
      mock((_command: string, _action: string, _params?: any) => {});

    // Mock PostHog with all required methods
    window.posthog = window.posthog || {
      init: mock((_apiKey: string, _options?: any) => {}),
      capture: mock(
        (_eventName: string, _properties?: Record<string, any>) => {},
      ),
      identify: mock(
        (_distinctId: string, _properties?: Record<string, any>) => {},
      ),
      opt_in_capturing: mock(() => {}),
      opt_out_capturing: mock(() => {}),
      has_opted_in_capturing: mock((): boolean => false),
      has_opted_out_capturing: mock((): boolean => false),
      reset: mock(() => {}),
    };

    // Set NODE_ENV to production for tests
    process.env.NODE_ENV = "production";

    // Create fresh analytics manager for each test
    analyticsManager = new AnalyticsManager(
      "test-ga-id",
      "test-gtm-id",
      "test-ph-key",
      "test-version",
    );
  });

  afterEach(() => {
    // Reset mocks
    mock.restore();

    // Restore original console methods
    console.log = originalConsoleLog;
    console.error = originalConsoleError;

    // Restore original values
    (global as any).isBrowser = originalIsBrowser;
    process.env.NODE_ENV = originalNodeEnv;

    // Clear localStorage
    localStorage.clear();
  });

  test("analytics manager is created with correct properties", () => {
    expect(analyticsManager).toBeDefined();
    expect((analyticsManager as any).gaMeasurementId).toBe("test-ga-id");
    expect((analyticsManager as any).posthogApiKey).toBe("test-ph-key");
    expect((analyticsManager as any).siteVersion).toBe("test-version");
  });

  test("isEnabled returns true in production", async () => {
    expect(await analyticsManager.isEnabled()).toBe(true);
  });

  test("isEnabled returns false in development", async () => {
    process.env.NODE_ENV = "development";
    expect(await analyticsManager.isEnabled()).toBe(false);
    process.env.NODE_ENV = "production";
  });

  test("enableAnalytics initializes tracking when enabled", async () => {
    // Spy on private initializeGoogleAnalytics method
    const initializeSpy = spyOn(
      analyticsManager as any,
      "initializeGoogleAnalytics",
    );
    const initializePostHogSpy = spyOn(
      analyticsManager as any,
      "initializePostHog",
    );

    // When analytics should be enabled
    const isEnabledSpy = spyOn(analyticsManager, "isEnabled");
    isEnabledSpy.mockResolvedValue(true);

    expect(await analyticsManager.enableAnalytics()).toBe(true);
    expect(initializeSpy).toHaveBeenCalled();
    expect(initializePostHogSpy).toHaveBeenCalled();

    // When analytics should be disabled
    isEnabledSpy.mockResolvedValue(false);
    expect(await analyticsManager.enableAnalytics()).toBe(false);

    // Should not call initialize again
    expect(initializeSpy.mock.calls.length).toBe(1);
  });

  test("trackPageView only tracks when analytics is enabled", async () => {
    // Create a fresh gtag mock for this test
    const gtagMock = mock(
      (_command: string, _action: string, _params?: any) => {},
    );
    window.gtag = gtagMock;

    // When analytics is enabled
    const enableSpy = spyOn(analyticsManager, "enableAnalytics");
    enableSpy.mockResolvedValue(true);

    await analyticsManager.trackPageView("/test-page");
    expect(gtagMock).toHaveBeenCalled();

    // Reset the mock for the second part of the test
    gtagMock.mockReset();

    // When analytics is disabled
    enableSpy.mockResolvedValue(false);

    await analyticsManager.trackPageView("/test-page");
    expect(gtagMock).not.toHaveBeenCalled();
  });

  test("trackEvent sends events to both GA and PostHog when enabled", async () => {
    // Create fresh mocks for this test
    const gtagMock = mock(
      (_command: string, _action: string, _params?: any) => {},
    );
    window.gtag = gtagMock;

    const posthogCaptureMock = mock(
      (_eventName: string, _properties?: Record<string, any>) => {},
    );
    window.posthog = {
      ...window.posthog!,
      capture: posthogCaptureMock,
    };

    // Enable analytics
    const enableSpy = spyOn(analyticsManager, "enableAnalytics");
    enableSpy.mockResolvedValue(true);

    // Track event
    await analyticsManager.trackEvent("test_event", { test_property: "value" });

    // Verify both analytics services were called
    expect(gtagMock).toHaveBeenCalled();
    expect(posthogCaptureMock).toHaveBeenCalled();

    // Reset mocks for the second part of the test
    gtagMock.mockReset();
    posthogCaptureMock.mockReset();

    // Disable analytics
    enableSpy.mockResolvedValue(false);

    // Track event with analytics disabled
    await analyticsManager.trackEvent("test_event", { test_property: "value" });

    // Verify neither service was called
    expect(gtagMock).not.toHaveBeenCalled();
    expect(posthogCaptureMock).not.toHaveBeenCalled();
  });
});
