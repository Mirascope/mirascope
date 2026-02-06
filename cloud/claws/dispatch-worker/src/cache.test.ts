import { describe, it, expect, beforeEach } from "vitest";

import {
  getCachedConfig,
  setCachedConfig,
  clearConfigCache,
  configCacheSize,
  CONFIG_CACHE_MAX,
  CONFIG_CACHE_TTL_MS,
} from "./cache";
import { createMockConfig } from "./test-helpers";

describe("config cache", () => {
  beforeEach(() => {
    clearConfigCache();
  });

  it("returns null for cache miss", () => {
    expect(getCachedConfig("nonexistent")).toBeNull();
  });

  it("stores and retrieves a config", () => {
    const config = createMockConfig({ clawId: "claw-1" });
    setCachedConfig("claw-1", config);
    expect(getCachedConfig("claw-1")).toEqual(config);
  });

  it("returns null after TTL expires", () => {
    const now = 1000000;
    const config = createMockConfig({ clawId: "claw-1" });
    setCachedConfig("claw-1", config, now);

    // Still valid just before TTL
    expect(getCachedConfig("claw-1", now + CONFIG_CACHE_TTL_MS - 1)).toEqual(
      config,
    );

    // Expired at exactly TTL + 1
    expect(getCachedConfig("claw-1", now + CONFIG_CACHE_TTL_MS + 1)).toBeNull();
  });

  it("evicts oldest entry when at capacity", () => {
    // Fill cache to max
    for (let i = 0; i < CONFIG_CACHE_MAX; i++) {
      setCachedConfig(`claw-${i}`, createMockConfig({ clawId: `claw-${i}` }));
    }
    expect(configCacheSize()).toBe(CONFIG_CACHE_MAX);

    // Add one more — should evict claw-0 (oldest)
    setCachedConfig("claw-new", createMockConfig({ clawId: "claw-new" }));
    expect(configCacheSize()).toBe(CONFIG_CACHE_MAX);
    expect(getCachedConfig("claw-0")).toBeNull();
    expect(getCachedConfig("claw-new")).not.toBeNull();
  });

  it("promotes accessed entries (LRU behavior)", () => {
    // Insert claw-0, claw-1, claw-2
    for (let i = 0; i < CONFIG_CACHE_MAX; i++) {
      setCachedConfig(`claw-${i}`, createMockConfig({ clawId: `claw-${i}` }));
    }

    // Access claw-0 to promote it (moves to end)
    getCachedConfig("claw-0");

    // Add a new entry — should evict claw-1 (now oldest), not claw-0
    setCachedConfig("claw-new", createMockConfig({ clawId: "claw-new" }));
    expect(getCachedConfig("claw-0")).not.toBeNull(); // promoted, not evicted
    expect(getCachedConfig("claw-1")).toBeNull(); // evicted
  });

  it("clearConfigCache empties the cache", () => {
    setCachedConfig("claw-1", createMockConfig());
    expect(configCacheSize()).toBe(1);
    clearConfigCache();
    expect(configCacheSize()).toBe(0);
  });
});
