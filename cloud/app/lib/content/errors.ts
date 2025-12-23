import { Schema } from "effect";

/**
 * Content-specific error definitions for the content system.
 *
 * These errors are used for:
 * - Build-time content preprocessing (filesystem operations)
 * - Runtime content loading (fetching and processing MDX)
 *
 * They are NOT HTTP/API-scoped and do not have HTTP status codes
 * as they are not returned from API endpoints.
 *
 * Usage:
 * - ContentError: Generic content processing failure
 * - DocumentNotFoundError: Content not found (file or URL)
 * - ContentLoadError: Error reading/parsing content
 * - MetadataValidationError: Missing or invalid frontmatter fields
 */

// =============================================================================
// Content Errors (preprocessing and runtime)
// =============================================================================

/**
 * Generic content processing error.
 * Use for unexpected errors during content preprocessing or runtime loading.
 */
export class ContentError extends Schema.TaggedError<ContentError>()(
  "ContentError",
  {
    message: Schema.String,
    path: Schema.optional(Schema.String),
    cause: Schema.optional(Schema.Unknown),
  },
) {}

/**
 * Document not found.
 * Used when a referenced content file doesn't exist (filesystem or fetch).
 */
export class DocumentNotFoundError extends Schema.TaggedError<DocumentNotFoundError>()(
  "DocumentNotFoundError",
  {
    message: Schema.String,
    path: Schema.String,
  },
) {}

/**
 * Error loading or parsing content.
 * Used when file read or fetch fails, or content parsing encounters an error.
 */
export class ContentLoadError extends Schema.TaggedError<ContentLoadError>()(
  "ContentLoadError",
  {
    message: Schema.String,
    path: Schema.String,
    cause: Schema.optional(Schema.Unknown),
  },
) {}

/**
 * Validation error for content metadata (frontmatter).
 * Thrown when required fields are missing or have invalid formats.
 */
export class MetadataValidationError extends Schema.TaggedError<MetadataValidationError>()(
  "MetadataValidationError",
  {
    message: Schema.String,
    path: Schema.String,
    missingFields: Schema.Array(Schema.String),
  },
) {}
