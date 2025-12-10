/**
 * Metadata Utilities
 *
 * Utility functions for metadata extraction, serialization, and parsing.
 */

import React from "react";
import type { RawMetadata, UnifiedMetadata, MetaTag, LinkTag } from "./types";

/**
 * Extracts metadata from React children
 *
 * @param children React children containing head elements
 * @returns Structured metadata object
 */
export function extractMetadata(children: React.ReactNode): RawMetadata {
  if (!children) {
    return { metaTags: [], linkTags: [], jsonLdScripts: [] };
  }

  let title: string | undefined;
  const metaTags: MetaTag[] = [];
  const linkTags: LinkTag[] = [];
  let description: string | undefined;

  // Define types for the various element props
  type TitleProps = {
    children?: React.ReactNode;
  };

  type MetaProps = {
    name?: string;
    property?: string;
    content?: string;
    httpEquiv?: string;
    charSet?: string;
  };

  type LinkProps = {
    rel?: string;
    href?: string;
    sizes?: string;
    type?: string;
    crossOrigin?: string;
    as?: string;
  };

  // Track JSON-LD scripts
  const jsonLdScripts: string[] = [];

  // Generic props with children
  type ElementProps = {
    children?: React.ReactNode;
  };

  // Helper to process child elements recursively
  const processChild = (child: React.ReactNode) => {
    // Skip null, undefined, and non-element nodes
    if (!child || typeof child !== "object" || !("type" in child)) return;

    // Cast to ReactElement to work with its properties
    const element = child as React.ReactElement;

    // Handle React elements based on type
    if (typeof element.type === "string") {
      switch (element.type.toLowerCase()) {
        case "title":
          const titleProps = element.props as TitleProps;
          if (titleProps?.children) {
            title = titleProps.children as string;
          }
          break;
        case "meta":
          const metaProps = element.props as MetaProps;
          // Extract description specifically
          if (
            metaProps.name === "description" ||
            metaProps.property === "og:description"
          ) {
            description = metaProps.content || "";
          }
          // Add to metaTags collection
          metaTags.push({
            name: metaProps.name,
            property: metaProps.property,
            content: metaProps.content,
            httpEquiv: metaProps.httpEquiv,
            charset: metaProps.charSet,
          });
          break;
        case "link":
          const linkProps = element.props as LinkProps;
          linkTags.push({
            rel: linkProps.rel,
            href: linkProps.href,
            sizes: linkProps.sizes,
            type: linkProps.type,
            crossOrigin: linkProps.crossOrigin,
            as: linkProps.as,
          });
          break;
        case "script":
          // Extract JSON-LD scripts
          const scriptProps = element.props as {
            type?: string;
            children?: React.ReactNode;
          };
          if (
            scriptProps.type === "application/ld+json" &&
            scriptProps.children
          ) {
            // Add to jsonLdScripts collection
            const scriptContent =
              typeof scriptProps.children === "string"
                ? scriptProps.children
                : JSON.stringify(scriptProps.children);
            jsonLdScripts.push(scriptContent);
          }
          break;
      }
    }

    // Process children recursively
    const props = element.props as ElementProps;
    if (props?.children) {
      React.Children.forEach(props.children, processChild);
    }
  };

  // Process all children
  React.Children.forEach(children, processChild);

  return {
    title,
    description,
    metaTags,
    linkTags,
    jsonLdScripts,
  };
}

/**
 * Unifies base and route metadata to create complete metadata
 * Validates the final metadata has required fields
 *
 * @param base Base metadata (site-wide)
 * @param route Route metadata (page-specific)
 * @returns Unified metadata with required fields
 */
export function unifyMetadata(
  base: RawMetadata,
  route: RawMetadata,
): UnifiedMetadata {
  // Route takes precedence for title and description
  const title = route.title || base.title;
  const description = route.description || base.description;

  // Validate required fields
  if (!title) {
    throw new Error("Unified metadata must have a title");
  }

  if (!description) {
    throw new Error("Unified metadata must have a description");
  }

  // Start with base meta tags
  const metaTags = [...base.metaTags];
  const linkTags = [...base.linkTags];
  const jsonLdScripts = [...base.jsonLdScripts];

  // Track existing meta tags by name/property to avoid duplicates
  const existingMetaKeys = new Set(
    base.metaTags.map((tag) => tag.name || tag.property).filter(Boolean),
  );

  // Add route meta tags, avoiding duplicates
  route.metaTags.forEach((tag) => {
    const key = tag.name || tag.property;
    if (key && existingMetaKeys.has(key)) {
      // Replace existing tag with same name/property
      const index = metaTags.findIndex((t) => (t.name || t.property) === key);
      if (index !== -1) {
        metaTags[index] = tag;
      }
    } else if (key) {
      // Add new tag
      metaTags.push(tag);
      existingMetaKeys.add(key);
    } else {
      // Add tags without name/property (like charset)
      metaTags.push(tag);
    }
  });

  // Track existing link tags by rel+href to avoid duplicates
  const existingLinkKeys = new Set(
    base.linkTags.map((link) => `${link.rel}:${link.href}`),
  );

  // Add route link tags, avoiding duplicates
  route.linkTags.forEach((link) => {
    const key = `${link.rel}:${link.href}`;
    if (!existingLinkKeys.has(key)) {
      linkTags.push(link);
      existingLinkKeys.add(key);
    }
  });

  // Combine JSON-LD scripts from route
  if (route.jsonLdScripts) {
    jsonLdScripts.push(...route.jsonLdScripts);
  }

  return {
    title,
    description,
    metaTags,
    linkTags,
    jsonLdScripts,
  };
}

/**
 * Encodes metadata to a base64 string for serialization
 * Works in both browser and Node.js environments
 *
 * @param metadata Metadata to serialize
 * @returns Base64 encoded string
 */
export function serializeMetadata(metadata: RawMetadata): string {
  const jsonString = JSON.stringify(metadata);
  return Buffer.from(jsonString).toString("base64");
}

/**
 * Decodes a base64 string back to metadata
 * Works in both browser and Node.js environments
 *
 * @param serialized Base64 encoded metadata string
 * @returns Parsed metadata object
 */
export function deserializeMetadata(serialized: string): RawMetadata {
  const jsonString = Buffer.from(serialized, "base64").toString("utf-8");
  return JSON.parse(jsonString);
}
