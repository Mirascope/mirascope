/**
 * Metadata System Types
 *
 * This file contains types for the metadata management system.
 */

/**
 * Base type for meta tags
 */
export type MetaTag = {
  name?: string;
  property?: string;
  content?: string;
  httpEquiv?: string;
  charset?: string;
  // Other meta attributes as needed
};

/**
 * Base type for link tags
 */
export type LinkTag = {
  rel?: string;
  href?: string;
  sizes?: string;
  type?: string;
  crossOrigin?: string;
  as?: string;
  // Other link attributes as needed
};

/**
 * Raw metadata extracted from components
 * Does not require title or description
 */
export type RawMetadata = {
  title?: string;
  description?: string;
  metaTags: MetaTag[];
  linkTags: LinkTag[];
  jsonLdScripts: string[]; // JSON-LD script contents
};

/**
 * Complete, unified metadata structure
 * Required fields for final output
 */
export type UnifiedMetadata = {
  title: string; // Required
  description: string; // Required
  metaTags: MetaTag[];
  linkTags: LinkTag[];
  jsonLdScripts: string[]; // JSON-LD script contents
};

/**
 * Internal Type for Serialized Metadata
 */
export interface SerializedMetadata {
  base64: string;
}
