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

## Getting Help

If you need more context about:
- **Specific modules or features**: Check the relevant package's README or documentation
- **Architecture decisions**: See `STRUCTURE.md` "Key Design Decisions" section
- **Development workflow**: See `README.md` for CI, testing, and build instructions

