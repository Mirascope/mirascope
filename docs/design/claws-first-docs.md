# Design Doc: Claws-First Documentation Restructure

**Author:** Sazed  
**Date:** 2026-02-13  
**Status:** Draft — Awaiting Review  
**Reviewers:** William, Sebastian

---

## Problem

The docs at mirascope.com/docs are currently structured around the Python SDK ("Mirascope v2"). Claws — our managed AI agent deployment product — have no documentation presence at all. As Claws become central to the product, the docs need to reflect that. The current welcome page, navigation hierarchy, and information architecture all assume the reader is a Python developer looking for an LLM library, not someone looking to deploy or manage AI agents.

With Sebastian adding TypeScript SDK docs, this is the right time to restructure rather than bolt more content onto a Python-centric frame.

## Goals

1. **Claws front-and-center.** The welcome page and primary navigation should lead with Claws — what they are, how to create one, how to manage them.
2. **SDK docs accessible but secondary.** Python and TypeScript SDK docs remain fully available as a "Learn" or "SDK" section — something you navigate *to*, not through.
3. **Clear product hierarchy.** Visitor mental model: Mirascope Cloud → Claws (deploy agents) → SDKs (build the code that runs in them).
4. **No content loss.** All existing docs remain; this is a restructure, not a rewrite.
5. **TypeScript-ready.** Structure accommodates the incoming TS SDK docs naturally.

## Non-Goals

- Writing all Claws documentation content (that's a follow-up).
- Redesigning the visual theme or component library.
- Changing the docs framework (Fumadocs / MDX).

## Current Structure

```
Welcome (root)
├── Welcome
├── Why Mirascope?
├── Mirascope Quickstart
└── Contributing

Learn
├── LLM (Python SDK concepts)
│   ├── Messages, Models, Responses, Prompts, Calls...
│   └── Tools, Structured Output, Streaming, Agents, MCP...
└── Ops
    ├── Configuration, Tracing, Sessions...
    └── Versioning, Instrumentation...

Guides (minimal)
API Reference (LLM + Ops)
v1 (legacy)
```

**Problems:**
- No Claws section at all
- Welcome page is SDK-focused ("Install Mirascope", "Your First Agent" code snippet)
- "Learn" implies SDK learning, not product understanding
- Navigation gives equal weight to legacy v1 and current content

## Proposed Structure

```
Welcome (root)
├── Welcome                    ← NEW: Product overview (Claws + SDKs + Cloud)
├── Why Mirascope?             ← Updated to include Claws value prop
└── Contributing

Claws                          ← NEW top-level section
├── Overview                   ← What Claws are, architecture diagram
├── Quickstart                 ← Create your first Claw (Cloud UI flow)
├── Configuration              ← SOUL.md, AGENTS.md, skills, channels
├── Channels                   ← Discord, Telegram, Signal, etc.
├── Skills                     ← Installing and creating skills
├── Memory & Context           ← MEMORY.md, coppermind patterns
├── Tools                      ← Browser, nodes, cron, messaging
├── Deployment                 ← Instance types, scaling, limits
└── API                        ← Claws management API reference

SDK                            ← Renamed from "Learn", houses both languages
├── Python
│   ├── Quickstart             ← Current "Mirascope Quickstart"
│   ├── LLM                    ← Current Learn/LLM (all pages intact)
│   └── Ops                    ← Current Learn/Ops (all pages intact)
├── TypeScript                 ← NEW: Sebastian's incoming TS docs
│   ├── Quickstart
│   ├── LLM
│   └── Ops
└── Guides                     ← Current Guides section

API Reference                  ← Existing, add language tabs
v1 (legacy)                    ← Existing, no changes
```

## Implementation Plan

### Phase 1: Restructure Navigation (no new content)

**Changes to `content/docs/_meta.ts`:**

```ts
const welcome: SectionSpec = {
  slug: "index",
  label: "Welcome",
  children: [
    { slug: "index", label: "Welcome" },
    { slug: "why", label: "Why Mirascope?" },
    { slug: "contributing", label: "Contributing" },
  ],
};

// NEW
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

// Renamed, restructured for multi-language
const sdk: SectionSpec = {
  slug: "sdk",
  label: "SDK",
  products: [
    { slug: "python", label: "Python" },
    { slug: "typescript", label: "TypeScript" },
  ],
  children: [python, typescript, guides],
};

export const docsSpec: FullDocsSpec = [
  { sections: [welcome, claws, sdk, api, v1] }
];
```

**File moves:**
- `content/docs/quickstart.mdx` → `content/docs/sdk/python/quickstart.mdx`
- `content/docs/learn/llm/` → `content/docs/sdk/python/llm/`
- `content/docs/learn/ops/` → `content/docs/sdk/python/ops/`
- `content/docs/guides/` → `content/docs/sdk/guides/`
- New directory: `content/docs/claws/`
- New directory: `content/docs/sdk/typescript/` (placeholder for Sebastian)

**URL redirects needed:**
| Old URL | New URL |
|---------|---------|
| `/docs/quickstart` | `/docs/sdk/python/quickstart` |
| `/docs/learn/llm/*` | `/docs/sdk/python/llm/*` |
| `/docs/learn/ops/*` | `/docs/sdk/python/ops/*` |
| `/docs/guides/*` | `/docs/sdk/guides/*` |

### Phase 2: New Welcome Page

Rewrite `content/docs/index.mdx` to be product-oriented:

```
# Welcome to Mirascope

Build, deploy, and manage AI agents.

## Claws — Deploy AI Agents Instantly
[Brief description + CTA to Claws docs]

## SDKs — Build with Python or TypeScript
[Brief description + CTA to SDK quickstarts]

## Cloud — Monitor and Manage
[Brief description + CTA to Cloud dashboard]
```

The current welcome page content (install instructions, first agent code) moves to the Python SDK quickstart where it belongs.

### Phase 3: Claws Content

Write the actual Claws documentation pages. Content sources:
- OpenClaw README and docs (`node_modules/openclaw/docs/`)
- `AGENTS.md`, `SOUL.md`, `HEARTBEAT.md` conventions
- Existing `cloud/claws/README.md` (architecture)
- Channel configuration patterns from live Claws

Priority order for content writing:
1. **Overview** — what Claws are, who they're for
2. **Quickstart** — create a Claw via Cloud UI, connect to Discord
3. **Configuration** — the file-based config system
4. **Channels** — supported platforms, setup guides
5. **Everything else** — iterative

### Phase 4: TypeScript SDK Slot

Sebastian fills in `content/docs/sdk/typescript/` with his TS docs. The structure is already waiting for him.

## URL Strategy

Use server-side redirects (not client-side) for all moved pages. This preserves SEO and existing bookmarks/links. Implementation depends on hosting — likely Cloudflare Workers `_redirects` or route rules.

## Migration Risks

| Risk | Mitigation |
|------|------------|
| Broken external links to `/docs/learn/*` | Redirects in Phase 1 |
| SEO impact from URL changes | 301 redirects, update sitemap |
| Sebastian's TS work collides with restructure | Coordinate — he can work in `content/docs/sdk/typescript/` from the start |
| Scope creep into content writing | Phases are sequential; Phase 1 is structure-only |

## Open Questions

1. **Should "Guides" stay SDK-scoped or become top-level?** Current guides are minimal. If we expect Claws guides too (e.g., "Build a customer support Claw"), a top-level Guides section spanning both Claws and SDKs might be better.
2. **API Reference splitting.** Should the Claws management API live under the Claws section or the shared API Reference section?
3. **v1 de-emphasis.** Should v1 be moved further down or behind a "Legacy" collapse? It's still useful content but shouldn't distract from the current product.

## Timeline

| Phase | Effort | Dependencies |
|-------|--------|-------------|
| Phase 1: Navigation restructure | 1-2 days | None |
| Phase 2: Welcome page rewrite | Half day | Phase 1 |
| Phase 3: Claws content | 3-5 days | Phase 1 |
| Phase 4: TypeScript SDK | Sebastian's timeline | Phase 1 |

Phases 3 and 4 can run in parallel once Phase 1 lands.
