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
import { mdx } from "@/../content/docs/v1/placeholder.mdx";

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
import { blogMetadata, docsMetadata, policyMetadata, devMetadata } from "virtual:content-meta";

// blogMetadata: BlogMeta[] - blog posts sorted by date (newest first)
// docsMetadata: DocMeta[] - documentation pages
// policyMetadata: PolicyMeta[] - policy pages
// devMetadata: DevMeta[] - dev pages

blogMetadata.forEach(post => {
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
4. Use `blogMetadata`, `docsMetadata`, etc. to list and query content

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

Generates a production `robots.txt` from the sitemap, disallowing low-priority URLs. The sitemap is generated during prerendering and only included entries have a `changefreq` tag. Entries without `changefreq` will be disallowed.

### Features

- **Sitemap-driven**: Reads the generated `sitemap.xml` after build
- **Selective disallow**: URLs without a `<changefreq>` tag are disallowed (not included in prerender, considered low-priority)
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

## Social Cards Plugin (`social-cards.ts`)

Generates Open Graph / Twitter card images for all content pages.

### Features

- **ContentProcessor-driven**: Gets routes and titles from the shared ContentProcessor instance
- **Worker thread pool**: Uses Piscina for true CPU parallelism across worker threads
- **Satori rendering**: Uses Satori to convert JSX templates to SVG
- **High-quality output**: Converts SVG → PNG (resvg-js) → WebP (Sharp)
- **Branded design**: Uses Williams Handwriting font on the homepage light background
- **Static page support**: Configurable titles for non-content routes (home, pricing, etc.)

### How It Works

1. After the build completes, the plugin initializes the ContentProcessor
2. It collects all routes from content metadata plus static page titles
3. A worker thread pool is created with one thread per CPU core (minus one for main thread)
4. Each worker loads font/background assets once, then renders assigned cards
5. Cards are converted to WebP and written to `dist/client/social-cards/`

### Output

Social card images are generated at `dist/client/social-cards/{route}.webp`:

- `/blog/my-post` → `social-cards/blog-my-post.webp`
- `/docs/v1/learn/intro` → `social-cards/docs-v1-learn-intro.webp`
- `/` → `social-cards/index.webp`

### Configuration

The Vite plugin accepts a shared `ContentProcessor` instance:

```typescript
viteSocialCards({
  processor,  // ContentProcessor instance (required)
})
```

The `SocialCardGenerator` class (used internally or standalone) accepts additional options:

```typescript
new SocialCardGenerator({
  processor,        // ContentProcessor instance (required)
  outputDir,        // Output directory (required)
  staticTitles,     // Static page titles for non-content routes (optional)
  concurrency,      // Max worker threads (default: CPU cores - 1)
  quality: 85,      // WebP quality 0-100 (default: 85)
  verbose: false,   // Enable detailed logging (default: false)
})
```

Default static titles are provided for common routes:

```typescript
{
  "/home": "Mirascope",
  "/pricing": "Pricing",
  "/docs": "Documentation",
  "/blog": "Blog",
}
```

### Template

The social card rendering is located at `app/lib/social-cards/render.ts`. It renders:

- **Background**: Light gradient background
- **Title**: Page title in Williams Handwriting font (72px, dark color)
- **Dimensions**: 1200×630 pixels (standard OG image size)

### Dependencies

The plugin uses:

- `piscina` - Worker thread pool for true CPU parallelism
- `satori` - JSX to SVG rendering (Vercel)
- `@resvg/resvg-js` - High-quality SVG to PNG conversion (Rust-based)
- `sharp` - PNG to WebP conversion (already used by images plugin)

Helper modules are in `app/lib/social-cards/`:

- `render.ts` - Render pipeline (Satori → resvg → Sharp) and asset loading
- `types.ts` - Type definitions for social card options

The worker implementation is in `vite-plugins/social-cards-worker.ts`.

### SEO Integration

Social card URLs are automatically included in page metadata via `app/lib/seo/head.ts`:

- `og:image` - Open Graph image for Facebook, LinkedIn, etc.
- `twitter:image` - Twitter card image
- `twitter:card` - Set to `summary_large_image` for large preview

### Build-time vs Runtime

- **Development**: No social images are generated; missing images will 404
- **Production**: All content pages get social card images generated at build time

### Error Handling

- Missing title: Falls back to generating title from URL path (e.g., `/docs/v1/learn` → "Docs V1 Learn")
- Individual failures: Logged as errors, other images continue generating
- Empty routes: Plugin logs and returns early with zero results

## Pagefind Dev Plugin (`pagefind-dev.ts`)

Serves Pagefind search index files during development mode.

### Features

- __Dev server middleware__: Intercepts requests to `/_pagefind/` and serves files from the build output
- **MIME type handling**: Correctly sets Content-Type headers for all Pagefind file types
- **Query parameter support**: Handles timestamp-suffixed requests for `pagefind-entry.json`
- **Graceful 404s**: Returns 404 for missing files without crashing the server

### How It Works

Pagefind generates its search index into `dist/client/_pagefind/` during the build process. In development, the Vite dev server doesn't serve from `dist/`, so this plugin provides middleware to:

1. Intercept any request starting with `/_pagefind/`
2. Resolve the corresponding file in `dist/client/_pagefind/`
3. Set the appropriate Content-Type header based on file extension
4. Serve the file contents or return 404 if not found

### Supported File Types

| Extension | Content-Type |
|-----------|--------------|
| `.js` | `application/javascript; charset=utf-8` |
| `.json` | `application/json` |
| `.css` | `text/css` |
| `.wasm` | `application/wasm` |
| `.pf_meta` | `application/octet-stream` |
| Other | `text/plain` |

### Build-time vs Runtime

- __Development__: Middleware serves Pagefind files from `dist/client/_pagefind/`. Requires running a build first to generate the index.
- **Production**: Pagefind files are served directly from the static build output. Middleware is not used.

### Prerequisites

The Pagefind index must exist in `dist/client/_pagefind/` for search to work in development. Run a build first:

```bash
bun run build
```

Then start the dev server. The search functionality will use the pre-built index.
