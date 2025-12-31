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
