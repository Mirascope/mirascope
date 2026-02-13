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
  ├── Channels (Discord, Telegram, Signal, etc.)
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

## Concrete `_meta.ts` Structure

The new Claws section would be defined as:

```ts
const claws: SectionSpec = {
  slug: "claws",
  label: "Claws",
  children: [
    { slug: "index", label: "Overview" },
    { slug: "quickstart", label: "Quickstart" },
    { slug: "configuration", label: "Configuration" },
    { slug: "channels", label: "Channels" },
    { slug: "skills", label: "Skills" },
    { slug: "memory", label: "Memory & Context" },
    { slug: "tools", label: "Tools" },
    { slug: "deployment", label: "Deployment" },
  ],
};
```

The top-level spec becomes:

```ts
const docs: VersionSpec = {
  sections: [welcome, claws, sdk, v1],
};
```

Where `sdk` wraps the existing `learn`, `guides`, and `api` sections.

## Redirect Table

To avoid breaking existing URLs:

| Old URL | New URL |
|---------|---------|
| `/docs/quickstart` | `/docs/sdk/python/quickstart` |
| `/docs/learn/llm/*` | `/docs/sdk/python/llm/*` |
| `/docs/learn/ops/*` | `/docs/sdk/python/ops/*` |
| `/docs/guides/*` | `/docs/sdk/guides/*` |
| `/docs/api/*` | `/docs/sdk/api/*` |
| `/docs/why` | `/docs/sdk/why` |

All old URLs should 301 redirect to their new locations.

## Timeline Estimates

- **Phase 1** (nav restructure + skeleton): 1-2 days
- **Phase 2** (welcome page rewrite): half day
- **Phase 3** (Claws content): 3-5 days
- **Phase 4** (TS SDK slot): Sebastian's timeline
- Phases 3 and 4 can run in parallel

## Migration Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Broken external links | SEO ranking loss, user confusion | 301 redirects for all moved URLs |
| Search index disruption | Temporary ranking drop | Sitemap update + canonical tags |
| Collision with Sebastian's TS work | Merge conflicts, duplicated effort | Coordinate on `_meta.ts` structure before Phase 4 |
| Incomplete Claws content at launch | Empty placeholder pages look unprofessional | Phase 1 skeleton uses "Coming Soon" markers; don't link from nav until content exists |

## Technical Notes

- Navigation is defined via `_meta.ts` files exporting `SectionSpec` objects (defined in `cloud/app/lib/content/spec.ts`)
- `SectionSpec` supports `slug`, `label`, `children`, and optionally `products` (for language/framework switching)
- The `products` field on `SectionSpec` could be used for Python/TypeScript switching within SDK docs
- Content files are MDX and live in `content/docs/`
