# Metadata System Design

This document outlines the architecture and design of the site-wide metadata management system.

## Overview

The metadata system provides a unified approach to managing document `<head>` content across the site, solving several key challenges:

1. Moving metadata out of the React component tree and into the document's canonical `<head>`
2. Ensuring consistency between server-side generated metadata and client-side updates
3. Providing a clean, JSX-based API for declaring metadata
4. Supporting both core (site-wide) and route-specific metadata
5. Validating metadata presence during build time

## Components

### BaseMeta

`BaseMeta` is the shared base implementation that both CoreMeta and RouteMeta inherit from. It handles:

- Serialization of metadata during prerendering
- Integration with HeadManager during client-side rendering
- Extraction of metadata from JSX children

This is an internal component not meant to be used directly.

### CoreMeta

`CoreMeta` defines site-wide metadata that remains consistent across all pages:

- Character encoding, viewport settings
- Favicon definitions
- Font preloading
- Web manifest links
- Other global meta tags

This component is used once in the root layout of the application.

### RouteMeta

`RouteMeta` defines page-specific metadata that changes with each route:

- Page title
- Description
- Open Graph/social sharing metadata
- Structured data
- Other route-specific meta tags

This component is used once per route.

### PageMeta

`PageMeta` is a higher-level component that uses `RouteMeta` internally, providing a convenient props-based API for common page metadata patterns including SEO and social sharing tags.

## Client-Side Implementation

In the browser:

1. Both `CoreMeta` and `RouteMeta` render nothing in the DOM
2. On mount, they call `HeadManager` to update the document's `<head>`
3. On prop changes, they trigger head updates with new metadata
4. The HeadManager handles removing previous tags and adding new ones

## Server-Side Implementation

During static site generation (SSG):

1. `CoreMeta` and `RouteMeta` render invisible div elements with serialized metadata
2. The build process validates exactly one of each exists
3. The build process extracts metadata from these divs
4. The extracted metadata is used to inject proper tags into the document `<head>`
5. The invisible divs are removed from the final HTML

## System Flow

The system works through these key interactions:

1. **Component Declaration**: `CoreMeta` and `RouteMeta` components declare metadata via JSX
2. **Serialization**: During SSG, metadata is serialized to JSON and base64 encoded in hidden divs
3. **Extraction**: Build process extracts and validates the serialized metadata
4. **Injection**: Extracted metadata is injected into the document head in the final HTML
5. **Client Hydration**: On the client, components update the document head via `HeadManager`
6. **Navigation**: On client-side navigation, route-specific metadata updates while core metadata remains

## Implementation Details

### Metadata Serialization

Metadata is serialized to a JSON structure and base64 encoded to avoid HTML escaping issues:

```typescript
// Base types for different tag types
type MetaTag = {
  name?: string;
  property?: string;
  content: string;
  httpEquiv?: string;
  // Other meta attributes
};

type LinkTag = {
  rel: string;
  href: string;
  sizes?: string;
  type?: string;
  crossOrigin?: string;
  // Other link attributes
};

// Complete metadata structure
type Metadata = {
  title: string;  // Required 
  description: string; // Required
  metaTags: MetaTag[];
  linkTags: LinkTag[];
  // Could add other specialized tag types as needed
};
```

### Head Manager

The `HeadManager` is responsible for:

1. Maintaining the current state of both base and route metadata
2. Merging them to create a complete head representation
3. Efficiently updating the document.head with minimal DOM operations
4. Handling special cases like title updates and duplicate prevention

### Build Process Integration

The build process:

1. Validates metadata presence and uniqueness
2. Extracts metadata from rendered HTML
3. Injects it into the canonical `<head>`
4. Removes the serialization divs from the final HTML output

## Usage Examples

### Basic Usage

```jsx
// In root layout:
<CoreMeta>
  <meta charSet="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <link rel="icon" href="/favicon.png" />
</CoreMeta>

// In a route component:
<RouteMeta>
  <title>Product Page | Mirascope</title>
  <meta name="description" content="Description of the product" />
  <meta property="og:title" content="Product Page | Mirascope" />
</RouteMeta>

// Or more commonly, using PageMeta:
<PageMeta 
  title="Product Page"
  description="Description of the product"
  type="website"
  product="mirascope"
/>
```

## Design Considerations

1. **Metadata Structure**: Title and description are required fields in the metadata structure, ensuring every page has these critical SEO elements.

2. **Serialization Approach**: Base64 encoding is used to avoid HTML escaping issues with quotes and special characters in metadata.

3. **Component Splitting**: `CoreMeta` and `RouteMeta` are separate components to enforce the "exactly one of each" rule and make validation clearer.

4. **Validation**: The build process strictly validates metadata presence to ensure good SEO practices across the site.

5. **JSX-based API**: The system uses JSX syntax for metadata to maintain the familiar React mental model for developers.

6. **SSR Compatibility**: The design works in both client and server environments, ensuring consistent metadata handling.

7. **Tag Specialization**: Different tag types (meta, link, etc.) have specialized handling for better type safety and clearer code organization.