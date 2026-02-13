# Cloud Application Development

The `cloud/` package uses specific patterns and technologies that differ from typical TypeScript projects:

## Effect TypeScript

The cloud application uses [Effect](https://effect.website/) for functional programming:

- **Services**: Use `Effect.gen` generators with `yield*` for dependency injection
- **Error Handling**: Use `Effect.flip` in tests to assert specific error types (converts success/failure)
- **Layers**: Compose services using `Layer.provide` and `Layer.merge`

```typescript
// Example: Effect-based database call
Effect.gen(function* () {
  const db = yield* Database;
  
  const user = yield* db.users.create({
    data: { email: "user@example.com", name: "User" },
  });
  
  // Nested resource access
  const org = yield* db.organizations.create({
    userId: user.id,
    data: { name: "My Org" },
  });
  
  return { user, org };
});
```

## Database Services (`cloud/db/`)

Services are Effect-native and located directly in `cloud/db/`:

- **`BaseEffectService`**: For unauthenticated resources (users, sessions)
- **`BaseAuthenticatedEffectService`**: For resources requiring authorization (organizations, projects, environments, API keys)

Key characteristics:

- Services use `yield* DrizzleORM` to access the database client
- Path parameters define resource hierarchy (e.g., `"organizations/:organizationId/projects/:projectId"`)
- Authorization is handled via `getRole()` and `getPermissionTable()` methods
- Error types: `DatabaseError`, `NotFoundError`, `AlreadyExistsError`, `PermissionDeniedError`

```typescript
// Service hierarchy via Database
db.users.create(...)
db.sessions.create(...)
db.organizations.create(...)
db.organizations.memberships.create(...)
db.organizations.projects.create(...)
db.organizations.projects.memberships.create(...)
db.organizations.projects.environments.create(...)
db.organizations.projects.environments.apiKeys.create(...)
```

## Error Handling (`cloud/db/errors.ts`)

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

## API Design (`cloud/api/`)

- Uses `@effect/platform` HttpApi for type-safe API definitions
- RESTful nested resources: organizations → projects → environments → api-keys
- Schemas use Effect's `Schema` module for validation
- Use full paths in endpoint definitions (e.g., `/organizations/:id`) not `.prefix()`

```typescript
// String validation pattern
Schema.String.pipe(Schema.nonEmpty(), Schema.maxLength(100))
```

## Frontend (`cloud/app/`)

- **TanStack Router**: File-based routing; run `bun run dev` to regenerate `routeTree.gen.ts` after route changes
- **TanStack Query + Effect Query**: Data fetching with React Query hooks that run Effect programs
- **API Client Hooks**: Located in `cloud/app/api/` - use `@tanstack/react-query` with `effect-query`
- **Contexts**: Located in `cloud/app/contexts/` for state management (organization, project, environment)
- **Import paths**: Use `@/app/` prefix (not `@/src/`)

```typescript
// Example: API hook pattern
export const useEnvironments = (organizationId: string | null, projectId: string | null) => {
  return useQuery({
    ...eq.queryOptions({
      queryKey: ["environments", organizationId, projectId],
      queryFn: () =>
        Effect.gen(function* () {
          const client = yield* ApiClient;
          return yield* client.environments.list({
            path: { organizationId: organizationId!, projectId: projectId! },
          });
        }),
    }),
    enabled: !!organizationId && !!projectId,
  });
};
```

## Route Metadata (SEO & Social Cards)

Route metadata (title, description) is managed differently for content vs static routes:

### Content Routes (docs, blog posts, policy pages)

Use `createContentRouteConfig()` from `@/app/lib/content/route-config.tsx`. Metadata comes from MDX frontmatter.

```typescript
// Example: docs.v1.$.tsx
export const Route = createFileRoute("/docs/v1/$")(
  createContentRouteConfig("/docs/v1/$", {
    getMeta: getAllDocsMeta,
    moduleMap: DOCS_MODULE_MAP,
    prefix: "docs",
    version: "v1",
    component: DocsPage,
  })
);
```

### Static Routes (home, pricing, etc.)

Use `createStaticRouteHead()` from `@/app/lib/seo/static-route-head.ts`. Metadata is defined in `@/app/lib/seo/static-routes.ts`.

```typescript
// Example: index.tsx
import { createStaticRouteHead } from "@/app/lib/seo/static-route-head";

export const Route = createFileRoute("/")({
  head: createStaticRouteHead("/"),
  component: HomePage,
});
```

**Adding a new static route**: Edit `static-routes.ts` to add an entry:

```typescript
// static-routes.ts
export const STATIC_ROUTE_REGISTRY = {
  "/": { title: "Home", description: "..." },
  "/pricing": { title: "Pricing", description: "..." },
  // Add new routes here - keys are TanStack Router route IDs
};
```

The social card generator (`vite-plugins/social-cards.ts`) automatically uses both registries.

## Design System, Styles, & UI Components

The frontend uses [shadcn/ui](https://ui.shadcn.com/) with Tailwind CSS v4.

### Adding shadcn Components

For easier maintenance, avoid making significant modifications to shadcn components. Instead, build your custom components by composing the provided primitives, following the structure outlined below.

```bash
bunx --bun shadcn@latest add <component>  # e.g., bunx --bun shadcn@latest add pagination
```

### Component Directory Structure

```
app/components/
├── blocks/           # Complex, often shared, composed components
│   ├── branding/     # Logo, GitHub button, Discord link
│   ├── code-block/   # Syntax-highlighted code blocks
│   ├── docs/         # Documentation-specific components (API signatures, tables)
│   └── navigation/   # Header, footer, sidebar, search bar
├── dashboard/        # Dashboard-specific components (stat cards, selectors)
├── error/            # Error boundary components
├── mdx/              # MDX rendering and custom elements
│   └── elements/     # MDX-specific components (callouts, tabs, code blocks)
└── ui/               # shadcn/ui primitives (button, dialog, input, etc.)
```

### CSS Organization

- `globals.css` - theme variables, base styles, and custom utilities
- `content.css` - MDX/documentation content styling
- `code-highlighting.css` - syntax highlighting for code blocks

**CSS Modules**: Use `.module.css` files when UI/UX differs significantly from the design system (e.g., `home-page.module.css`, `mermaid-diagram.module.css`).

### Class Utilities

- **Always use `cn()`** from `@/app/lib/utils` when combining Tailwind classes
- **Use `cva`** from `class-variance-authority` when creating components with style variants (see `button.tsx`, `alert.tsx` for examples)

```typescript
// Example: Component with variants using cva
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/app/lib/utils";

const myComponentVariants = cva("base-classes", {
  variants: {
    variant: { default: "...", secondary: "..." },
    size: { default: "...", sm: "..." },
  },
  defaultVariants: { variant: "default", size: "default" },
});
```

### Custom Utility Classes

These utility classes are defined in `globals.css`:

- `textured-bg` - paper texture overlay
- `text-shade` / `box-shade` - shadow effects
- `nav-text` - navigation text with theme-aware styling

### Brand & Typography

- `text-mirple` / `bg-mirple` - Mirascope brand purple
- `font-display` - headings, buttons, and UI elements (Nunito)
- `font-sans` - body/content text (Nunito Sans)
- `font-handwriting` - logo only (Williams Handwriting)

## Authentication (`cloud/auth/`)

- **Session-based**: Via cookies with `getSessionIdFromCookie()`
- **API Key-based**: Via `X-API-Key` header with `authenticateApiKeyWithUser()`
- API keys are scoped to their creator via `createdById` column
- Use `getCreator(apiKeyId)` to resolve the user who created an API key
- `authenticate(...)` tries session auth first, then API key auth

## Testing Patterns

### Test Fixtures (`cloud/tests/db.ts`)

Hierarchical fixtures for Effect-native database tests:

```typescript
// Organization-level fixture
const { org, owner, admin, member, nonMember } = yield* TestOrganizationFixture;

// Project-level fixture (includes organization fixture)
const { org, project, owner, admin, member, nonMember, 
        projectAdmin, projectDeveloper, projectViewer, projectAnnotator } 
  = yield* TestProjectFixture;

// Environment-level fixture (includes project fixture)
const { org, project, environment, owner, ... } = yield* TestEnvironmentFixture;
```

### Testing with `it.effect`

Use the wrapped `it` from `@/tests/db` for both regular and Effect tests:

```typescript
import { describe, it, expect, TestProjectFixture } from "@/tests/db";

describe("MyService", () => {
  // Regular vitest test
  it("should do something sync", () => {
    expect(1 + 1).toBe(2);
  });

  // Effect-native test with auto-provided database layer
  it.effect("should create a resource", () =>
    Effect.gen(function* () {
      const { org, owner } = yield* TestProjectFixture;
      const db = yield* Database;
      
      const result = yield* db.organizations.projects.create({
        userId: owner.id,
        organizationId: org.id,
        data: { name: "New Project" },
      });
      
      expect(result.name).toBe("New Project");
    }),
  );
});
```

### Testing Errors with `Effect.flip`

```typescript
it.effect("returns NotFoundError for non-existent resource", () =>
  Effect.gen(function* () {
    const db = yield* Database;
    
    const result = yield* db.users.findById({ userId: "non-existent" })
      .pipe(Effect.flip); // Converts failure to success for assertion
    
    expect(result).toBeInstanceOf(NotFoundError);
  }),
);
```

### MockDrizzleORM for Database Error Testing

```typescript
import { MockDrizzleORM } from "@/tests/db";

it.effect("returns DatabaseError when query fails", () =>
  Effect.gen(function* () {
    const db = yield* Database;
    
    const result = yield* db.users.findById({ userId: "any-id" })
      .pipe(Effect.flip);
    
    expect(result).toBeInstanceOf(DatabaseError);
  }).pipe(
    Effect.provide(
      new MockDrizzleORM().select(new Error("Connection failed")).build(),
    ),
  ),
);
```

## Testing Requirements

- **100% test coverage required** (branches, statements, functions, lines)
- Run `bun run test:coverage` to verify
- Use `/* v8 ignore next */` or `/* v8 ignore start/stop */` for defensive code that can't be tested
- Resource cleanup: use `beforeAll`/`afterAll` hooks in test helpers

## Common Commands (from `cloud/`)

```bash
bun run typecheck      # TypeScript type checking
bun run lint:oxlint    # oxlint
bun run test           # Run all tests (NOT `bun test`)
bun run test:coverage  # Run tests with coverage report
bun run test <file>    # Run specific test file
bun run dev            # Start dev server (also regenerates TanStack Router routes)
bun run db:generate    # Generate new database migrations
```

**Important**: Use `bun run test` (not `bun test`) to run tests through vitest with proper configuration.

## OpenAPI & SDK Generation

- OpenAPI spec: `bun run api/generate-openapi.ts > ../fern/openapi.json`
- Python SDK: `bun run cloud:python-sdk:generate` (from repo root)
- Note: Effect's `_tag` discriminator is renamed to `tag` for Fern SDK compatibility

## Before Implementing

1. **Read existing implementations first**: Always examine similar existing code before implementing new features. For example, look at how `Projects` is implemented before implementing `Environments`.

2. **Understand the path parameter pattern**: The codebase uses REST-style path patterns (`"organizations/:organizationId/projects/:projectId"`) that determine authorization scope and type safety.

3. **Check import paths**: Frontend code uses `@/app/` prefix, not `@/src/`. Database code uses `@/db/` prefix.

## During Implementation

1. **Follow the nested service pattern**: Services are accessed via `db.organizations.projects.environments.apiKeys`, not flat.

2. **Authorization flows down**: Environments inherit project permissions, API keys inherit environment permissions. Use `getRole()` from parent service.

3. **Store creator references**: For auditable resources like API keys, store `createdById` to track who created them.

## Testing

1. **Use appropriate fixtures**: `TestOrganizationFixture` < `TestProjectFixture` < `TestEnvironmentFixture`. Each includes users with different role levels.

2. **Test all role levels**: OWNER, ADMIN, DEVELOPER, VIEWER, ANNOTATOR have different permissions.

3. **Test error cases**: Use `Effect.flip` to convert failures to successes for assertion, `MockDrizzleORM` for database errors.

## Common Gotchas

1. **`bun test` vs `bun run test`**: Always use `bun run test` to run vitest properly.

2. **UUID format in tests**: Use valid UUID format (`"00000000-0000-0000-0000-000000000000"`) not arbitrary strings like `"non-existent"`.

3. **PostgreSQL NOTICE messages**: These are suppressed in tests via `onnotice: () => {}` in the postgres client config.

4. **Effect `it.effect` context**: The wrapped `it` from `@/tests/db` automatically provides the database layer.
