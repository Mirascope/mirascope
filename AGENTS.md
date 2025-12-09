# AI Agent Context Guide

This document provides guidance for AI agents and assistants working with the Mirascope codebase. It points to key resources that provide high-level context about the codebase structure, architecture, and development practices.

## Primary Context Sources

When working on this codebase, start by reviewing these documents for high-level context:

1. **[README.md](README.md)**: Overview of the project, installation, development setup, and quick start information.

2. **[STRUCTURE.md](STRUCTURE.md)**: Comprehensive documentation of the codebase structure, including:
   - Monorepo organization and benefits
   - Detailed file structure for each package (Python SDK, TypeScript SDK, Cloud, Docs)
   - Tooling choices and rationale
   - Key design decisions and architectural patterns

## Codebase Overview

Mirascope is a monorepo containing:

- **Python SDK** (`python/`): The main Python implementation with LLM abstractions
- **TypeScript SDK** (`typescript/`): TypeScript implementation (development paused)
- **Cloud Application** (`cloud/`): Full-stack React application with Cloudflare Workers
- **Documentation** (`docs/`): Unified cross-language documentation site

## Key Principles

When making changes to the codebase:

1. **Keep STRUCTURE.md Updated**: If you modify the codebase structure (add/remove directories, change organization, update tooling), update `STRUCTURE.md` to reflect these changes. This document should serve as a live, self-updating reference.

2. **Follow Existing Patterns**: The codebase has established patterns for:
   - Decorator-based APIs in Python (`@llm.call`, `@llm.prompt`, `@llm.tool`)
   - Provider-agnostic abstractions
   - Type safety across languages
   - Test organization

3. **Respect Monorepo Structure**: Each package (`python/`, `typescript/`, `cloud/`, `docs/`) has its own tooling and dependencies. Use the root-level passthrough scripts when possible.

## Quick Reference

- **Python Package Manager**: `uv`
- **TypeScript/JS Package Manager**: `bun`
- **Python Testing**: `pytest`
- **TypeScript Testing**: `vitest`
- **Linting**: `ruff` (Python), `eslint` (TypeScript)
- **Type Checking**: `pyright` (Python), `tsc` (TypeScript)

## Cloud Application Development

The `cloud/` package uses specific patterns and technologies that differ from typical TypeScript projects:

### Effect TypeScript

The cloud application uses [Effect](https://effect.website/) for functional programming:

- **Services**: Use `Effect.gen` generators with `yield*` for dependency injection
- **Error Handling**: Use `Effect.either` in tests to assert specific error types
- **Layers**: Compose services using `Layer.provide` and `Layer.merge`

```typescript
// Example: Effect-based service call
Effect.gen(function* () {
  const db = yield* DatabaseService;
  const user = yield* AuthenticatedUser;
  return yield* db.organizations.findAll(user.id);
})
```

### Database Services (`cloud/db/services/`)

- Services extend `BaseService` or `BaseAuthenticatedService` for CRUD operations
- `BaseAuthenticatedService` includes built-in permission checks
- Error types: `DatabaseError`, `NotFoundError`, `AlreadyExistsError`, `PermissionDeniedError`

### Error Handling (`cloud/db/errors.ts`)

Error types have a static `status` property for HTTP status codes:

```typescript
// Errors define their own HTTP status
export class NotFoundError extends Schema.TaggedError<NotFoundError>()(...) {
  static readonly status = 404 as const;
}

// Use in API schemas - always reference the static property
HttpApiEndpoint.get("get", "/resource/:id")
  .addError(NotFoundError, { status: NotFoundError.status })
  .addError(PermissionDeniedError, { status: PermissionDeniedError.status })
  .addError(DatabaseError, { status: DatabaseError.status })
```

Status code mappings:
| Error | Status |
|-------|--------|
| `NotFoundError` | 404 |
| `PermissionDeniedError` | 403 |
| `AlreadyExistsError` | 409 |
| `UnauthorizedError` | 401 |
| `InvalidSessionError` | 401 |
| `DatabaseError` | 500 |

### API Design (`cloud/api/`)

- Uses `@effect/platform` HttpApi for type-safe API definitions
- RESTful nested resources: organizations → projects → environments → api-keys
- Schemas use Effect's `Schema` module for validation
- Use full paths in endpoint definitions (e.g., `/organizations/:id`) not `.prefix()`

```typescript
// String validation pattern
Schema.String.pipe(Schema.nonEmpty(), Schema.maxLength(100))
```

### Frontend (`cloud/src/`)

- **TanStack Router**: File-based routing; run `bun run dev` to regenerate `routeTree.gen.ts` after route changes
- **TanStack Query**: Data fetching with React Query hooks
- **Server Functions**: Use `createServerFn` with only `GET` (reads) or `POST` (mutations) - not REST verbs like DELETE/PUT

### Testing Requirements

- **100% test coverage required** (branches, statements, functions, lines)
- Run `bun run test:coverage` to verify
- Use `/* v8 ignore next */` or `/* v8 ignore start/stop */` for defensive code that can't be tested
- Use `Effect.either` to test error cases and assert specific error types
- Resource cleanup: use `beforeAll`/`afterAll` hooks in test helpers

### Common Commands (from `cloud/`)

```bash
bun run typecheck      # TypeScript type checking
bun run lint:eslint    # ESLint
bun run test:coverage  # Run tests with coverage report
bun run test <file>    # Run specific test file
bun run dev            # Start dev server (also regenerates TanStack Router routes)
```

### OpenAPI & SDK Generation

- OpenAPI spec: `bun run api/generate-openapi.ts > ../fern/openapi.json`
- Python SDK: `bun run cloud:python-sdk:generate` (from repo root)
- Note: Effect's `_tag` discriminator is renamed to `tag` for Fern SDK compatibility

## Git Workflow with Graphite

The repository uses [Graphite](https://graphite.dev/) (`gt`) for stacked PRs:

```bash
gt create ENG-{NUM} -m "{MESSAGE}"  # Create a new branch/PR
gt modify -a                         # Amend current PR with staged changes
gt checkout <branch>                 # Switch to a branch in the stack
gt up / gt down                      # Navigate up/down the stack
gt submit                            # Push all PRs in the stack
```

### PR Checklist

Before submitting changes, ensure:

1. `bun run typecheck` passes
2. `bun run lint:eslint` passes  
3. `bun run test:coverage` shows 100% coverage
4. OpenAPI spec regenerated if API changed

## Getting Help

If you need more context about:

- **Specific modules or features**: Check the relevant package's README or documentation
- **Architecture decisions**: See `STRUCTURE.md` "Key Design Decisions" section
- **Development workflow**: See `README.md` for CI, testing, and build instructions

