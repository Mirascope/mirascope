/**
 * Site-wide constants
 */

// Import GitHub stats from build-time generated file
import githubStats from "./github-stats.json";

// todo(seb): consolidate versions as part of posthog integration
// Site version information
export const SITE_VERSION = "2.0.0-alpha.5";

// Base URL for absolute URLs
export const BASE_URL = "https://mirascope.com";

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
