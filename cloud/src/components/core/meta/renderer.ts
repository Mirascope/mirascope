/**
 * Metadata Renderer
 *
 * Shared utilities for metadata rendering in both client and server environments.
 * Uses DOM elements as the source of truth, with an optional serialization step for SSG.
 */

import type { UnifiedMetadata, MetaTag, LinkTag } from "./types";

/**
 * Creates a DOM element with attributes from a tag object
 * Works in both browser and server (via HappyDOM) environments
 */
export function createMetaElement(tag: MetaTag): HTMLMetaElement {
  const element = document.createElement("meta");

  // Apply all defined attributes
  Object.entries(tag)
    .filter(([_, value]) => value !== undefined)
    .forEach(([key, value]) => {
      // Convert camelCase to kebab-case for attributes
      const attrName = key.replace(/([A-Z])/g, "-$1").toLowerCase();
      element.setAttribute(attrName, value as string);
    });

  return element;
}

/**
 * Creates a DOM element for a link tag
 */
export function createLinkElement(tag: LinkTag): HTMLLinkElement {
  const element = document.createElement("link");

  Object.entries(tag)
    .filter(([_, value]) => value !== undefined)
    .forEach(([key, value]) => {
      const attrName = key.replace(/([A-Z])/g, "-$1").toLowerCase();
      element.setAttribute(attrName, value as string);
    });

  return element;
}

/**
 * Creates a DOM element for the title
 */
export function createTitleElement(title: string): HTMLTitleElement {
  const element = document.createElement("title");
  element.textContent = title;
  return element;
}

/**
 * Converts a DOM element to its HTML string representation
 */
export function elementToString(element: Element): string {
  if (element.tagName.toLowerCase() === "title") {
    return `<title>${element.textContent}</title>`;
  }

  // For self-closing tags like meta and link
  let html = `<${element.tagName.toLowerCase()}`;

  // Add attributes
  for (let i = 0; i < element.attributes.length; i++) {
    const attr = element.attributes[i];
    html += ` ${attr.name}="${attr.value}"`;
  }

  html += ">";
  return html;
}

/**
 * Creates a script element for JSON-LD data
 */
export function createScriptElement(content: string): HTMLScriptElement {
  const element = document.createElement("script");
  element.setAttribute("type", "application/ld+json");
  element.textContent = content;
  return element;
}

/**
 * Creates all metadata DOM elements for the given unified metadata
 */
export function createMetadataElements(metadata: UnifiedMetadata) {
  // Create title element
  const titleElement = createTitleElement(metadata.title);
  titleElement.setAttribute("data-head-manager", "true");

  // Create meta elements
  const metaElements = metadata.metaTags.map((tag) => {
    const element = createMetaElement(tag);
    element.setAttribute("data-head-manager", "true");
    return element;
  });

  // Create link elements
  const linkElements = metadata.linkTags.map((tag) => {
    const element = createLinkElement(tag);
    element.setAttribute("data-head-manager", "true");
    return element;
  });

  // Create JSON-LD script elements if present
  const scriptElements = (metadata.jsonLdScripts || []).map((content) => {
    const element = createScriptElement(content);
    element.setAttribute("data-head-manager", "true");
    return element;
  });

  return {
    title: titleElement,
    meta: metaElements,
    link: linkElements,
    script: scriptElements,
  };
}

/**
 * Generates HTML strings for all metadata elements
 * Used in static site generation
 */
export function generateMetadataHtml(metadata: UnifiedMetadata) {
  const elements = createMetadataElements(metadata);

  return {
    title: elementToString(elements.title),
    meta: elements.meta.map(elementToString).join("\n"),
    link: elements.link.map(elementToString).join("\n"),
    script: elements.script
      .map((script) => {
        return `<script type="application/ld+json">${script.textContent}</script>`;
      })
      .join("\n"),
  };
}

/**
 * Updates document head with metadata
 * Used in client-side rendering
 * NOTE: This is a placeholder for future implementation
 */
export function updateDocumentHead(metadata: UnifiedMetadata) {
  const elements = createMetadataElements(metadata);

  // Set document title
  document.title = metadata.title;

  // Remove existing managed meta tags
  document
    .querySelectorAll('meta[data-managed="true"]')
    .forEach((el) => el.remove());

  // Add new meta tags
  elements.meta.forEach((element) => {
    element.setAttribute("data-managed", "true");
    document.head.appendChild(element);
  });

  // Remove existing managed link tags
  document
    .querySelectorAll('link[data-managed="true"]')
    .forEach((el) => el.remove());

  // Add new link tags
  elements.link.forEach((element) => {
    element.setAttribute("data-managed", "true");
    document.head.appendChild(element);
  });
}
