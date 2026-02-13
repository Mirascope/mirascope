# Documentation Redesign: Claws Front and Center

**Author:** William / Verse  
**Date:** 2025-02-13  
**Status:** Proposal

## Problem

The mirascope.com/docs site is entirely SDK-centric. Every page assumes the reader is a Python developer looking to use the Mirascope LLM toolkit directly. With **Claws** launching as Mirascope's hosted AI agent platform, and **TypeScript SDK** support being added by Sebastian, the documentation needs to be restructured so that:

1. **Claws is the primary product** — most visitors should land on Claws docs first
2. **Mirascope SDK** (Python + TypeScript) is accessible but secondary — it's the toolkit for developers who want to build at a lower level
3. The transition is smooth — existing SDK doc URLs shouldn't break

## Current Top-Level Navigation

```
Welcome
  ├── index (Welcome to Mirascope)
  ├── why
  ├── quickstart
  └── contributing
Learn
  ├── LLM (calls, prompts, tools, agents, streams, etc.)
  └── Ops (tracing, versioning, evals, etc.)
Guides
  ├── Prompt Engineering
  └── Agent Recipes
API Reference
v1 (legacy)
```

The welcome page (`index.mdx`) leads with "Welcome to Mirascope" and focuses on the Python SDK + Cloud dashboard. No Claws documentation exists yet.

## Proposed New Top-Level Navigation

```
Welcome
  ├── index (redesigned — leads with Claws)
  └── contributing
Claws                              ← NEW, front and center
  ├── What are Claws?
  ├── Getting Started
  ├── Configuration
  │   ├── soul.md
  │   ├── Skills
  │   └── Memory
  ├── Deployment
  ├── Managing Claws
  ├── OpenClaw CLI
  ├── Skill Development
  └── Registry
Mirascope SDK                      ← Existing content, reorganized
  ├── Overview (why Mirascope, quickstart)
  ├── Learn
  │   ├── LLM (calls, prompts, tools, agents, etc.)
  │   └── Ops (tracing, versioning, etc.)
  ├── Guides
  │   ├── Prompt Engineering
  │   └── Agent Recipes
  └── API Reference
v1 (legacy, stays as-is)
```

### Key Changes

- **Claws section** is the second item in nav (after Welcome), making it the first real content section visitors see
- **Mirascope SDK** wraps all existing LLM/Ops/Guides/API content under a single section, with Python and TypeScript as sub-paths or tabs
- **Welcome page** is redesigned to lead with Claws
- **v1** stays unchanged

## Welcome Page Redesign

The root `index.mdx` should be restructured:

**Hero section:** "Build and deploy persistent AI agents" — introduces Claws as the headline product. Primary CTA: "Get Started with Claws →"

**Secondary section:** "Build with the Mirascope LLM Toolkit" — for developers who want the SDK directly. Links to Python and TypeScript quickstarts.

**Tertiary:** Links to community, contributing, etc.

## Implementation Plan

### Phase 1: Navigation Restructure + Claws Skeleton

- Update `content/docs/_meta.ts` to add the Claws section and wrap existing content under "Mirascope SDK"
- Create placeholder pages for each Claws doc (`content/docs/claws/`)
- Ensure existing SDK content still renders at new paths
- Add redirects from old paths if URLs change

### Phase 2: Claws Content

- Write "What are Claws?" overview
- Write Getting Started guide (install OpenClaw CLI, create first claw, deploy)
- Write Configuration docs (soul.md format, skill definitions, memory configuration)
- Write Deployment guide (local dev, cloud deployment)
- Write Managing Claws guide (monitoring, updating, versioning)
- Write OpenClaw CLI reference
- Write Skill Development guide
- Write Registry docs

### Phase 3: Welcome Page Rewrite

- Redesign `index.mdx` with Claws-first messaging
- Update hero, CTAs, and feature highlights
- Remove or move SDK-centric welcome content into the Mirascope SDK section

### Phase 4: SDK Content Migration

- Move `why.mdx` and `quickstart.mdx` under SDK section
- Ensure Learn, Guides, and API Reference are properly nested under Mirascope SDK
- Integrate TypeScript SDK docs (Sebastian's work) alongside Python docs
- Update internal cross-references

## Open Questions

1. **URL structure:** Should Claws docs live at `/docs/claws/...` (under the docs umbrella) or `/claws/...` (top-level)? The former is simpler to implement given the current content system; the latter signals Claws as a first-class product.

2. **TypeScript SDK integration:** Should TypeScript be a separate section within Mirascope SDK, or should each page have Python/TypeScript tabs (like many SDK docs do)? Tabs reduce duplication for concepts that are the same across languages, but may be complex to implement.

3. **Blog posts:** Do existing blog posts reference SDK doc URLs that will change? If so, do we update them or rely on redirects?

4. **Search:** How does the restructure affect search indexing? Should we update `sitemap.xml` generation and add `canonical` tags during the migration?

5. **SDK version selector:** Currently v1/v2 is handled via the nav. With the restructure, should the version selector be scoped to the SDK section only?

## Technical Notes

- Navigation is defined via `_meta.ts` files exporting `SectionSpec` objects (defined in `cloud/app/lib/content/spec.ts`)
- `SectionSpec` supports `slug`, `label`, `children`, and optionally `products` (for language/framework switching)
- The `products` field on `SectionSpec` could be used for Python/TypeScript switching within SDK docs
- Content files are MDX and live in `content/docs/`
