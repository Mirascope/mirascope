# Website Development Guide

The `website/` package is the Mirascope marketing website built with React, TanStack Router, and Vite. It serves the docs, blog, landing page, and pricing page.

## Tech Stack

- **React 19** with **TanStack Router** (file-based routing)
- **Vite** as the build tool and dev server
- **Tailwind CSS v4** for styling
- **shadcn/ui** components in `app/components/ui/`
- **Vitest** for testing
- **Cloudflare Pages** for deployment

## Key Directories

- `app/routes/` — TanStack Router pages (file-based routing)
- `app/components/` — React components
  - `blocks/` — Composed components (navigation, code blocks, etc.)
  - `ui/` — shadcn/ui primitives
  - `error/` — Error boundary components
- `app/lib/` — Shared utilities
  - `content/` — Content loading (MDX, docs)
  - `search/` — Search functionality
  - `seo/` — SEO utilities
  - `mdx/` — MDX processing
- `app/hooks/` — Custom React hooks
- `public/` — Static assets
- `vite-plugins/` — Custom Vite plugins

## Naming Conventions

- **Files**: kebab-case (e.g., `home-page.tsx`, `pricing-page.tsx`)
- **Exports**: PascalCase for components (e.g., `HomePage`, `PricingPage`)
- **Routes**: Follow TanStack Router file-based conventions

## Common Commands (from `website/`)

```bash
bun run dev          # Start dev server
bun run build        # Build for production
bun run typecheck    # Run TypeScript type checking
bun run lint         # Run all linters
bun run test         # Run tests
bun run test:coverage # Run tests with coverage
```

## PR Checklist

Before submitting changes, ensure:

1. `bun run typecheck` passes
2. `bun run lint:oxlint` passes
3. `bun run test:coverage` passes
