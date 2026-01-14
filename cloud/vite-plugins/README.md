# Vite Plugins

Custom Vite plugins for the Mirascope Cloud application.

## MDX Plugin (`mdx.ts`)

Transforms `.mdx` files into importable ES modules at build time.

### Features

- **Frontmatter parsing**: Extracts YAML frontmatter from MDX files
- **Table of contents generation**: Automatically generates TOC from headings
- **MDX compilation**: Compiles MDX to JSX using `@mdx-js/mdx`
- **Syntax highlighting**: Code blocks styled with `rehype-pretty-code` (Shiki)
- **Hot Module Replacement**: Full HMR support in development mode

### Usage

Import MDX files directly in your components:

```typescript
import { mdx } from "@/content/docs/v1/placeholder.mdx";

// mdx is a React component with metadata attached
console.log(mdx.frontmatter.title); // Access frontmatter
console.log(mdx.tableOfContents); // Access TOC
<mdx />; // Render the component
```

### MDX File Format

```mdx
---
title: Getting Started
description: Learn how to use Mirascope
---

# Getting Started

Your content here...
```

For blog posts, include additional frontmatter:

```mdx
---
title: My Blog Post
description: A description of the post
date: "2024-01-15"
author: "Author Name"
readTime: "5 min read"
---
```

### Build-time vs Runtime

- **Development**: Files are compiled on-demand with HMR
- **Production**: Files are pre-compiled during the Vite build step
- **Pre-rendering**: MDX content is included in pre-rendered static HTML

### Type Safety

TypeScript types are provided in:
- `app/types/mdx.d.ts` - types for MDX imports

## Content Plugin (`content.ts`)

Scans the content directory and maintains metadata about all MDX files for listing and querying.

### Features

- **Directory scanning**: Scans `content/` on startup with parallel processing
- **Metadata extraction**: Builds metadata for all MDX files (title, description, slug, route, etc.)
- **Virtual module**: Exposes meta via `virtual:content-meta`
- **Hot Module Replacement**: Meta is automatically updated when files change

### Usage

Access content metadata via the virtual module:

```typescript
// @ts-expect-error - virtual module resolved by vite plugin
import { blogPosts, allContent } from "virtual:content-meta";

// blogPosts: BlogMeta[] - blog posts sorted by date (newest first)
// allContent: ContentMeta[] - all MDX content entries

blogPosts.forEach(post => {
  console.log(post.title, post.date, post.route);
});
```

### Content Types

The plugin recognizes content types based on directory structure:
- `content/blog/` → type: "blog"
- `content/docs/` → type: "docs"
- `content/policy/` → type: "policy"
- `content/dev/` → type: "dev"

### Blog Metadata

Blog posts include additional fields:
- `date`: Publication date
- `author`: Author name
- `readTime`: Estimated reading time
- `lastUpdated`: Last update date

### Adding New Content

1. Create a new `.mdx` file in the appropriate `content/` subdirectory
2. Add frontmatter with required fields
3. The meta is automatically updated during development (HMR)
4. Use `blogPosts` or `allContent` to list and query content

### Type Safety

TypeScript types are provided in:
- `app/types/virtual-content-meta.d.ts` - types for the virtual module
- `app/lib/content/types.ts` - `ContentMeta` and `BlogMeta` interfaces

## Images Plugin (`images.ts`)

Provides WebP image processing for both development and production builds.

### Features

- **On-demand processing**: Images converted to WebP only when requested (development)
- **Build-time generation**: Responsive variants auto-generated for all images during build
- **Path-specific configs**: Different quality/sizes for backgrounds vs other images
- **WebP validation**: Build fails if any PNG/JPG files are found in dist
- **Skip patterns**: Configurable patterns to exclude from processing
- **In-memory caching**: Processed images cached in memory for fast subsequent requests
- **Source format detection**: Automatically finds source images (.webp, .png, .jpg, .jpeg)

### Configuration

The plugin uses the following configuration:

| Setting | Value | Description |
|---------|-------|-------------|
| `baseDir` | `public/assets` | Base directory for all assets (scanned recursively) |
| `distAssetsDir` | `dist/client/assets` | Output directory to validate after build |
| `skipPatterns` | `[]` | Regex patterns to exclude from processing |

### Path-specific Configuration

The plugin uses different settings based on image path:

| Path Pattern | Quality | Medium | Small |
|--------------|---------|--------|-------|
| `/backgrounds/` | 95% | 1200px | 800px |
| All other images | 80% | 1024px | 640px |

### Usage

Request optimized images by URL pattern:

- `/assets/hero.webp` - Original size as WebP
- `/assets/hero-medium.webp` - Medium width variant
- `/assets/hero-small.webp` - Small width variant

The plugin looks for source images in `public/` and processes them on-the-fly during development.

### Build-time vs Runtime

- **Development**: Middleware intercepts all WebP requests and processes images on-demand with in-memory caching. Static files on disk are ignored — the middleware always takes priority.
- **Production**: Responsive variants (`-medium`, `-small`) are generated for all images in `public/assets/` at build start, then copied to `dist/` with other assets. No middleware runs in production.

### WebP Validation

After the build completes, the plugin scans `dist/client/assets/` and **fails the build** if any `.png`, `.jpg`, or `.jpeg` files are found. This ensures all images are WebP format in production.

SVG and GIF files are allowed (they're valid non-raster or animated formats).

## Robots Plugin (`robots.ts`)

Generates a production `robots.txt` from the sitemap, disallowing low-priority URLs.

### Features

- **Sitemap-driven**: Reads the generated `sitemap.xml` after build
- **Selective disallow**: URLs without a `<changefreq>` tag are disallowed (considered low-priority)
- **Post-build generation**: Runs after sitemap generation to ensure sitemap exists
- **Environment-aware**: Different behavior for development vs production

### How It Works

1. After the build completes, the plugin reads `dist/client/sitemap.xml`
2. It parses all `<url>` entries and identifies those without a `<changefreq>` tag
3. URLs without `changefreq` are added as `Disallow` rules in robots.txt
4. The generated `robots.txt` is written to `dist/client/robots.txt`

The logic assumes that URLs with `changefreq` are high-value pages (docs, blog posts) that should be crawled, while URLs without it (app routes, utility pages) should be excluded from search engines.

### Build-time vs Runtime

- **Development**: `public/robots.txt` is served directly (permissive, allows all)
- **Production**: `dist/client/robots.txt` is generated with selective disallow rules

### Generated Output Example

```txt
# robots.txt for https://mirascope.com
User-agent: *
Allow: /
Disallow: /dashboard
Disallow: /settings
Disallow: /api/health

Sitemap: https://mirascope.com/sitemap.xml
```

### Dependencies

The plugin uses helper functions from `app/lib/robots.ts`:
- `parseSitemapForUrlsWithoutChangefreq()` - Extracts URLs without changefreq from sitemap XML
- `generateRobotsTxt()` - Generates the robots.txt content string

### Error Handling

The plugin will **fail the build** if:
- The sitemap file does not exist at `dist/client/sitemap.xml`

This ensures the sitemap plugin runs before the robots plugin.
