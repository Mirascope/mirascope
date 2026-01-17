/**
 * @fileoverview Test utilities for rate limiting.
 *
 * Provides MockRateLimiter implementation for testing rate limiting without
 * requiring actual Cloudflare rate limiter bindings.
 */

import type { RateLimiterBinding } from "@/workers/config";

/**
 * Mock implementation of Cloudflare rate limiter binding for testing.
 *
 * Provides an in-memory counter that mimics rate limiter behavior including:
 * - Token bucket algorithm
 * - Automatic reset after period expires
 * - Per-key rate limiting
 *
 * @example
 * ```ts
 * const mockLimiter = new MockRateLimiter(100);
 * const result = await mockLimiter.limit({ key: "org_123" });
 * console.log(result.success); // true or false
 * ```
 */
export class MockRateLimiter implements RateLimiterBinding {
  private counters: Map<string, { count: number; resetAt: number }> = new Map();
  private readonly limitValue: number;
  private readonly periodMs: number = 60000;

  constructor(limit: number) {
    this.limitValue = limit;
  }

  /**
   * Check if the key is within the rate limit.
   *
   * @param options - Options containing the key to check
   * @returns Promise resolving to { success: true } if allowed, { success: false } if rate limited
   */
  // eslint-disable-next-line @typescript-eslint/require-await
  async limit(options: { key: string }): Promise<{ success: boolean }> {
    // Special case: if limit is 0, always deny
    if (this.limitValue === 0) {
      return { success: false };
    }

    const now = Date.now();
    const entry = this.counters.get(options.key);

    // Reset if period expired
    if (!entry || now >= entry.resetAt) {
      this.counters.set(options.key, {
        count: 1,
        resetAt: now + this.periodMs,
      });
      return { success: true };
    }

    // Increment counter
    entry.count += 1;

    // Check limit
    if (entry.count > this.limitValue) {
      return { success: false };
    }

    return { success: true };
  }

  /**
   * Reset all counters (test utility).
   */
  reset(): void {
    this.counters.clear();
  }

  /**
   * Get current count for a key (test utility).
   *
   * @param key - The key to check
   * @returns Current count, or 0 if key doesn't exist or expired
   */
  getCount(key: string): number {
    const entry = this.counters.get(key);
    if (!entry || Date.now() >= entry.resetAt) {
      return 0;
    }
    return entry.count;
  }
}
