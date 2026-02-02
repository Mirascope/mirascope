# AI Agent Context Guide

**Note**: AGENTS.md is the canonical source of truth for AI coding assistant context. It is symlinked to agent-specific locations, like `.claude/CLAUDE.md` and `.cursorrules`.

## Primary Context Sources

When working on this codebase, start by reviewing these documents for high-level context:

1. **[README.md](README.md)**: Overview of the project, installation, development setup, and quick start information.

2. **[STRUCTURE.md](STRUCTURE.md)**: Comprehensive documentation of the codebase structure, including:

- Monorepo organization and benefits
- Detailed file structure for each package (Python SDK, TypeScript SDK, Cloud, Docs)
- Tooling choices and rationale
- Key design decisions and architectural patterns

3. **Directory-specific AGENTS.md files**: Some directories have their own AGENTS.md files:

- `cloud/AGENTS.md`
- `python/AGENTS.md`

Be sure to read these files when they are in scope for project-specific context.

## Codebase Overview

Mirascope is a monorepo containing:

- **Python SDK** (`python/`): The main Python implementation with LLM abstractions
- **TypeScript SDK** (`typescript/`): TypeScript implementation (development paused)
- **Cloud Application** (`cloud/`): Full-stack React application with Cloudflare Workers. If working on `cloud/`, then you MUST read `cloud/AGENTS.md`.
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

4. **Maintain Type Safety**: We place a very high value on type safety. Do not circumvent the type system (e.g. by adding type ignores) except with specific human approval.

## Quick Reference

- **Python Package Manager**: `uv`
- **TypeScript/JS Package Manager**: `bun`
- **Python Testing**: `pytest`
- **TypeScript Testing**: `vitest`
- **Linting**: `ruff` (Python), `oxlint` (TypeScript)
- **Type Checking**: `pyright` (Python), `tsc` (TypeScript)

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
2. `bun run lint:oxlint` passes  
3. `bun run test:coverage` shows 100% coverage
4. OpenAPI spec regenerated if API changed

## Getting Help

If you need more context about:

- **Specific modules or features**: Check the relevant package's README or documentation
- **Architecture decisions**: See `STRUCTURE.md` "Key Design Decisions" section
- **Development workflow**: See `README.md` for CI, testing, and build instructions
- **Cloud Development Instructions**: See `cloud/AGENTS.md` if working on the `cloud/` directory.
