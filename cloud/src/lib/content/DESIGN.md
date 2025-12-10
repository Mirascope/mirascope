# Content System Design

## Table of Contents
- [Overview](#overview)
- [File Structure & Key Components](#file-structure--key-components)
  - [Unified Content Service](#unified-content-service-contentts)
  - [Core Types](#core-types-contentts)
  - [Environment Utilities](#environment-environmentts)
  - [Document Specification](#document-specification-spects)
- [Data Flow](#data-flow)
  - [Build-time Content Preparation](#build-time-content-preparation)
  - [Runtime Content Loading](#runtime-content-loading)
  - [Server Side Generation](#server-side-generation)
- [Error Handling](#error-handling)
- [Caching Strategy](#caching-strategy)
- [MDX Processing](#mdx-processing)
- [Common Tasks](#common-tasks)

## Overview

This document outlines the architecture of the unified content system for handling docs, blog posts, and policy pages in the Mirascope website.

A general overview:
- All content is stored as MDX files with frontmatter. The MDX has access to custom components defined in MDXProvider.tsx.
- Content is organized in the root `/content/` directory, subdivided by type (`content/docs`, `content/policy`, `content/blog`, `content/dev`).
- Blog posts are automatically included in the blog index, but docs must be manually incorporated by editing the `_meta.ts` files which contain the doc content specification. This spec also defines the layout for docs in the sidebar.
- At build time, all content is processed into JSON files with extracted metadata.


## File Structure & Key Components

The system is organized with a centralized content service and shared utilities:

```
src/lib/content/
  ├── content.ts              # Unified content service for all content types
  ├── environment.ts          # Environment detection utilities
  ├── index.ts                # Public API exports
  ├── mdx-processing.ts       # MDX processing and frontmatter parsing
  ├── preprocess.ts           # Build-time content preprocessing
  ├── spec.ts                 # Doc specification types and processing
```

Each component is focused on its specific responsibility:

### Unified Content Service (content.ts)

The content service provides a centralized API for accessing all content types:

- Contains all content type definitions
- Implements content loading and metadata retrieval functions
- Organized into logical sections for each content type (blog, docs, policy)
- Provides strongly-typed functions for each content domain
- Includes error handling logic

```typescript
// Blog content functions
export async function getBlogContent(slug: string): Promise<BlogContent>;
export async function getAllBlogMeta(): Promise<BlogMeta[]>;

// Doc content functions
export async function getDocContent(path: string): Promise<DocContent>;
export function getAllDocMeta(): DocMeta[];

// Policy content functions
export async function getPolicy(path: string): Promise<PolicyContent>;
export async function getAllPolicyMeta(): Promise<PolicyMeta[]>;
```

### Core Types (content.ts)

Defines the foundational types used throughout the content system:

```typescript
// Core content type enum
export type ContentType = "docs" | "blog" | "policy" | "dev";

// Base metadata interface
export interface ContentMeta {
  title: string;
  description: string;
  path: string;
  slug: string;
  type: ContentType;
}

// Type-specific metadata extensions
export interface DocMeta extends ContentMeta {
  product: string;
}

export interface BlogMeta extends ContentMeta {
  date: string;
  author: string;
  readTime: string;
  lastUpdated: string;
}

// Base content interface with metadata plus content
export interface Content<T extends ContentMeta = ContentMeta> {
  meta: T; // Typed, validated metadata
  content: string; // Raw MDX with frontmatter stripped
  
  // MDX structure expected by components
  mdx: {
    code: string;
    frontmatter: Record<string, any>;
  };
}
```

### Environment (environment.ts)

Provides environment detection and fetch utilities:

This is important because we use the same codepaths for loading content both on the frontend and for pre-rendering during SSG.

During SSG, it's important to use `environment.onError` to inform the build system when an error has occurred during prerendering.

```typescript
/**
 * Environment utilities for content loading system
 */
export const environment = {
  isDev: () => import.meta.env?.DEV ?? false,
  isProd: () => import.meta.env?.PROD ?? false,
  getMode: () => (import.meta.env?.DEV ? "development" : "production"),
  fetch: (...args: Parameters<typeof fetch>) => fetch(...args),
  onError: (error: Error) => {
    console.error(error);
  },
};
```

### Document Specification (spec.ts)

Provides types and utilities for working with the structured documentation.

This is used to set up the document structure in the sidebar layout of the docs sidebar.
Doc content will only be included in the site if it is listed in the `content/docs/_meta.ts` file.

```typescript
// Types for document structure
export interface DocSpec {
  slug: Slug;
  label: string;
  children?: DocSpec[];
}

export interface SectionSpec {
  slug: Slug;
  label: string;
  children: DocSpec[];
}

export interface ProductSpec {
  sections: SectionSpec[];
}

// Processing and validation functions
export function processDocSpec(docSpec: DocSpec, product: string, pathPrefix: string): DocMeta[];
export function validateDocSpec(spec: DocSpec): ValidationResult;
```

## Data Flow

### Build-time Content Preparation

During the build process:

1. The `preprocessContent` function from `preprocess.ts` is invoked
2. For each content type (blog, doc, policy, dev):
   - MDX files are discovered using glob patterns
   - Frontmatter is extracted from each file
   - Metadata is validated for required fields based on content type
   - Content and metadata are saved as JSON files in `public/static/content/{type}/{path}.json`
   - Metadata indices are created and saved in `public/static/content-meta/{type}/index.json`
3. The build will fail if:
   - Any required metadata field is missing
   - Date formats are invalid
   - Filenames don't follow URL-friendly slug rules

We do not validate the MDX content itself at build time to ensure fast server startup. However, if there are issues with the MDX content, they will be caught during the SSG (prerendering) process.

### Runtime Content Loading

At runtime, when a route is accessed:

1. TanStack Router calls the route loader function for the route
2. The loader calls the appropriate content function (e.g., `getBlogContent`)
3. The content function calls the unified `loadContent` function with the content type
4. The `loadContent` function:
   - Resolves the content path using `resolveContentPath`
   - Fetches the JSON file using `environment.fetch`
   - Extracts the raw content and metadata
   - Processes the MDX content using `processMDXContent`
   - Returns the complete `Content` object
5. The React component receives the loader data through `useLoaderData`
6. The component renders the content using the MDX renderer component

### Server Side Generation

The site uses Static Site Generation (SSG) to prerender every route:

1. During the build, each route is prerendered by executing its loader
2. The loader fetches all necessary content and processes it
3. The prerendered HTML is saved for each route
4. If any errors occur during prerendering, the build will fail

TanStack Router tends to suppress errors by default. To ensure the build is aware of any errors during prerendering, wire the route's `onError` handler to the `environment.onError` function when adding new routes.

## Error Handling

The content system uses a structured approach to error handling:

1. **Specific Error Types**:
   - `ContentError` - Base error class for all content-related errors
   - `DocumentNotFoundError` - Specific error for 404-like situations
   - `ContentLoadError` - Specific error for content loading failures

2. **Consistent Error Processing**:
   - The `handleContentError` function takes any error and wraps it in the appropriate typed error
   - 404-like errors are automatically detected and converted to `DocumentNotFoundError`
   - All errors include content type and path information for better debugging

3. **Error Propagation**:
   - Errors from loader functions are caught by TanStack Router
   - During SSG, errors will cause the build to fail, preventing broken content from being published
   - At runtime, errors are displayed using error boundary components

## Caching Strategy

TanStack Router provides built-in caching:

- Results from loader functions are cached automatically
- Cache invalidation is handled by TanStack Router
- Concurrent requests for the same content are deduped

## MDX Processing

The MDX processing pipeline:

1. Raw content with frontmatter is stored in JSON files
2. When content is loaded, frontmatter is extracted using `parseFrontmatter`
3. MDX is processed using the `next-mdx-remote/serialize` library
4. The processed content includes:
   - Clean content with frontmatter removed
   - Parsed frontmatter object
   - Compiled MDX code for rendering
5. The MDXRenderer component uses this processed content for rendering

## Testing

We do not have much unit test coverage, although the fact that we pre-render every route provides some assurances:
if the build succeeds, then the site is likely in good shape.

If you make a change to the content system and wish to test it, you can do the following:
- Use `bun run start` to test the dev build. Try looking at one of every content type (e.g. docs index, a docs page, blog index, a blog page, and one of the policy pages).
- Use `bun run build && bun run serve` to test the prod build. `bun run build` will prerender every page which is a comprehensive check that all routes are okay.

## Common Tasks


### Adding a New Document to the Docs

1. Create a new MDX file in the appropriate location in `content/docs/`
2. Include required frontmatter: title, description
3. Add an entry for the document in the appropriate `_meta.ts` file
4. If adding a new section, include it in the product's section array

### Creating a New Blog Post

1. Create a new MDX file in `content/blog/`
2. Include required frontmatter: title, description, date, author, readTime
3. The post will be automatically included in the blog index
4. Blog images should be added in `public/assets`

### Adding a New Content Type

To add a new content type:

1. Add the new type to the `ContentType` union and `CONTENT_TYPES` array in `content.ts`
2. Create a new type-specific metadata interface extending `ContentMeta`
3. Add a new type-specific content type using the `Content` generic
4. Add functions for loading content and metadata for the new type
5. Update `preprocess.ts` to handle the new content type
6. Create the corresponding directory in `content/`