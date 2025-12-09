# LLM Documents System Design

## Overview

The LLM Documents system generates concatenated MDX documentation files optimized for consumption by Large Language Models while maintaining human readability. These documents aggregate content from multiple existing documentation sources into coherent, comprehensive documents.

## Goals

- **LLM-Optimized**: Generate comprehensive documentation in formats ideal for LLM context windows
- **Human-Accessible**: Provide web interfaces for browsing and copying LLM-optimized content
- **Maintainable**: Declarative, type-safe configuration that stays in sync with source documentation
- **Flexible**: Support product-specific, section-specific, and cross-product aggregations

## Architecture Overview

### Content Organization


(Out of date: I moved the llms stuff into content/llms and the route to /llms-full, havent updated.)
```
content/docs/
├── _meta.ts                    # Regular documentation structure
├── _llms-meta.ts              # Central registry for all LLM documents
├── llms-full.ts               # Cross-product comprehensive doc
├── mirascope/
│   ├── _meta.ts               # Regular mirascope docs structure  
│   ├── llms-full.ts           # Complete mirascope documentation
│   ├── api/
│   │   ├── llms-full.ts       # Mirascope API documentation only
│   │   └── call.mdx           # Regular doc file
│   └── learn/
│       └── calls.mdx          # Regular doc file
└── lilypad/
    ├── _meta.ts               # Regular lilypad docs structure
    └── llms-full.ts           # Complete lilypad documentation
```

### Route Structure

Each LLM document generates two routes:
- **Raw content**: `/docs/path/to/document.txt` - Direct text file for LLM consumption
- **Human viewer**: `/docs/path/to/document` - Web interface with copy functionality

Examples:
- `/docs/llms-full.txt` + `/docs/llms-full` (cross-product)
- `/docs/mirascope/llms-full.txt` + `/docs/mirascope/llms-full` (product-specific)
- `/docs/mirascope/api/llms-full.txt` + `/docs/mirascope/api/llms-full` (section-specific)

## Core Types and Interfaces

### LLM Document Definition

```typescript
interface LLMDocument {
  metadata: {
    slug: string;           // URL slug (becomes filename)
    title: string;          // Human-readable title
    description: string;    // Document description
  };
  
  sections: LLMDocSection[];
}

interface LLMDocSection {
  title: string;              // Section heading
  content?: string;           // Optional intro content for the section
  includes: IncludeDirective[]; // Content to aggregate
}

interface IncludeDirective {
  type: 'exact' | 'glob' | 'wildcard';
  pattern: string;            // Path pattern to match
}
```

### Central Registry

```typescript
// content/docs/_llms-meta.ts
export interface LLMDocRegistry {
  documents: LLMDocument[];
}
```

## Content Inclusion System

### Include Types

1. **Exact Match**: `include.exact('mirascope/index.mdx')`
   - Includes a specific document
   - Type-safe path validation

2. **Glob Pattern**: `include.glob('mirascope/learn/*.mdx')`
   - Includes direct children only (no subdirectories)
   - Maintains order from `_meta.ts`

3. **Wildcard**: `include.wildcard('lilypad/*')`
   - Includes all content recursively
   - Maintains hierarchical order from `_meta.ts`


## Template Definition DSL

### Basic Example

```typescript
// content/docs/mirascope/llms-full.ts
import { defineLLMDocument, include } from '@/src/lib/content/llm-documents';

export default defineLLMDocument({
  metadata: {
    slug: 'llms-full',
    title: 'Complete Mirascope Documentation',
    description: 'Comprehensive documentation for building AI applications with Mirascope',
  },
  
  sections: [
    {
      title: 'Getting Started',
      content: `
# Getting Started

Core concepts and quickstart guide for Mirascope.
      `,
      includes: [
        include.exact('mirascope/index.mdx'),
        include.exact('mirascope/guides/getting-started/quickstart.mdx'),
      ]
    },
    {
      title: 'Learning Mirascope',
      content: `
# Learning Mirascope

In-depth guides for all framework features.
      `,
      includes: [
        include.glob('mirascope/learn/*.mdx'),
      ]
    },
    {
      title: 'API Reference',
      includes: [
        include.wildcard('mirascope/api/*'),
      ]
    }
  ],
});
```

## Build Process Integration

### Preprocessing Pipeline

1. **Content Preprocessing**: Regular docs are processed first
2. **LLM Doc Discovery**: Scan for `**/llms-*.ts` files
3. **Template Processing**: Process each LLM document template
4. **Output Generation**: Write `.txt` files to appropriate locations
5. **Route Registration**: Register viewer routes for each LLM document

### File Output

Generated txt files are placed where they will be automatically available as raw content:
- `public/docs/llms-full.txt`
- `public/docs/mirascope/llms-full.txt`
- `public/docs/mirascope/api/llms-full.txt`

For the human-readable display, we will also output the content, likely as json under `public/static/content/docs` for consistency. However, that part of the system has yet to be fleshed out.

## Human Viewer Interface

Each LLM document gets a corresponding viewer page with:

- **Document metadata**: Title, description, last updated
- **Content preview**: Formatted MDX rendering
- **Copy functionality**: One-click copy of raw content
- **Download option**: Save as `.txt` file
- **Table of contents**: Navigate through sections
- **Source links**: Links to individual source documents

## Error Handling and Validation

### Build-Time Validation

- **Reference validation**: All include patterns must resolve to existing documents
- **Circular dependency detection**: Prevent infinite inclusion loops
- **Content size limits**: Warn on documents exceeding reasonable token limits
- **Duplicate detection**: Warn on content included multiple times

### Runtime Error Handling

- **Graceful degradation**: Continue processing other templates if one fails
- **Detailed error messages**: Clear indication of what failed and why
- **Content freshness**: Track when source documents change

## Integration with Existing Systems

### Content System Integration

- **Leverages existing doc registry**: Uses `getAllDocInfo()` for content discovery
- **Respects doc ordering**: Maintains order defined in `_meta.ts` files
- **Uses standard content loading**: Integrates with existing content pipeline

### Route System Integration

- **Standard route generation**: LLM document routes work like regular doc routes
- **SEO integration**: Generated routes include proper metadata
- **Sitemap inclusion**: LLM documents appear in sitemap