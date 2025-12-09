/**
 * Site-wide constants
 */

// Import GitHub stats from build-time generated file
import githubStats from "./github-stats.json";
import type { ProductName } from "../content/spec";

// Site version information
export const SITE_VERSION = "1.1";

// Base URL for absolute URLs
// IMPORTANT: When changing this value, also update the hardcoded URLs in index.html
export const BASE_URL = "https://mirascope.com";

// Analytics constants
export const GA_MEASUREMENT_ID = "G-DJHT1QG9GK";
export const GTM_ID = "GTM-T8PZJDKM";
export const POSTHOG_PUBLIC_KEY = "phc_tnTm56utLwHvtXvjyIwj0rF1AKc6wgfLlczRRZ2dthy";

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

export const LILYPAD: ProductConfig = {
  title: "Lilypad",
  tagline: "Spin up your data flywheel with one line of code.",
  github: {
    repo: "Mirascope/lilypad",
    stars: githubStats.lilypad.stars,
    version: githubStats.lilypad.version,
  },
};

// Product configurations
export const PRODUCT_CONFIGS: Record<ProductName, ProductConfig> = {
  mirascope: MIRASCOPE,
  lilypad: LILYPAD,
};

// Helper function to get product config with defaulting to Mirascope
// Currently just uses productName not version since we assume this is conserved across versions
export function getProductConfigByName(product: ProductName): ProductConfig {
  return PRODUCT_CONFIGS[product || "mirascope"];
}
