/**
 * @fileoverview Tests for browser context collection and transformation.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

import {
  collectBrowserContext,
  toPostHogProperties,
  toGA4Properties,
  extractDomain,
  type BrowserContext,
} from "@/app/lib/browser-context";
import { LIBRARY_NAME, SITE_VERSION } from "@/app/lib/site";

/**
 * Creates a mock BrowserContext with default values.
 * Override specific fields as needed.
 */
function createMockBrowserContext(
  overrides: Partial<BrowserContext> = {},
): BrowserContext {
  return {
    currentUrl: "https://example.com/page",
    pathname: "/page",
    host: "example.com",
    referrer: "https://google.com/search",
    referringDomain: "google.com",
    pageTitle: "Test Page",
    initialReferrer: "https://google.com/",
    initialReferringDomain: "google.com",
    screenHeight: 1080,
    screenWidth: 1920,
    viewportHeight: 900,
    viewportWidth: 1600,
    browser: "Chrome",
    browserVersion: "120.0.0",
    os: "macOS",
    deviceType: "Desktop",
    device: "Mac",
    language: "en-US",
    lib: "mirascope-cloud",
    libVersion: "1.0.0",
    insertId: "test-uuid-1234",
    timestamp: "2024-01-01T00:00:00.000Z",
    ...overrides,
  };
}

describe("extractDomain", () => {
  it("extracts domain from valid URL", () => {
    expect(extractDomain("https://example.com/path")).toBe("example.com");
    expect(extractDomain("https://sub.example.com/path")).toBe(
      "sub.example.com",
    );
    expect(extractDomain("http://localhost:3000/page")).toBe("localhost");
  });

  it("returns empty string for empty URL", () => {
    expect(extractDomain("")).toBe("");
  });

  it("returns empty string for invalid URL", () => {
    expect(extractDomain("not-a-url")).toBe("");
    expect(extractDomain("://invalid")).toBe("");
  });
});

describe("toPostHogProperties", () => {
  it("transforms browser context to PostHog format with $ prefix", () => {
    const ctx = createMockBrowserContext();
    const result = toPostHogProperties(ctx);

    // Verify all keys have $ prefix (PostHog convention)
    const keys = Object.keys(result);
    expect(keys.every((key) => key.startsWith("$"))).toBe(true);
  });

  it("maps URL context properties correctly", () => {
    const ctx = createMockBrowserContext({
      currentUrl: "https://app.mirascope.com/dashboard",
      pathname: "/dashboard",
      host: "app.mirascope.com",
      referrer: "https://google.com/search?q=mirascope",
      referringDomain: "google.com",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$current_url).toBe("https://app.mirascope.com/dashboard");
    expect(result.$pathname).toBe("/dashboard");
    expect(result.$host).toBe("app.mirascope.com");
    expect(result.$referrer).toBe("https://google.com/search?q=mirascope");
    expect(result.$referring_domain).toBe("google.com");
  });

  it("maps screen and viewport properties correctly", () => {
    const ctx = createMockBrowserContext({
      screenWidth: 2560,
      screenHeight: 1440,
      viewportWidth: 1920,
      viewportHeight: 1080,
    });
    const result = toPostHogProperties(ctx);

    expect(result.$screen_width).toBe(2560);
    expect(result.$screen_height).toBe(1440);
    expect(result.$viewport_width).toBe(1920);
    expect(result.$viewport_height).toBe(1080);
  });

  it("maps browser and device properties correctly", () => {
    const ctx = createMockBrowserContext({
      browser: "Firefox",
      browserVersion: "121.0",
      os: "Windows 11",
      deviceType: "Desktop",
      device: "PC",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$browser).toBe("Firefox");
    expect(result.$browser_version).toBe("121.0");
    expect(result.$os).toBe("Windows 11");
    expect(result.$device_type).toBe("Desktop");
    expect(result.$device).toBe("PC");
  });

  it("maps metadata properties correctly", () => {
    const ctx = createMockBrowserContext({
      lib: "mirascope-cloud",
      libVersion: "2.0.0",
      insertId: "unique-event-id",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$lib).toBe("mirascope-cloud");
    expect(result.$lib_version).toBe("2.0.0");
    expect(result.$insert_id).toBe("unique-event-id");
  });

  it("handles empty referrer", () => {
    const ctx = createMockBrowserContext({
      referrer: "",
      referringDomain: "",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$referrer).toBe("");
    expect(result.$referring_domain).toBe("");
  });

  it("handles mobile device type", () => {
    const ctx = createMockBrowserContext({
      deviceType: "Mobile",
      device: "iPhone",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$device_type).toBe("Mobile");
    expect(result.$device).toBe("iPhone");
  });

  it("handles tablet device type", () => {
    const ctx = createMockBrowserContext({
      deviceType: "Tablet",
      device: "iPad",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$device_type).toBe("Tablet");
    expect(result.$device).toBe("iPad");
  });

  it("maps initial referrer properties correctly", () => {
    const ctx = createMockBrowserContext({
      initialReferrer: "https://twitter.com/post/123",
      initialReferringDomain: "twitter.com",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$initial_referrer).toBe("https://twitter.com/post/123");
    expect(result.$initial_referring_domain).toBe("twitter.com");
  });

  it("handles $direct initial referrer", () => {
    const ctx = createMockBrowserContext({
      initialReferrer: "$direct",
      initialReferringDomain: "$direct",
    });
    const result = toPostHogProperties(ctx);

    expect(result.$initial_referrer).toBe("$direct");
    expect(result.$initial_referring_domain).toBe("$direct");
  });
});

describe("toGA4Properties", () => {
  it("maps URL and page properties correctly", () => {
    const ctx = createMockBrowserContext({
      currentUrl: "https://app.mirascope.com/dashboard",
      pageTitle: "Dashboard | Mirascope",
      referrer: "https://google.com/search",
    });
    const result = toGA4Properties(ctx);

    expect(result.page_location).toBe("https://app.mirascope.com/dashboard");
    expect(result.page_title).toBe("Dashboard | Mirascope");
    expect(result.page_referrer).toBe("https://google.com/search");
  });

  it("formats screen_resolution as WxH string", () => {
    const ctx = createMockBrowserContext({
      screenWidth: 1920,
      screenHeight: 1080,
    });
    const result = toGA4Properties(ctx);

    expect(result.screen_resolution).toBe("1920x1080");
  });

  it("handles different screen resolutions", () => {
    const ctx1 = createMockBrowserContext({
      screenWidth: 2560,
      screenHeight: 1440,
    });
    expect(toGA4Properties(ctx1).screen_resolution).toBe("2560x1440");

    const ctx2 = createMockBrowserContext({
      screenWidth: 375,
      screenHeight: 812,
    });
    expect(toGA4Properties(ctx2).screen_resolution).toBe("375x812");

    const ctx3 = createMockBrowserContext({
      screenWidth: 768,
      screenHeight: 1024,
    });
    expect(toGA4Properties(ctx3).screen_resolution).toBe("768x1024");
  });

  it("maps language correctly", () => {
    const ctx = createMockBrowserContext({ language: "en-GB" });
    const result = toGA4Properties(ctx);

    expect(result.language).toBe("en-GB");
  });

  it("handles empty referrer", () => {
    const ctx = createMockBrowserContext({ referrer: "" });
    const result = toGA4Properties(ctx);

    expect(result.page_referrer).toBe("");
  });
});

describe("collectBrowserContext", () => {
  describe("in SSR environment (no window)", () => {
    beforeEach(() => {
      vi.stubGlobal("window", undefined);
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("returns empty context with defaults", () => {
      const ctx = collectBrowserContext();

      expect(ctx.currentUrl).toBe("");
      expect(ctx.pathname).toBe("");
      expect(ctx.host).toBe("");
      expect(ctx.screenWidth).toBe(0);
      expect(ctx.screenHeight).toBe(0);
      expect(ctx.browser).toBe("");
      expect(ctx.os).toBe("");
      expect(ctx.deviceType).toBe("Desktop");
      expect(ctx.initialReferrer).toBe("$direct");
      expect(ctx.initialReferringDomain).toBe("$direct");
      expect(ctx.lib).toBe(LIBRARY_NAME);
      expect(ctx.libVersion).toBe(SITE_VERSION);
      expect(ctx.insertId).toBeDefined();
      expect(ctx.timestamp).toBeDefined();
    });
  });

  describe("in browser environment", () => {
    let mockStorage: Map<string, string>;

    beforeEach(() => {
      mockStorage = new Map();

      vi.stubGlobal("window", {
        location: {
          href: "https://example.com/test?q=1",
          pathname: "/test",
          host: "example.com",
        },
        screen: {
          width: 1920,
          height: 1080,
        },
        innerWidth: 1600,
        innerHeight: 900,
      });

      vi.stubGlobal("document", {
        referrer: "https://google.com/search",
        title: "Test Page",
      });

      vi.stubGlobal("navigator", {
        userAgent:
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        language: "en-US",
      });

      // Mock crypto.randomUUID
      vi.stubGlobal("crypto", {
        randomUUID: () => "test-uuid-1234-5678",
      });

      // Mock localStorage
      vi.stubGlobal("localStorage", {
        getItem: (key: string) => mockStorage.get(key) ?? null,
        setItem: (key: string, value: string) => mockStorage.set(key, value),
        clear: () => mockStorage.clear(),
      });
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("collects URL context from window.location", () => {
      const ctx = collectBrowserContext();

      expect(ctx.currentUrl).toBe("https://example.com/test?q=1");
      expect(ctx.pathname).toBe("/test");
      expect(ctx.host).toBe("example.com");
    });

    it("collects referrer from document.referrer", () => {
      const ctx = collectBrowserContext();

      expect(ctx.referrer).toBe("https://google.com/search");
      expect(ctx.referringDomain).toBe("google.com");
    });

    it("collects page title from document.title", () => {
      const ctx = collectBrowserContext();

      expect(ctx.pageTitle).toBe("Test Page");
    });

    it("collects screen dimensions", () => {
      const ctx = collectBrowserContext();

      expect(ctx.screenWidth).toBe(1920);
      expect(ctx.screenHeight).toBe(1080);
    });

    it("collects viewport dimensions", () => {
      const ctx = collectBrowserContext();

      expect(ctx.viewportWidth).toBe(1600);
      expect(ctx.viewportHeight).toBe(900);
    });

    it("collects language from navigator.language", () => {
      const ctx = collectBrowserContext();

      expect(ctx.language).toBe("en-US");
    });

    it("detects Chrome browser", () => {
      const ctx = collectBrowserContext();

      expect(ctx.browser).toBe("Chrome");
      expect(ctx.browserVersion).toBe("120.0.0.0");
    });

    it("detects macOS", () => {
      const ctx = collectBrowserContext();

      expect(ctx.os).toContain("macOS");
    });

    it("detects Desktop device type", () => {
      const ctx = collectBrowserContext();

      expect(ctx.deviceType).toBe("Desktop");
      expect(ctx.device).toBe("Mac");
    });

    it("generates unique insertId", () => {
      const ctx = collectBrowserContext();

      expect(ctx.insertId).toBe("test-uuid-1234-5678");
    });

    it("generates ISO timestamp", () => {
      const ctx = collectBrowserContext();

      // Verify it's a valid ISO timestamp
      expect(() => new Date(ctx.timestamp)).not.toThrow();
      expect(ctx.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
    });

    it("includes library metadata", () => {
      const ctx = collectBrowserContext();

      expect(ctx.lib).toBe(LIBRARY_NAME);
      expect(ctx.libVersion).toBe(SITE_VERSION);
    });
  });

  describe("browser detection", () => {
    afterEach(() => {
      vi.unstubAllGlobals();
    });

    function setupBrowserTest(userAgent: string) {
      const mockStorage = new Map<string, string>();
      vi.stubGlobal("window", {
        location: { href: "", pathname: "", host: "" },
        screen: { width: 1920, height: 1080 },
        innerWidth: 1600,
        innerHeight: 900,
      });
      vi.stubGlobal("document", { referrer: "", title: "" });
      vi.stubGlobal("navigator", { userAgent, language: "en-US" });
      vi.stubGlobal("crypto", { randomUUID: () => "uuid" });
      vi.stubGlobal("localStorage", {
        getItem: (key: string) => mockStorage.get(key) ?? null,
        setItem: (key: string, value: string) => mockStorage.set(key, value),
      });
    }

    it("detects Firefox", () => {
      setupBrowserTest(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
      );
      const ctx = collectBrowserContext();
      expect(ctx.browser).toBe("Firefox");
      expect(ctx.browserVersion).toBe("121.0");
    });

    it("detects Safari", () => {
      setupBrowserTest(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
      );
      const ctx = collectBrowserContext();
      expect(ctx.browser).toBe("Safari");
      expect(ctx.browserVersion).toBe("17.2");
    });

    it("detects Edge", () => {
      setupBrowserTest(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
      );
      const ctx = collectBrowserContext();
      expect(ctx.browser).toBe("Edge");
      expect(ctx.browserVersion).toBe("120.0.0.0");
    });

    it("detects Opera", () => {
      setupBrowserTest(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
      );
      const ctx = collectBrowserContext();
      expect(ctx.browser).toBe("Opera");
      expect(ctx.browserVersion).toBe("106.0.0.0");
    });
  });

  describe("OS detection", () => {
    afterEach(() => {
      vi.unstubAllGlobals();
    });

    function setupOSTest(userAgent: string) {
      const mockStorage = new Map<string, string>();
      vi.stubGlobal("window", {
        location: { href: "", pathname: "", host: "" },
        screen: { width: 1920, height: 1080 },
        innerWidth: 1600,
        innerHeight: 900,
      });
      vi.stubGlobal("document", { referrer: "", title: "" });
      vi.stubGlobal("navigator", { userAgent, language: "en-US" });
      vi.stubGlobal("crypto", { randomUUID: () => "uuid" });
      vi.stubGlobal("localStorage", {
        getItem: (key: string) => mockStorage.get(key) ?? null,
        setItem: (key: string, value: string) => mockStorage.set(key, value),
      });
    }

    it("detects Windows 10", () => {
      setupOSTest(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
      );
      const ctx = collectBrowserContext();
      expect(ctx.os).toBe("Windows 10");
    });

    it("detects iOS", () => {
      setupOSTest(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
      );
      const ctx = collectBrowserContext();
      expect(ctx.os).toBe("iOS");
    });

    it("detects Android", () => {
      setupOSTest(
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile",
      );
      const ctx = collectBrowserContext();
      expect(ctx.os).toBe("Android");
    });

    it("detects Linux", () => {
      setupOSTest(
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0",
      );
      const ctx = collectBrowserContext();
      expect(ctx.os).toBe("Linux");
    });
  });

  describe("device type detection", () => {
    afterEach(() => {
      vi.unstubAllGlobals();
    });

    function setupDeviceTest(userAgent: string) {
      const mockStorage = new Map<string, string>();
      vi.stubGlobal("window", {
        location: { href: "", pathname: "", host: "" },
        screen: { width: 1920, height: 1080 },
        innerWidth: 1600,
        innerHeight: 900,
      });
      vi.stubGlobal("document", { referrer: "", title: "" });
      vi.stubGlobal("navigator", { userAgent, language: "en-US" });
      vi.stubGlobal("crypto", { randomUUID: () => "uuid" });
      vi.stubGlobal("localStorage", {
        getItem: (key: string) => mockStorage.get(key) ?? null,
        setItem: (key: string, value: string) => mockStorage.set(key, value),
      });
    }

    it("detects Mobile (iPhone)", () => {
      setupDeviceTest(
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
      );
      const ctx = collectBrowserContext();
      expect(ctx.deviceType).toBe("Mobile");
      expect(ctx.device).toBe("iPhone");
    });

    it("detects Tablet (iPad)", () => {
      setupDeviceTest(
        "Mozilla/5.0 (iPad; CPU OS 17_2 like Mac OS X) AppleWebKit/605.1.15",
      );
      const ctx = collectBrowserContext();
      expect(ctx.deviceType).toBe("Tablet");
      expect(ctx.device).toBe("iPad");
    });

    it("detects Tablet (Android tablet)", () => {
      setupDeviceTest(
        "Mozilla/5.0 (Linux; Android 14; SM-X910) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
      );
      const ctx = collectBrowserContext();
      expect(ctx.deviceType).toBe("Tablet");
    });

    it("detects Mobile (Android phone)", () => {
      setupDeviceTest(
        "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
      );
      const ctx = collectBrowserContext();
      expect(ctx.deviceType).toBe("Mobile");
    });

    it("detects Desktop (Windows)", () => {
      setupDeviceTest(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0",
      );
      const ctx = collectBrowserContext();
      expect(ctx.deviceType).toBe("Desktop");
      expect(ctx.device).toBe("PC");
    });
  });

  describe("initial referrer tracking", () => {
    let mockStorage: Map<string, string>;

    beforeEach(() => {
      mockStorage = new Map();

      vi.stubGlobal("window", {
        location: {
          href: "https://mirascope.com/docs",
          pathname: "/docs",
          host: "mirascope.com",
        },
        screen: { width: 1920, height: 1080 },
        innerWidth: 1600,
        innerHeight: 900,
      });

      vi.stubGlobal("navigator", {
        userAgent:
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0",
        language: "en-US",
      });

      vi.stubGlobal("crypto", {
        randomUUID: () => "test-uuid",
      });

      vi.stubGlobal("localStorage", {
        getItem: (key: string) => mockStorage.get(key) ?? null,
        setItem: (key: string, value: string) => mockStorage.set(key, value),
        clear: () => mockStorage.clear(),
      });
    });

    afterEach(() => {
      vi.unstubAllGlobals();
    });

    it("stores initial referrer on first visit from external source", () => {
      vi.stubGlobal("document", {
        referrer: "https://google.com/search?q=mirascope",
        title: "Test Page",
      });

      const ctx = collectBrowserContext();

      expect(ctx.initialReferrer).toBe("https://google.com/search?q=mirascope");
      expect(ctx.initialReferringDomain).toBe("google.com");
      expect(mockStorage.get("mirascope_initial_referrer")).toBe(
        "https://google.com/search?q=mirascope",
      );
      expect(mockStorage.get("mirascope_initial_referring_domain")).toBe(
        "google.com",
      );
    });

    it("preserves initial referrer on subsequent visits", () => {
      // Simulate first visit from Twitter
      mockStorage.set(
        "mirascope_initial_referrer",
        "https://twitter.com/post/123",
      );
      mockStorage.set("mirascope_initial_referring_domain", "twitter.com");

      // Now referrer is internal navigation
      vi.stubGlobal("document", {
        referrer: "https://mirascope.com/",
        title: "Docs",
      });

      const ctx = collectBrowserContext();

      // Should still show Twitter as initial referrer
      expect(ctx.initialReferrer).toBe("https://twitter.com/post/123");
      expect(ctx.initialReferringDomain).toBe("twitter.com");
    });

    it("uses $direct for direct traffic (no referrer)", () => {
      vi.stubGlobal("document", {
        referrer: "",
        title: "Test Page",
      });

      const ctx = collectBrowserContext();

      expect(ctx.initialReferrer).toBe("$direct");
      expect(ctx.initialReferringDomain).toBe("$direct");
      expect(mockStorage.get("mirascope_initial_referrer")).toBe("$direct");
      expect(mockStorage.get("mirascope_initial_referring_domain")).toBe(
        "$direct",
      );
    });

    it("handles localStorage unavailable gracefully", () => {
      // Mock localStorage to throw (simulating private browsing)
      vi.stubGlobal("localStorage", {
        getItem: () => {
          throw new Error("Access denied");
        },
        setItem: () => {
          throw new Error("Access denied");
        },
      });

      vi.stubGlobal("document", {
        referrer: "https://google.com/",
        title: "Test Page",
      });

      // Should not throw and fall back to current referrer
      const ctx = collectBrowserContext();

      expect(ctx.initialReferrer).toBe("https://google.com/");
      expect(ctx.initialReferringDomain).toBe("google.com");
    });

    it("handles partial localStorage state (only referrer stored)", () => {
      // Only one key stored (edge case)
      mockStorage.set("mirascope_initial_referrer", "https://google.com/");
      // mirascope_initial_referring_domain is missing

      vi.stubGlobal("document", {
        referrer: "https://twitter.com/",
        title: "Test Page",
      });

      const ctx = collectBrowserContext();

      // Should reinitialize from current referrer
      expect(ctx.initialReferrer).toBe("https://twitter.com/");
      expect(ctx.initialReferringDomain).toBe("twitter.com");
    });

    it("current referrer differs from initial referrer after navigation", () => {
      // First visit was from Google
      mockStorage.set("mirascope_initial_referrer", "https://google.com/");
      mockStorage.set("mirascope_initial_referring_domain", "google.com");

      // Current page was reached from internal navigation
      vi.stubGlobal("document", {
        referrer: "https://mirascope.com/docs/getting-started",
        title: "API Reference",
      });

      const ctx = collectBrowserContext();

      // Current referrer reflects where user came from
      expect(ctx.referrer).toBe("https://mirascope.com/docs/getting-started");
      expect(ctx.referringDomain).toBe("mirascope.com");

      // Initial referrer still shows original source
      expect(ctx.initialReferrer).toBe("https://google.com/");
      expect(ctx.initialReferringDomain).toBe("google.com");
    });
  });
});
