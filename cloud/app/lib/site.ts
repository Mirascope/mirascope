/**
 * Site-wide constants
 */

// Import GitHub stats from build-time generated file
import githubStats from "./github-stats.json";

// Site version information for analytics tracking
export const SITE_VERSION = "2.1.1";
export const LIBRARY_NAME = "mirascope";

// Base URL for absolute URLs
export const BASE_URL = "https://mirascope.com";

// Discord invite URL (uses full URL to work in all environments including local dev)
export const DISCORD_INVITE_URL = "https://mirascope.com/discord-invite";

// Analytics constants
export const GA_MEASUREMENT_ID = "G-DJHT1QG9GK";
export const GTM_ID = "GTM-T8PZJDKM";
export const POSTHOG_PUBLIC_KEY =
  "phc_tnTm56utLwHvtXvjyIwj0rF1AKc6wgfLlczRRZ2dthy";

export interface GithubInfo {
  repo: string;
  stars: number;
  version: string;
}

export interface ProductConfig {
  title: string;
  tagline: string;
  github: GithubInfo;
}

export const MIRASCOPE: ProductConfig = {
  title: "Mirascope",
  tagline: "LLM abstractions that aren't obstructions.",
  github: {
    repo: "Mirascope/mirascope",
    stars: githubStats.mirascope.stars,
    version: githubStats.mirascope.version,
  },
};

export const isDevelopment = () => import.meta.env?.DEV ?? false;
