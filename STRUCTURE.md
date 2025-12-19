# File Structure

This document outlines the codebase structure for the Mirascope monorepo, which contains the Python and TypeScript SDKs, cloud application, and unified documentation.

> **Note**: This document is intended to be a live, self-updating reference. When making structural changes to the codebase (adding/removing directories, changing organization, updating tooling), please update this file accordingly. This ensures it remains an accurate source of truth for the codebase structure.

## Overview

```text
mirascope/         # Version 2
├── python/          # Python SDK implementation
├── typescript/      # TypeScript SDK implementation
├── cloud/           # Full-stack cloud application
├── docs/            # Unified cross-language documentation and website
└── [config files]   # Monorepo-level configuration
```

## Monorepo Structure

Mirascope uses a monorepo structure to manage multiple packages and applications in a single repository. This provides several key benefits:

### Benefits of Monorepo Structure

1. **Unified Development**: All packages share the same repository, enabling coordinated development across Python, TypeScript, and cloud applications.

2. **Simplified Script Orchestration**: The root `package.json` provides convenient passthrough commands to run scripts in any workspace (e.g., `bun run test:python`, `bun run typecheck:typescript`, `bun run cloud:dev`).

3. **Shared Documentation**: Unified documentation site (`docs/`) provides cross-language documentation for both Python and TypeScript implementations.

4. **Consistent Tooling**: Shared linting, formatting, and CI/CD configuration across all packages.

5. **Language-Specific Tooling**: Python uses `uv` for package management, TypeScript/Cloud/Docs use `bun`, each optimized for their respective ecosystems.

## Python SDK Implementation (`python/`)

```text
python/
├── mirascope/            # Main Python package
│   ├── __init__.py         # Package exports
│   ├── llm/                # "LLM abstractions that aren't obstructions"
│   │   ├── __init__.py       # LLM module exports
│   │   ├── agents/           # Agent functionality (currently not publicly exported)
│   │   │   ├── __init__.py
│   │   │   ├── agent.py
│   │   │   ├── agent_template.py
│   │   │   └── decorator.py
│   │   ├── calls/            # Call decorator and call management
│   │   │   ├── __init__.py
│   │   │   ├── base_call.py
│   │   │   ├── calls.py
│   │   │   └── decorator.py
│   │   ├── providers/         # Provider-specific implementations
│   │   │   ├── __init__.py
│   │   │   ├── base/
│   │   │   ├── anthropic/
│   │   │   ├── google/
│   │   │   ├── openai/
│   │   │   │   └── completions/base_provider.py
│   │   │   ├── together/
│   │   │   ├── provider_registry.py
│   │   │   └── load_provider.py
│   │   ├── content/          # Content types (text, image, audio, etc.)
│   │   │   ├── __init__.py
│   │   │   ├── audio.py
│   │   │   ├── document.py
│   │   │   ├── image.py
│   │   │   ├── text.py
│   │   │   ├── thought.py
│   │   │   ├── tool_call.py
│   │   │   └── tool_output.py
│   │   ├── context/          # Context management
│   │   │   ├── __init__.py
│   │   │   ├── context.py
│   │   │   └── _utils.py
│   │   ├── exceptions.py     # Exception classes
│   │   ├── formatting/       # Response formatting
│   │   │   ├── __init__.py
│   │   │   ├── format.py
│   │   │   ├── from_call_args.py
│   │   │   ├── partial.py
│   │   │   ├── types.py
│   │   │   └── _utils.py
│   │   ├── mcp/              # Model Context Protocol support
│   │   │   ├── __init__.py
│   │   │   └── client.py
│   │   ├── messages/         # Message types
│   │   │   ├── __init__.py
│   │   │   └── message.py
│   │   ├── models/           # Model abstraction
│   │   │   ├── __init__.py
│   │   │   └── models.py
│   │   ├── prompts/          # Prompt decorator and templates
│   │   │   ├── __init__.py
│   │   │   ├── decorator.py
│   │   │   ├── protocols.py
│   │   │   └── _utils.py
│   │   ├── responses/        # Response and streaming response types
│   │   │   ├── __init__.py
│   │   │   ├── base_response.py
│   │   │   ├── base_stream_response.py
│   │   │   ├── finish_reason.py
│   │   │   ├── response.py
│   │   │   ├── root_response.py
│   │   │   ├── stream_response.py
│   │   │   ├── streams.py
│   │   │   └── _utils.py
│   │   ├── tools/            # Tool decorator and types and toolkits
│   │   │   ├── __init__.py
│   │   │   ├── decorator.py
│   │   │   ├── protocols.py
│   │   │   ├── tool_schema.py
│   │   │   ├── toolkit.py
│   │   │   ├── tools.py
│   │   │   └── _utils.py
│   │   └── types/            # Type definitions
│   │       ├── __init__.py
│   │       ├── dataclass.py
│   │       ├── jsonable.py
│   │       └── type_vars.py
│   └── graphs/             # Graph/FSM functionality (currently not publicly exported)
│       ├── __init__.py
│       └── finite_state_machine.py
├── examples/             # Example code
│   ├── intro/              # Introduction examples
│   │   ├── context/
│   │   ├── decorator/
│   │   ├── format/
│   │   ├── model/
│   │   ├── override/
│   │   ├── parameters/
│   │   ├── resume/
│   │   ├── system_messages/
│   │   └── tool_call/
│   ├── misc/               # Miscellaneous examples
│   └── sazed/              # Sazed examples
├── tests/                # Test suite
│   ├── conftest.py         # Pytest configuration
│   ├── e2e/                # End-to-end tests
│   │   ├── input/            # Tests for various input possibilities
│   │   ├── output/           # Tests for various output possibilities
│   │   └── assets/           # Test assets (images, audio)
│   ├── llm/                # LLM module tests
│   │   ├── calls/
│   │   ├── clients/
│   │   ├── content/
│   │   ├── context/
│   │   ├── formatting/
│   │   ├── messages/
│   │   ├── models/
│   │   ├── prompts/
│   │   ├── providers/
│   │   ├── responses/
│   │   └── tools/
│   ├── test_imports.py
│   └── utils.py
├── typechecking/         # Type checking utilities
│   ├── agent.py
│   ├── call.py
│   ├── context.py
│   ├── format.py
│   ├── streams.py
│   ├── tool.py
│   └── utils.py
├── scripts/              # Build and utility scripts
│   ├── example_generator.ts
│   ├── regenerate_examples.ts
│   └── model_features/   # Model feature testing and code generation
│       ├── codegen_openai.py
│       ├── test_openai.py
│       └── data/
│           └── openai.yaml
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

## Cloud Application (`cloud/`)

The full-stack cloud application built with React and Cloudflare Workers.

**Note**: React component files use shadcn-style kebab-case (e.g. `home-page.tsx`), exports use PascalCase (e.g. `HomePage`).

```text
cloud/
├── app/                           # Frontend React application
│   ├── api/                       # API client code
│   │   ├── auth/                  # Authentication API endpoints
│   │   ├── client.ts
│   │   └── [other files]          # organizations.ts, index.ts, etc.
│   ├── components/                # React components
│   │   ├── blocks/                # Components which are composed of other components
│   │   │   ├── code-block/        # Code block component
│   │   │   ├── combobox.tsx
│   │   │   └── [other files]      # copy-button.tsx, diff-tool.tsx, etc.
│   │   ├── error/                 # Error components
│   │   │   └── default-catch-boundary.tsx
│   │   ├── ui/                    # UI component library, contains the shadcn-ui components
│   │   ├── home-page.tsx
│   │   ├── home-page.module.css   # CSS module for non-tailwind CSS of the home page
│   │   └── [other files]          # front-page.tsx, login-page.tsx, etc.
│   ├── contexts/                  # React contexts
│   │   └── auth.tsx               # Authentication context
│   ├── hooks/                     # Custom React hooks
│   │   ├── gradient-fade-scroll.ts
│   │   └── sunset-time.ts
│   ├── lib/                       # Shared utilities
│   │   ├── code-highlight.ts
│   │   └── [other files]          # utils.ts, types.ts, effect.ts, etc.
│   ├── routes/                    # TanStack Router pages
│   │   ├── auth/                  # Authentication routes
│   │   │   ├── github.tsx
│   │   │   └── [other files]      # google.tsx, callback routes, etc.
│   │   ├── __root.tsx             # Root layout
│   │   └── [other files]          # index.tsx, home.tsx, login.tsx, etc.
│   ├── styles/                    # CSS and styling
│   │   └── globals.css
│   ├── router.tsx
│   └── routeTree.gen.ts           # Auto-generated route tree
├── api/                           # Backend API handlers
│   ├── api.ts
│   ├── docs.handlers.ts           # Documentation handlers
│   └── [other files]              # handlers, schemas, tests for docs/health/orgs/traces
├── auth/                          # Authentication module
│   ├── service.ts                 # Auth service
│   └── [other files]              # context.ts, errors.ts, oauth.ts, etc.
├── db/                            # Database module
│   ├── migrations/                # Database migrations
│   │   ├── meta/                  # Migration metadata
│   │   └── *.sql
│   ├── schema/                    # Database schema
│   │   ├── users.ts
│   │   └── [other files]          # organizations.ts, sessions.ts, etc.
│   ├── services/                  # Database services
│   │   ├── base.ts                # Base service
│   │   └── [other files]          # users.ts, organizations.ts, tests, etc.
│   ├── errors.ts                  # Database errors
│   └── utils.ts                   # Database utilities
├── tests/                         # Test utilities
│   ├── api.ts                     # API test utilities
│   └── db.ts                      # Database test utilities
├── docker/                        # Docker configuration
│   ├── compose.yml
│   └── data/                      # Docker data directory
├── dist/                          # Build output
│   ├── client/                    # Client build artifacts
│   └── server/                    # Server build artifacts
├── public/                        # Static assets
│   ├── assets/                    # Static assets
│   │   ├── backgrounds/           # Background images
│   │   └── branding/              # Branding assets
│   ├── fonts/                     # Custom fonts
│   ├── icons/                     # App icons and favicons
│   ├── manifest.json
│   └── robots.txt
├── components.json                # Shadcn-ui components configuration
├── [other files]                  # e.g. package.json, tsconfig.json, vite.config.ts, etc.
```

**Tooling Choices**:

- **React 19**: Modern React features and performance improvements
- **TanStack Router**: File-based routing with type-safe navigation
- **Vite**: Fast build tool and dev server
- **Tailwind CSS v4**: Utility-first CSS
- **Cloudflare Workers**: Serverless edge deployment
- **Vitest**: Fast test runner

## Documentation (`docs/`)

Unified cross-language documentation site built with custom MDX-based system.

```text
docs/
├── content/               # Documentation content
│   ├── _meta.ts             # Navigation metadata
│   ├── index.mdx            # Home page
│   └── examples.mdx         # Examples page
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

1. **Monorepo Structure**: Using a monorepo to manage Python SDK, TypeScript SDK, cloud application, and documentation in a single repository enables coordinated development and shared tooling.

2. **Language-Specific Tooling**: Python uses `uv` for fast package management, while TypeScript/JavaScript uses `bun` for optimal performance in their respective ecosystems.

3. **Unified Documentation**: Single documentation site (`docs/`) provides cross-language documentation, ensuring consistency between Python and TypeScript implementations.

4. **Provider-Agnostic Design**: The `llm` module in both Python and TypeScript provides unified interfaces that abstract over provider-specific differences, enabling code portability across LLM providers.

5. **Decorator-Based API**: The Python implementation provides a decorator approach (`@llm.call`, `@llm.prompt`, `@llm.tool`) while also exposing lower-level model APIs. TypeScript doesn't support decorators the same way, so it has a more functional approach.

6. **Type Safety**: Strong type safety in both Python (via Pydantic and type hints) and TypeScript (via TypeScript's type system) ensures compile-time error detection.

7. **Passthrough Scripts**: Root `package.json` provides convenient commands that delegate to workspace-specific scripts, enabling unified CI/CD and developer workflows.

8. **Test Organization**: Tests are co-located with their respective packages (`python/tests/`, `cloud/` tests), with root-level `tests/` for legacy code only.

9. **Cloud Application**: Full-stack application in `cloud/` demonstrates real-world usage of the SDKs and provides cloud-based features.

This structure enables independent development of each package while maintaining deployment simplicity and unified tooling through the monorepo setup.
