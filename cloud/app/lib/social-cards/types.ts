/**
 * Types for social card generation
 */

/**
 * Configuration options for the social images plugin
 */
export interface SocialImagesOptions {
  /** Concurrency limit for image generation (default: 10) */
  concurrency?: number;
  /** WebP quality (0-100, default: 85) */
  quality?: number;
  /** Enable verbose logging (default: false) */
  verbose?: boolean;
}
