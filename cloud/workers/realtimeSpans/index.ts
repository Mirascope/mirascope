/**
 * @fileoverview Realtime spans module exports.
 *
 * This module provides the RealtimeSpans Effect service for accessing
 * the Durable Object cache.
 *
 * Note: RealtimeSpansDurableObject is exported only from server-entry.ts
 * as required by Cloudflare Workers for class discovery.
 */

export {
  RealtimeSpans,
  createSpanCacheKey,
  realtimeSpansLayer,
  setRealtimeSpansLayer,
  type RealtimeSpanExistsInput,
} from "@/workers/realtimeSpans/client";
