/**
 * Types for social card generation
 */

/**
 * Props for the social card template component
 */
export interface SocialCardProps {
  /** The page title/headline to display */
  title: string;
  /** Base64 data URL of the background image */
  backgroundImage: string;
}

/**
 * Metadata for a page that needs a social card
 */
export interface PageMeta {
  /** URL path (e.g., "/blog/my-post") */
  route: string;
  /** Page title */
  title: string;
}

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
