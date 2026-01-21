/**
 * @fileoverview Public exports for analytics services.
 *
 * Provides unified access to analytics functionality. The Analytics service
 * aggregates multiple analytics providers (Google Analytics, PostHog) behind
 * a clean, simple interface.
 *
 * Consumers should only use the Analytics service - the underlying providers
 * are implementation details.
 */

export { Analytics } from "@/analytics/service";
export type {
  AnalyticsConfig,
  AnalyticsService,
  TrackEventParams,
  TrackPageViewParams,
  IdentifyParams,
} from "@/analytics/service";
