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
import { mdx } from "@/content/docs/v1/getting-started.mdx";

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

### Adding New MDX Files

1. Create a new `.mdx` file in `content/docs/v1/`
2. Add frontmatter (optional but recommended)
3. Import and use it in your route components
4. The plugin automatically handles compilation and metadata extraction

### Build-time vs Runtime

- **Development**: Files are compiled on-demand with HMR
- **Production**: Files are pre-compiled during the Vite build step
- **Pre-rendering**: MDX content is included in pre-rendered static HTML

### Type Safety

TypeScript types are provided in `app/types/mdx.d.ts` for proper autocomplete and type checking.

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
