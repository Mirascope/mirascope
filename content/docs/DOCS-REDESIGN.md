# Documentation Redesign: Claws Front and Center

**Author:** William / Verse  
**Date:** 2026-02-13  
**Status:** Approved

## Problem

The mirascope.com/docs site is entirely SDK-centric. Every page assumes the reader is a Python developer looking to use the Mirascope LLM toolkit directly. With **Claws** launching as Mirascope's hosted AI agent platform, and **TypeScript SDK** support being added by Sebastian, the documentation needs to be restructured so that:

1. **Claws is the primary product** — the docs landing page should be about Claws
2. **Mirascope SDK** (Python + TypeScript) is accessible but secondary — for developers who want to build at a lower level
3. The transition is smooth — existing SDK doc URLs shouldn't break

## Current Top-Level Navigation

```
Welcome (slug: "index" — landing page at /docs)
  ├── index (Welcome to Mirascope)
  ├── why
  ├── quickstart
  └── contributing
Learn
  ├── LLM (calls, prompts, tools, agents, streams, etc.)
  └── Ops (tracing, versioning, evals, etc.)
Guides
  └── Overview
API Reference
  ├── LLM
  └── Ops
v1 (legacy)
```

## New Top-Level Navigation

```
Claws (slug: "index" — landing page at /docs)
  ├── index (Welcome / What are Claws?)
  ├── quickstart
  ├── configuration
  ├── channels (Discord, Telegram, Signal, etc.)
  ├── skills
  ├── memory
  ├── tools
  ├── deployment
  └── contributing
Guides (top-level, stays as-is)
  └── Overview
SDK (renamed from Learn, 1:1 content)
  ├── LLM (calls, prompts, tools, agents, etc.)
  └── Ops (tracing, versioning, etc.)
API Reference (stays as-is)
  ├── LLM
  └── Ops
```

### Key Changes

1. **Claws replaces Welcome** as the `slug: "index"` section — it becomes the `/docs` landing page and all claws content lives at `/docs/<page>` (top-level URLs)
2. **Learn → SDK** — renamed, content is 1:1. SDK pages live at `/docs/sdk/llm/*` and `/docs/sdk/ops/*`
3. **Guides** stays top-level at `/docs/guides/*`
4. **API Reference** stays top-level at `/docs/api/*`
5. **v1** — no longer in top-level nav. Add a small note in the SDK section pointing to `/docs/v1/*` for those who need it
6. Current Welcome content (`why.mdx`, `quickstart.mdx`) moves into SDK or is rewritten for Claws

## `_meta.ts` Structure

### `content/docs/_meta.ts`

```ts
const claws: SectionSpec = {
  slug: "index",
  label: "Claws",
  children: [
    { slug: "index", label: "Welcome" },
    { slug: "quickstart", label: "Quickstart" },
    { slug: "configuration", label: "Configuration" },
    { slug: "channels", label: "Channels" },
    { slug: "skills", label: "Skills" },
    { slug: "memory", label: "Memory & Context" },
    { slug: "tools", label: "Tools" },
    { slug: "deployment", label: "Deployment" },
    { slug: "contributing", label: "Contributing" },
  ],
};

const docs: VersionSpec = {
  sections: [claws, guides, sdk, api],
};
```

### `content/docs/learn/_meta.ts` → rename to SDK

```ts
const sdk: SectionSpec = {
  slug: "sdk",
  label: "SDK",
  products: [
    { slug: "llm", label: "LLM" },
    { slug: "ops", label: "Ops" },
  ],
  children: [llm, ops],
};
```

## URL Changes

| Old URL | New URL | Action |
|---------|---------|--------|
| `/docs` (Welcome to Mirascope) | `/docs` (Claws landing) | Rewrite content |
| `/docs/why` | `/docs/sdk/why` or remove | Move or drop |
| `/docs/quickstart` | `/docs/quickstart` (Claws quickstart) | Rewrite content |
| `/docs/learn/llm/*` | `/docs/sdk/llm/*` | Redirect (learn → sdk) |
| `/docs/learn/ops/*` | `/docs/sdk/ops/*` | Redirect (learn → sdk) |
| `/docs/guides/*` | `/docs/guides/*` | No change |
| `/docs/api/*` | `/docs/api/*` | No change |
| `/docs/v1/*` | `/docs/v1/*` | No change (just hidden from nav) |

Only the `learn → sdk` rename needs redirects. Guides and API Reference URLs are unchanged.

## Implementation Plan

### Phase 1: Nav Restructure (this PR stack)

1. Rename `learn` section to `sdk` in `_meta.ts`
2. Rename `content/docs/learn/` directory to `content/docs/sdk/`
3. Replace `welcome` section with `claws` section (slug: "index")
4. Create Claws skeleton pages (placeholder content)
5. Move `contributing.mdx` into Claws section
6. Remove v1 from top-level `sections` array (content stays, just not in nav)
7. Add `learn → sdk` redirect

### Phase 2: Claws Content

- Write proper Claws landing page (replaces current Welcome)
- Write Claws quickstart (install CLI, create first claw, deploy)
- Write configuration docs (soul.md, AGENTS.md, config file)
- Write channels guide (Discord, Telegram, Signal setup)
- Write skills docs (creating, installing, registry)
- Write memory docs (MEMORY.md, daily files, context management)
- Write tools docs (built-in tools, custom tools)
- Write deployment guide (local dev, cloud hosting)

### Phase 3: SDK Polish

- Add note in SDK section pointing to v1 for legacy users
- Integrate TypeScript SDK content (coordinate with Sebastian)
- Update any internal cross-references

## Timeline

- **Phase 1** (nav restructure): 1 day
- **Phase 2** (Claws content): 3-5 days
- **Phase 3** (SDK polish + TS): Sebastian's timeline
- Phases 2 and 3 can run in parallel

## Migration Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Broken `/docs/learn/*` links | 404s for bookmarked/shared URLs | 301 redirects to `/docs/sdk/*` |
| Collision with Sebastian's TS work | Merge conflicts in `_meta.ts` | Coordinate: TS goes into SDK section's products |
| Incomplete Claws content | Empty pages look bad | Placeholder content with "Coming Soon"; only link pages with real content from nav |
