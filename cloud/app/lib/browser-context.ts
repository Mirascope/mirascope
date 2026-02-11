/**
 * @fileoverview Browser context collection for analytics.
 *
 * Collects browser properties that PostHog JS SDK and GA4 gtag.js normally
 * auto-capture, enabling rich analytics data through our proxy architecture.
 *
 * ## Usage
 *
 * ```typescript
 * import { collectBrowserContext, toPostHogProperties, toGA4Properties } from "@/app/lib/browser-context";
 *
 * const context = collectBrowserContext();
 * const posthogProps = toPostHogProperties(context);
 * const ga4Props = toGA4Properties(context);
 * ```
 */

/**
 * Browser context collected from the client.
 * This is the internal representation used by our analytics system.
 */
export interface BrowserContext {
  // URL context
  readonly currentUrl: string;
  readonly pathname: string;
  readonly host: string;
  readonly referrer: string;
  readonly referringDomain: string;
  readonly pageTitle: string;

  // Initial referrer (persisted in localStorage)
  readonly initialReferrer: string;
  readonly initialReferringDomain: string;

  // Screen/viewport
  readonly screenHeight: number;
  readonly screenWidth: number;
  readonly viewportHeight: number;
  readonly viewportWidth: number;

  // Device/browser (parsed from user agent)
  readonly browser: string;
  readonly browserVersion: string;
  readonly os: string;
  readonly deviceType: "Desktop" | "Mobile" | "Tablet";
  readonly device: string;

  // Locale
  readonly language: string;

  // Metadata
  readonly lib: string;
  readonly libVersion: string;
  readonly insertId: string;
  readonly timestamp: string;

  // Anonymous user ID (persisted in localStorage for user deduplication)
  readonly anonymousId: string;
}

/**
 * PostHog standard properties.
 * Keys must exactly match what PostHog JS SDK sends.
 * @see https://posthog.com/docs/data/autocapture#properties
 */
export interface PostHogProperties {
  readonly $current_url: string;
  readonly $pathname: string;
  readonly $host: string;
  readonly $referrer: string;
  readonly $referring_domain: string;
  readonly $initial_referrer: string;
  readonly $initial_referring_domain: string;
  readonly $screen_height: number;
  readonly $screen_width: number;
  readonly $viewport_height: number;
  readonly $viewport_width: number;
  readonly $browser: string;
  readonly $browser_version: string;
  readonly $os: string;
  readonly $device_type: "Desktop" | "Mobile" | "Tablet";
  readonly $device: string;
  readonly $lib: string;
  readonly $lib_version: string;
  readonly $insert_id: string;
}

/**
 * GA4 Measurement Protocol event parameters.
 * Keys must exactly match GA4 API expectations.
 * @see https://developers.google.com/analytics/devguides/collection/protocol/ga4/reference
 */
export interface GA4Properties {
  readonly page_location: string;
  readonly page_title: string;
  readonly page_referrer: string;
  readonly screen_resolution: string;
  readonly language: string;
}

import { LIBRARY_NAME, SITE_VERSION } from "@/app/lib/site";

/**
 * Extracts domain from a URL string.
 * Returns empty string if URL is empty or invalid.
 */
export function extractDomain(url: string): string {
  if (!url) return "";
  try {
    const parsed = new URL(url);
    return parsed.hostname;
  } catch {
    return "";
  }
}

/**
 * Generates a UUID v4.
 * Used for anonymousId (user deduplication) and insertId (event deduplication).
 */
function generateUUID(): string {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  // Fallback for environments without crypto.randomUUID
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Browser detection patterns.
 */
interface BrowserInfo {
  browser: string;
  browserVersion: string;
}

function detectBrowser(userAgent: string): BrowserInfo {
  const ua = userAgent.toLowerCase();

  // Order matters: check more specific patterns first
  const patterns: Array<{ pattern: RegExp; name: string }> = [
    { pattern: /edg(?:e|a|ios)?\/(\d+[\d.]*)/, name: "Edge" },
    { pattern: /opr\/(\d+[\d.]*)/, name: "Opera" },
    { pattern: /opera\/(\d+[\d.]*)/, name: "Opera" },
    { pattern: /chrome\/(\d+[\d.]*)/, name: "Chrome" },
    { pattern: /crios\/(\d+[\d.]*)/, name: "Chrome" },
    { pattern: /firefox\/(\d+[\d.]*)/, name: "Firefox" },
    { pattern: /fxios\/(\d+[\d.]*)/, name: "Firefox" },
    { pattern: /safari\/(\d+[\d.]*)/, name: "Safari" },
    { pattern: /msie\s(\d+[\d.]*)/, name: "Internet Explorer" },
    { pattern: /trident.*rv:(\d+[\d.]*)/, name: "Internet Explorer" },
  ];

  for (const { pattern, name } of patterns) {
    const match = ua.match(pattern);
    if (match) {
      // For Safari, we need to get version from Version/ instead
      if (name === "Safari") {
        const versionMatch = ua.match(/version\/(\d+[\d.]*)/);
        return {
          browser: name,
          browserVersion: versionMatch ? versionMatch[1] : match[1],
        };
      }
      return { browser: name, browserVersion: match[1] };
    }
  }

  return { browser: "Unknown", browserVersion: "" };
}

/**
 * OS detection patterns.
 */
function detectOS(userAgent: string): string {
  const ua = userAgent.toLowerCase();

  if (ua.includes("windows nt 10")) return "Windows 10";
  if (ua.includes("windows nt 11")) return "Windows 11";
  if (ua.includes("windows nt 6.3")) return "Windows 8.1";
  if (ua.includes("windows nt 6.2")) return "Windows 8";
  if (ua.includes("windows nt 6.1")) return "Windows 7";
  if (ua.includes("windows")) return "Windows";
  // Check iOS BEFORE macOS since iOS UAs contain "like Mac OS X"
  if (ua.includes("iphone") || ua.includes("ipad") || ua.includes("ipod"))
    return "iOS";
  if (ua.includes("mac os x")) {
    const match = ua.match(/mac os x (\d+[._]\d+)/);
    if (match) {
      return `macOS ${match[1].replace("_", ".")}`;
    }
    return "macOS";
  }
  if (ua.includes("android")) return "Android";
  if (ua.includes("linux")) return "Linux";
  if (ua.includes("cros")) return "Chrome OS";

  return "Unknown";
}

/**
 * Device type detection.
 */
function detectDeviceType(userAgent: string): "Desktop" | "Mobile" | "Tablet" {
  const ua = userAgent.toLowerCase();

  // Check for tablets first (before mobile)
  if (
    ua.includes("ipad") ||
    (ua.includes("android") && !ua.includes("mobile"))
  ) {
    return "Tablet";
  }

  // Check for mobile devices
  if (
    ua.includes("iphone") ||
    ua.includes("ipod") ||
    (ua.includes("android") && ua.includes("mobile")) ||
    ua.includes("windows phone") ||
    ua.includes("blackberry")
  ) {
    return "Mobile";
  }

  return "Desktop";
}

/**
 * Device name detection.
 */
function detectDevice(userAgent: string): string {
  const ua = userAgent.toLowerCase();

  if (ua.includes("iphone")) return "iPhone";
  if (ua.includes("ipad")) return "iPad";
  if (ua.includes("ipod")) return "iPod";
  if (ua.includes("macintosh") || ua.includes("mac os")) return "Mac";
  if (ua.includes("windows")) return "PC";
  if (ua.includes("android")) {
    // Try to extract device model
    const match = userAgent.match(/;\s*([^;)]+)\s+Build/i);
    if (match) return match[1].trim();
    return "Android Device";
  }
  if (ua.includes("linux")) return "Linux Device";

  return "Unknown";
}

// localStorage keys for persistence
const INITIAL_REFERRER_KEY = "mirascope_initial_referrer";
const INITIAL_REFERRING_DOMAIN_KEY = "mirascope_initial_referring_domain";
const ANONYMOUS_ID_KEY = "mirascope_anonymous_id";

/**
 * Safely reads from localStorage.
 * Returns null if localStorage is unavailable (private browsing).
 */
function safeLocalStorageGet(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

/**
 * Safely writes to localStorage.
 * No-op if localStorage is unavailable.
 */
function safeLocalStorageSet(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    // Ignore - localStorage unavailable
  }
}

/**
 * Gets or initializes the initial referrer.
 * - On first visit: stores current referrer (or "$direct") in localStorage
 * - On subsequent visits: returns stored value
 * - If localStorage unavailable: returns "$direct"
 */
function getOrInitializeInitialReferrer(): {
  referrer: string;
  domain: string;
} {
  const storedReferrer = safeLocalStorageGet(INITIAL_REFERRER_KEY);
  const storedDomain = safeLocalStorageGet(INITIAL_REFERRING_DOMAIN_KEY);

  // Already initialized
  if (storedReferrer !== null && storedDomain !== null) {
    return { referrer: storedReferrer, domain: storedDomain };
  }

  // First visit - initialize from current referrer
  const currentReferrer = document.referrer || "$direct";
  const currentDomain = document.referrer
    ? extractDomain(document.referrer)
    : "$direct";

  safeLocalStorageSet(INITIAL_REFERRER_KEY, currentReferrer);
  safeLocalStorageSet(INITIAL_REFERRING_DOMAIN_KEY, currentDomain);

  return { referrer: currentReferrer, domain: currentDomain };
}

/**
 * Gets or initializes the anonymous user ID.
 * - On first visit: generates UUID and stores in localStorage
 * - On subsequent visits: returns stored value
 * - If localStorage unavailable: generates fresh UUID (no persistence)
 */
function getOrInitializeAnonymousId(): string {
  const storedId = safeLocalStorageGet(ANONYMOUS_ID_KEY);
  if (storedId) {
    return storedId;
  }

  const newId = generateUUID();
  safeLocalStorageSet(ANONYMOUS_ID_KEY, newId);
  return newId;
}

/**
 * Collects browser context from the current window.
 * Should only be called in browser environment.
 */
export function collectBrowserContext(): BrowserContext {
  // Only track real users in browsers, not prerender builds.
  // Use document (not window) since Workers have window-like globals.
  if (typeof document === "undefined") {
    // Empty context prevents build crashes, replaced client-side
    return {
      currentUrl: "",
      pathname: "",
      host: "",
      referrer: "",
      referringDomain: "",
      pageTitle: "",
      initialReferrer: "$direct",
      initialReferringDomain: "$direct",
      screenHeight: 0,
      screenWidth: 0,
      viewportHeight: 0,
      viewportWidth: 0,
      browser: "",
      browserVersion: "",
      os: "",
      deviceType: "Desktop",
      device: "",
      language: "",
      lib: LIBRARY_NAME,
      libVersion: SITE_VERSION,
      anonymousId: generateUUID(), // Fresh ID for SSR (won't persist)
      insertId: generateUUID(),
      timestamp: new Date().toISOString(),
    };
  }

  const userAgent = navigator.userAgent;
  const { browser, browserVersion } = detectBrowser(userAgent);
  const { referrer: initialReferrer, domain: initialReferringDomain } =
    getOrInitializeInitialReferrer();

  return {
    // URL context
    currentUrl: window.location.href,
    pathname: window.location.pathname,
    host: window.location.host,
    referrer: document.referrer,
    referringDomain: extractDomain(document.referrer),
    pageTitle: document.title,

    // Initial referrer (persisted)
    initialReferrer,
    initialReferringDomain,

    // Screen/viewport
    screenHeight: window.screen.height,
    screenWidth: window.screen.width,
    viewportHeight: window.innerHeight,
    viewportWidth: window.innerWidth,

    // Device/browser
    browser,
    browserVersion,
    os: detectOS(userAgent),
    deviceType: detectDeviceType(userAgent),
    device: detectDevice(userAgent),

    // Locale
    language: navigator.language,

    // Metadata
    lib: LIBRARY_NAME,
    libVersion: SITE_VERSION,
    anonymousId: getOrInitializeAnonymousId(),
    insertId: generateUUID(),
    timestamp: new Date().toISOString(),
  };
}

/**
 * Transforms browser context to PostHog property format.
 * All keys are prefixed with $ as per PostHog convention.
 */
export function toPostHogProperties(ctx: BrowserContext): PostHogProperties {
  return {
    $current_url: ctx.currentUrl,
    $pathname: ctx.pathname,
    $host: ctx.host,
    $referrer: ctx.referrer,
    $referring_domain: ctx.referringDomain,
    $initial_referrer: ctx.initialReferrer,
    $initial_referring_domain: ctx.initialReferringDomain,
    $screen_height: ctx.screenHeight,
    $screen_width: ctx.screenWidth,
    $viewport_height: ctx.viewportHeight,
    $viewport_width: ctx.viewportWidth,
    $browser: ctx.browser,
    $browser_version: ctx.browserVersion,
    $os: ctx.os,
    $device_type: ctx.deviceType,
    $device: ctx.device,
    $lib: ctx.lib,
    $lib_version: ctx.libVersion,
    $insert_id: ctx.insertId,
  };
}

/**
 * Transforms browser context to GA4 Measurement Protocol format.
 */
export function toGA4Properties(ctx: BrowserContext): GA4Properties {
  return {
    page_location: ctx.currentUrl,
    page_title: ctx.pageTitle,
    page_referrer: ctx.referrer,
    screen_resolution: `${ctx.screenWidth}x${ctx.screenHeight}`,
    language: ctx.language,
  };
}
