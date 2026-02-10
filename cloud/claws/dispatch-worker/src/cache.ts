/**
 * LRU cache for bootstrap configs.
 *
 * Avoids re-fetching on every request — config only changes on deploy.
 * Max entries and TTL are configurable for testing.
 */

import type { OpenClawConfig } from "./types";

interface CacheEntry {
  config: OpenClawConfig;
  at: number;
}

export const CONFIG_CACHE_MAX = 100;
export const CONFIG_CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

const configCache = new Map<string, CacheEntry>();

export function getCachedConfig(
  clawId: string,
  now: number = Date.now(),
): OpenClawConfig | null {
  const entry = configCache.get(clawId);
  if (!entry) return null;
  if (now - entry.at > CONFIG_CACHE_TTL_MS) {
    configCache.delete(clawId);
    return null;
  }
  // Move to end (most recently used)
  configCache.delete(clawId);
  configCache.set(clawId, entry);
  return entry.config;
}

export function setCachedConfig(
  clawId: string,
  config: OpenClawConfig,
  now: number = Date.now(),
): void {
  // Evict oldest if at capacity
  if (configCache.size >= CONFIG_CACHE_MAX) {
    const oldest = configCache.keys().next().value;
    if (oldest !== undefined) {
      configCache.delete(oldest);
    }
  }
  configCache.set(clawId, { config, at: now });
}

/** Clear the entire cache. Exposed for testing. */
export function clearConfigCache(): void {
  configCache.clear();
}

/** Get current cache size. Exposed for testing. */
export function configCacheSize(): number {
  return configCache.size;
}
