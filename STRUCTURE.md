# File Structure

This document outlines the codebase structure for the Mirascope monorepo, which contains the Python and TypeScript SDKs, website, and unified documentation.

> **Note**: This document is intended to be a live, self-updating reference. When making structural changes to the codebase (adding/removing directories, changing organization, updating tooling), please update this file accordingly. This ensures it remains an accurate source of truth for the codebase structure.

## Overview

```text
mirascope/         # Version 2
├── python/          # Python SDK implementation
├── typescript/      # TypeScript SDK implementation
├── website/         # Marketing website (docs, blog, landing page)
├── docs/            # Unified cross-language documentation and website
└── [config files]   # Monorepo-level configuration
```

## Monorepo Structure

Mirascope uses a monorepo structure to manage multiple packages and applications in a single repository. This provides several key benefits:

### Benefits of Monorepo Structure

1. **Unified Development**: All packages share the same repository, enabling coordinated development across Python, TypeScript, and the website.

2. **Simplified Script Orchestration**: The root `package.json` provides convenient passthrough commands to run scripts in any workspace (e.g., `bun run test:python`, `bun run typecheck:typescript`, `bun run website:dev`).

3. **Shared Documentation**: Unified documentation site (`docs/`) provides cross-language documentation for both Python and TypeScript implementations.

4. **Consistent Tooling**: Shared linting, formatting, and CI/CD configuration across all packages.

5. **Language-Specific Tooling**: Python uses `uv` for package management, TypeScript/Website/Docs use `bun`, each optimized for their respective ecosystems.

## Python SDK Implementation (`python/`)

```text
python/
├── mirascope/            # Main Python package
│   ├── __init__.py         # Package exports
│   ├── llm/                # "LLM abstractions that aren't obstructions"
│   │   ├── __init__.py       # LLM module exports
│   │   ├── agents/           # Agent functionality (currently not publicly exported)
│   │   ├── calls/            # Call decorator and call management
│   │   ├── providers/         # Provider-specific implementations
│   │   ├── content/          # Content types (text, image, audio, etc.)
│   │   ├── context/          # Context management
│   │   ├── formatting/       # Response formatting
│   │   ├── mcp/              # Model Context Protocol support
│   │   ├── messages/         # Message types
│   │   ├── models/           # Model abstraction
│   │   ├── prompts/          # Prompt decorator and templates
│   │   ├── responses/        # Response and streaming response types
│   │   ├── tools/            # Tool decorator and types and toolkits
│   │   └── types/            # Type definitions
│   └── ops/               # Operational helpers (tracing, versioning)
├── examples/             # Example code
├── tests/                # Test suite
├── typechecking/         # Type checking utilities
├── scripts/              # Build and utility scripts
├── pyproject.toml        # Python package configuration
├── uv.lock               # Dependency lock file
└── README.md             # Python SDK README
```

**Tooling Choices**:

- **uv**: Fast Python package manager and resolver
- **pytest**: Test framework with comprehensive e2e testing
- **ruff**: Fast Python linter and formatter
- **pyright**: Type checker for Python (waiting for `ty` to become stable)
- **pydantic**: Data validation and settings management

## TypeScript Implementation (`typescript/`)

The TypeScript SDK's development is currently paused. We plan to resume development once we further finalize the Python `llm` interfaces.

## Website (`website/`)

The marketing website built with React, TanStack Router, and Vite. Serves docs, blog, landing page, and pricing.

**Note**: React component files use shadcn-style kebab-case (e.g. `home-page.tsx`), exports use PascalCase (e.g. `HomePage`).

```text
website/
├── app/                           # Frontend React application
│   ├── components/                # React components
│   │   ├── blocks/                # Components composed of other components
│   │   │   ├── code-block/        # Code block component
│   │   │   ├── navigation/        # Header, desktop/mobile navigation
│   │   │   └── [other files]      # copy-button.tsx, etc.
│   │   ├── error/                 # Error components
│   │   ├── ui/                    # UI component library (shadcn-ui)
│   │   ├── home-page.tsx
│   │   └── [other files]          # pricing-page.tsx, etc.
│   ├── hooks/                     # Custom React hooks
│   ├── lib/                       # Shared utilities
│   │   ├── content/               # Content loading utilities
│   │   ├── search/                # Search functionality
│   │   ├── seo/                   # SEO utilities
│   │   └── mdx/                   # MDX processing
│   ├── routes/                    # TanStack Router pages
│   │   ├── __root.tsx             # Root layout
│   │   ├── index.tsx              # Home page
│   │   ├── docs.tsx               # Documentation layout
│   │   ├── blog.tsx               # Blog layout
│   │   ├── pricing.tsx            # Pricing page
│   │   └── [other files]          # privacy.tsx, terms.tsx, etc.
│   └── styles/                    # CSS and styling
├── public/                        # Static assets
├── vite-plugins/                  # Custom Vite plugins
├── package.json
├── tsconfig.json
├── vite.config.ts
└── wrangler.jsonc                 # Cloudflare Pages deployment config
```

**Tooling Choices**:

- **React 19**: Modern React features and performance improvements
- **TanStack Router**: File-based routing with type-safe navigation
- **Vite**: Fast build tool and dev server
- **Tailwind CSS v4**: Utility-first CSS
- **Vitest**: Fast test runner

## Documentation (`docs/`)

Unified cross-language documentation site built with custom MDX-based system.

```text
docs/
├── content/               # Documentation content
│   ├── _meta.ts             # Navigation metadata
│   ├── index.mdx            # Home page
├── config/                # Build configuration
│   └── [build output]       # Generated build files
├── scripts/               # Documentation build scripts
│   ├── cli.py               # CLI utilities
│   ├── merge-api-meta.ts    # API metadata merging
│   └── sync-website.ts      # Website synchronization
├── package.json           # Dependencies and scripts
├── tsconfig.json          # TypeScript configuration
├── wrangler.jsonc         # Cloudflare Pages deployment config
└── dist/                  # Built documentation site
```

**Tooling Choices**:

- **MDX**: Markdown with JSX components
- **TanStack Router**: File-based routing for documentation
- **Custom Build System**: Tailored documentation generation
- **Cloudflare Pages**: Documentation hosting

## Root-Level Configuration

### Monorepo Configuration

- **`package.json`**: Root package configuration with passthrough scripts for all workspaces
- **`.prettierrc`**: Code formatting configuration (applies to all workspaces)
- **`.gitignore`**: Git ignore patterns (applies to entire monorepo)
- **`pyrightconfig.json`**: Python type checking configuration

### Build Artifacts

- **`build/`**: Generated build snippets and artifacts
- **`dist/`**: Distribution files
- **`site/`**: Built documentation site (legacy)
- **`htmlcov/`**: HTML coverage reports

## Key Design Decisions

1. **Monorepo Structure**: Using a monorepo to manage Python SDK, TypeScript SDK, website, and documentation in a single repository enables coordinated development and shared tooling.

2. **Language-Specific Tooling**: Python uses `uv` for fast package management, while TypeScript/JavaScript uses `bun` for optimal performance in their respective ecosystems.

3. **Unified Documentation**: Single documentation site (`docs/`) provides cross-language documentation, ensuring consistency between Python and TypeScript implementations.

4. **Provider-Agnostic Design**: The `llm` module in both Python and TypeScript provides unified interfaces that abstract over provider-specific differences, enabling code portability across LLM providers.

5. **Decorator-Based API**: The Python implementation provides a decorator approach (`@llm.call`, `@llm.prompt`, `@llm.tool`) while also exposing lower-level model APIs. TypeScript doesn't support decorators the same way, so it has a more functional approach.

6. **Type Safety**: Strong type safety in both Python (via Pydantic and type hints) and TypeScript (via TypeScript's type system) ensures compile-time error detection.

7. **Passthrough Scripts**: Root `package.json` provides convenient commands that delegate to workspace-specific scripts, enabling unified CI/CD and developer workflows.

8. **Test Organization**: Tests are co-located with their respective packages (`python/tests/`, `website/` tests), with root-level `tests/` for legacy code only.

This structure enables independent development of each package while maintaining deployment simplicity and unified tooling through the monorepo setup.
