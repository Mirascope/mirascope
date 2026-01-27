---
name: blog-v1-deprecation-auditor
description: Interactive workflow for auditing and updating blog posts with deprecated Mirascope v1 API patterns. Use this to scan blog posts, identify issues, and migrate code to v2 patterns.
compatibility: Requires linear-server MCP to be configured for Linear issue tracking features.
---

# Blog Audit and Migration Tool

Interactive multi-phase workflow for auditing and updating blog posts with deprecated Mirascope v1 API patterns.

## Usage

```
/blog-v1-deprecation-auditor
```

This starts an interactive workflow that guides you through:
1. **Audit Report** - Scan all blog posts and see which need updates
2. **Post Selection** (Optional) - Pick a specific post to work through
3. **Code Migration** (Optional) - Rewrite deprecated code with v2 patterns

---

## Phase 1: Generate Audit Summary

### Instructions

1. Run the audit script (summary mode):
   ```bash
   uv run .claude/skills/blog-v1-deprecation-auditor/scripts/audit_posts.py
   ```

2. The script outputs a compact summary:
   - Total posts scanned
   - Posts needing updates (count)
   - Total issues by priority (H/M/L)
   - Numbered list of posts with issues (filename + counts only)

3. Ask the user:
   > "Would you like to select a blog post to work through? Enter a number or 'no' to exit."

4. If user says no, end the workflow. If they enter a number, proceed to Phase 2.

---

## Phase 2: Audit Selected Post

### Instructions

1. **Check Linear for existing sub-issue**:
   - Use `mcp__linear-server__list_issues` with:
     - `parentId`: `ce78a778-d632-43e5-97e4-f01b46bb752c` (GROWTH-51's ID)
     - `query`: the filename (e.g., `engineers-should-handle-prompting-llms.mdx`)
   - If a matching sub-issue exists, note its ID for later status updates
   - If no sub-issue exists, ask the user:
     > "No Linear sub-issue found for this post. Would you like me to create one? (yes/no)"
   - If yes, use `mcp__linear-server__create_issue` with:
     - `title`: `Migrate: <filename>`
     - `team`: `Growth`
     - `parentId`: `ce78a778-d632-43e5-97e4-f01b46bb752c`

2. Run the audit script with the selected file:
   ```bash
   uv run .claude/skills/blog-v1-deprecation-auditor/scripts/audit_posts.py --file <filename>.mdx
   ```

3. This shows detailed issues for that file only:
   - Issues grouped by category
   - Line numbers and found text for each issue

4. Ask the user:
   > "Would you like me to help rewrite the deprecated code blocks in this post? (yes/no)"

5. If user says no, offer to select a different post or end. If yes, proceed to Phase 3.

---

## Phase 3: Interactive Issue Resolution

### Instructions

Iterate through **every issue** from the Phase 2 audit (code blocks, prose, links, images, etc.):

#### For each issue:

1. **Show the issue details**:
   - Category (e.g., "Deprecated Decorator Syntax", "Prose Reference", "Image")
   - Line number and found text
   - Priority level (HIGH/MEDIUM/LOW)

2. **Read surrounding context** from the MDX file using the line numbers.

3. **Offer resolution based on issue type**:

   | Issue Type | Claude's Action |
   |------------|-----------------|
   | **Code block** | Propose rewritten code with v2 patterns, show diff |
   | **Prose/inline code** | Propose updated text |
   | **Link** | Suggest the correct URL |
   | **Image** | Flag for manual review (cannot auto-fix) |

   For code/prose fixes, gather context from:
   - `references/current-patterns.md` for transformation rules
   - `references/api-reference.md` for quick API lookup
   - Python library source (`python/mirascope/llm/__init__.py`, `python/mirascope/ops/__init__.py`) for edge cases

   **IMPORTANT**: Always verify rewritten code against the live docs at https://mirascope.com/docs before proposing. Fetch the relevant doc page to confirm the correct API usage and patterns.

4. **Present user options**:
   > "How would you like to handle this issue?"
   - **"apply"** - Claude applies the proposed fix using the Edit tool
   - **"auto"** - Claude automatically applies all issues that can be auto-fixed (code, prose, links); images are skipped for manual review
   - **"skip"** - Move on without fixing (user may handle later)
   - **"modify"** - User provides feedback, Claude regenerates the fix
   - **"done"** - User already fixed it manually; Claude verifies and moves on

5. **Confirm resolution**:
   > "Mark this issue as resolved? (yes/no)"
   - Track which issues are resolved vs skipped

6. **Move to next issue** and repeat.

#### After all issues in the post:

1. **Show summary**:
   ```
   Issues resolved: X/Y
   Issues skipped: Z
   ```

2. **If all issues resolved**, offer to mark the post complete:
   > "All issues resolved! Add `v2_migration_completed` to frontmatter? (yes/no)"
   - If yes: Add `v2_migration_completed: "YYYY-MM-DD"` (today's date) to frontmatter

3. **Offer next steps**:
   > "Would you like to work on another post or exit?"

---

## Reference Files

- `references/current-patterns.md` - Canonical v2 patterns and transformation rules
- `references/api-reference.md` - Quick API lookup for `llm.*` and `ops.*`
- `references/audit-checklist.md` - Detailed checklist of what to audit

## External References

When rewriting code, consult these sources in order:

1. **Reference files** (above) - For common patterns and transformations
2. **Live docs** at https://mirascope.com/docs - **Always fetch and verify** code rewrites against the relevant doc page
3. **Python library source**:
   - `python/mirascope/llm/__init__.py` - Authoritative `llm.*` API
   - `python/mirascope/ops/__init__.py` - Authoritative `ops.*` API

---

## Priority Levels

- **HIGH**: Lilypad references (deprecated branding), legacy API syntax, prose references to deprecated APIs
- **MEDIUM**: Prose context around flagged code, provider-specific explanations, year references, old docs links, dated models
- **LOW**: Image references (manual review)

---

## Key Transformations

### Imports
```python
# Old
from mirascope.core import openai, anthropic

# New
from mirascope import llm, ops
```

### LLM Calls
```python
# Old
@openai.call("gpt-4o-mini")

# New
@llm.call("openai/gpt-4o-mini")
```

### Messages
```python
# Old
Messages.System("..."), Messages.User("...")

# New
llm.messages.system("..."), llm.messages.user("...")
```

### Tracing (Lilypad -> Mirascope Cloud)
```python
# Old
import lilypad
lilypad.configure(auto_llm=True)
@lilypad.trace(versioning="automatic")

# New
from mirascope import ops
ops.configure()
ops.instrument_llm()
@ops.trace  # or @ops.version for versioning
```

---

## Completion Tracking

### The `v2_migration_completed` Key

When a blog post has been fully migrated to v2 patterns, add this key to its frontmatter:

```yaml
---
title: "My Blog Post"
date: "2024-03-15"
v2_migration_completed: "2026-01-26"
---
```

**Key name**: `v2_migration_completed`

**Value**: ISO date string when the migration was completed (e.g., `"2026-01-26"`)

**Behavior**:
- **Absence** = post needs review (may have issues)
- **Presence** = post has been fully migrated and is excluded from audit lists

**When to add**: At the end of Phase 3, after the user confirms all issues in a post have been addressed.
