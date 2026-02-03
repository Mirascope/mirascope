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

## Batch Mode

For processing multiple posts in parallel across instances:

### Invocation

```
/blog-v1-deprecation-auditor --batch 1/3
```

Where `1/3` means "batch 1 of 3 total batches".

### Behavior

In batch mode:
- Posts are sorted alphabetically by title (case-insensitive)
- Posts are assigned to batches via modulo (predictable, stable assignment)
- All interactive prompts are skipped
- Claude rewrites all deprecated code blocks using the same logic as interactive mode
- "auto" mode is the default - Claude applies all fixes without confirmation
- Linear issues are created automatically (no confirmation)
- `updatedAt` is added to frontmatter after successful migration

### Parallel Execution

Run multiple instances simultaneously:
- Instance 1: `/blog-v1-deprecation-auditor --batch 1/3`
- Instance 2: `/blog-v1-deprecation-auditor --batch 2/3`
- Instance 3: `/blog-v1-deprecation-auditor --batch 3/3`

Each instance processes ~1/3 of the posts with no overlap.

### Post Assignment Algorithm

Posts are assigned using modulo distribution:
- Posts are filtered to only those with issues and no `updatedAt`
- Posts are sorted by title (case-insensitive) for stable ordering
- Post at index `i` goes to batch `(i % total_batches) + 1`

Example with 52 posts and 3 batches:
- Batch 1: posts 0, 3, 6, 9, ... (indices where i % 3 == 0) → ~18 posts
- Batch 2: posts 1, 4, 7, 10, ... (indices where i % 3 == 1) → ~17 posts
- Batch 3: posts 2, 5, 8, 11, ... (indices where i % 3 == 2) → ~17 posts

---

## Phase 1: Generate Audit Summary

### Instructions

1. Run snippet extraction to validate code block types:
   ```bash
   cd cloud && bun run generate:snippets --blog
   ```
   This validates that all Python code blocks use supported types (`python`, `python-snippet-concat`, `python-snippet-skip`). Any unsupported block types will be reported as errors.

2. Run the audit script (summary mode). **IMPORTANT**: Use the absolute path from the skill's base directory:
   ```bash
   uv run "$(git rev-parse --show-toplevel)/.claude/skills/blog-v1-deprecation-auditor/scripts/audit_posts.py"
   ```

4. The script outputs a compact summary:
   - Total posts scanned
   - Posts needing updates (count)
   - Total issues by priority (H/M/L)
   - Numbered list of posts with issues (filename + counts only)

5. Ask the user:
   > "Would you like to select a blog post to work through? Enter a number or 'no' to exit."

6. If user says no, end the workflow. If they enter a number, proceed to Phase 2.

---

## Phase 2: Audit Selected Post

### Instructions

1. **ALWAYS Check Linear for existing sub-issue FIRST**:
   - **MANDATORY**: You MUST check for existing issues before ANY creation attempt
   - Use `mcp__linear-server__list_issues` with:
     - `parentId`: `ce78a778-d632-43e5-97e4-f01b46bb752c` (GROWTH-51's ID)
     - `query`: the filename (e.g., `engineers-should-handle-prompting-llms.mdx`)
   - If a matching sub-issue exists, note its ID - do NOT create a new issue
   - If no sub-issue exists, ask the user:
     > "No Linear sub-issue found for this post. Would you like me to create one? (yes/no)"
   - If yes, use `mcp__linear-server__create_issue` with:
     - `title`: `Migrate: <filename>`
     - `team`: `Growth`
     - `parentId`: `ce78a778-d632-43e5-97e4-f01b46bb752c`

2. Run the audit script with the selected file:
   ```bash
   uv run "$(git rev-parse --show-toplevel)/.claude/skills/blog-v1-deprecation-auditor/scripts/audit_posts.py" --file <filename>.mdx
   ```

3. This shows detailed issues for that file only:
   - Issues grouped by category
   - Line numbers and found text for each issue

4. Ask the user:
   > "Would you like me to help rewrite the deprecated code blocks in this post? (yes/no)"

5. If user says no, offer to select a different post or end. If yes, proceed to Phase 3.

**IMPORTANT: Linear Issue Status**
- NEVER mark Linear issues as "Done" or change their status
- Only update the issue description with migration notes/summary
- Leave status changes to humans for final review

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

   **CRITICAL: Style Guide Verification**
   Before proposing ANY code fix, you MUST:
   1. Read `references/current-patterns.md` completely
   2. Check ALL style guidelines, not just API patterns. Key style rules include:
      - Response text access: Break up chained calls (e.g., `print(func().text())` → separate assignment + print)
      - Code formatting and readability patterns
   3. Compare EVERY code block in the post against these style guidelines
   4. Fix style violations even if the audit script didn't flag them

   **IMPORTANT**: Always verify rewritten code against the live docs at https://mirascope.com/docs before proposing. Fetch the relevant doc page to confirm the correct API usage and patterns.

4. **Present user options**:
   > "How would you like to handle this issue? (apply / auto / skip / modify / done)"

   - **"apply"** - Claude applies the proposed fix using the Edit tool
   - **"auto"** - Claude automatically applies all remaining issues that can be auto-fixed (code, prose, links); images are skipped for manual review
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

2. **Validate snippet extraction** for the updated file:
   ```bash
   cd cloud && bun run generate:snippets --file=../content/blog/<filename>.mdx
   ```
   This confirms all code blocks can be extracted successfully after migration.

3. **Type check and lint the extracted snippet**:
   ```bash
   cd cloud && bun run validate:snippets --path=.extracted-snippets/blog/<post-slug>/
   ```
   This confirms the migrated code passes pyright type checking and ruff linting.

3. **If all issues resolved**, offer to mark the post complete:
   > "All issues resolved! Add `updatedAt` to frontmatter? (yes/no)"
   - If yes: Add `updatedAt: "YYYY-MM-DD"` (today's date) to frontmatter

4. **Offer next steps**:
   > "Would you like to work on another post or exit?"

---

## Batch Mode Phases

When `--batch N/M` is provided, follow these non-interactive phases instead:

### Batch Phase 1: Get Assigned Posts

1. Run snippet extraction to validate code block types:
   ```bash
   cd cloud && bun run generate:snippets --blog
   ```
   This validates all blog posts have valid Python block types.

2. Run the audit script with batch argument:
   ```bash
   uv run "$(git rev-parse --show-toplevel)/.claude/skills/blog-v1-deprecation-auditor/scripts/audit_posts.py" --batch N/M
   ```

4. The script outputs:
   - Batch identifier (e.g., "Batch 1/3")
   - Number of posts assigned
   - Numbered list of posts sorted by title

5. **No user prompt** - proceed directly to processing each post sequentially.

### Batch Phase 2: Process Each Post

For each post in the batch, perform these steps automatically:

#### 2a. Check/Create Linear Issue (Auto)

1. **ALWAYS check for existing sub-issue FIRST** under GROWTH-51:
   - **MANDATORY**: You MUST check for existing issues before ANY creation attempt
   - Use `mcp__linear-server__list_issues` with `parentId: ce78a778-d632-43e5-97e4-f01b46bb752c` and `query: <filename>`
   - If a matching sub-issue exists, note its ID - do NOT create a new issue

2. **Only if no existing issue found**, create one automatically:
   - Use `mcp__linear-server__create_issue` with:
     - `title`: `Migrate: <filename>`
     - `team`: `Growth`
     - `parentId`: `ce78a778-d632-43e5-97e4-f01b46bb752c`

**IMPORTANT: Linear Issue Status**
- NEVER mark Linear issues as "Done" or change their status
- Only update the issue description with migration notes/summary
- Leave status changes to humans for final review

#### 2b. Run Detailed Audit

1. Run:
   ```bash
   uv run "$(git rev-parse --show-toplevel)/.claude/skills/blog-v1-deprecation-auditor/scripts/audit_posts.py" --file <filename>.mdx
   ```

2. Note all issues by category and line number.

### Batch Phase 3: Auto-Fix All Issues

For the current post, iterate through every issue and apply fixes automatically:

#### For each issue:

1. **Note the issue details** (from audit output):
   - Category (e.g., "Deprecated Decorator Syntax", "Prose Reference", "Image")
   - Line number and found text
   - Priority level (HIGH/MEDIUM/LOW)

2. **Read surrounding context** from the MDX file using the line numbers.

3. **Apply the appropriate fix**:

   | Issue Type | Auto Action |
   |------------|-------------|
   | **Code block** | Rewrite with v2 patterns using Edit tool |
   | **Prose/inline code** | Update text using Edit tool |
   | **Link** | Replace with correct URL using Edit tool |
   | **Image** | **Skip** - flag in final summary for manual review |

   For code/prose fixes, gather context from:
   - `references/current-patterns.md` for transformation rules
   - `references/api-reference.md` for quick API lookup
   - Python library source (`python/mirascope/llm/__init__.py`, `python/mirascope/ops/__init__.py`) for edge cases

   **CRITICAL: Style Guide Verification**
   Before applying ANY code fix, you MUST:
   1. Read `references/current-patterns.md` completely
   2. Check ALL style guidelines, not just API patterns. Key style rules include:
      - Response text access: Break up chained calls (e.g., `print(func().text())` → separate assignment + print)
      - Code formatting and readability patterns
   3. Compare EVERY code block in the post against these style guidelines
   4. Fix style violations even if the audit script didn't flag them

   **IMPORTANT**: Always verify rewritten code against the live docs at https://mirascope.com/docs. Fetch the relevant doc page to confirm the correct API usage and patterns.

4. **Move to next issue** and repeat.

#### After all issues in the post:

1. **Validate snippet extraction** for the updated file:
   ```bash
   cd cloud && bun run generate:snippets --file=../content/blog/<filename>.mdx
   ```

2. **Type check and lint the extracted snippet**:
   ```bash
   cd cloud && bun run validate:snippets --path=.extracted-snippets/blog/<post-slug>/
   ```

3. **Mark post complete**:
   - Add `updatedAt: "YYYY-MM-DD"` to frontmatter (today's date)
   - Report: "Completed: <filename> (X issues fixed, Y images skipped)"

4. **Move to next post** in the batch.

### Batch Phase 4: Final Summary

After all posts in the batch are processed:

1. **Run full validation on all blog snippets**:
   ```bash
   cd cloud && bun run validate:snippets --path=.extracted-snippets/blog/
   ```
   This ensures all migrated posts pass type checking and linting.

2. **Output a summary**:

```
# Batch N/M Complete

## Posts Processed: X

| Post | Issues Fixed | Images Skipped | Status |
|------|--------------|----------------|--------|
| post-1.mdx | 12 | 1 | ✓ Complete |
| post-2.mdx | 8 | 0 | ✓ Complete |
| post-3.mdx | 15 | 2 | ✓ Complete |

## Items Requiring Manual Review

- post-1.mdx: 1 image at line 45
- post-3.mdx: 2 images at lines 78, 156
```

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

### The `updatedAt` Key

When a blog post has been fully migrated to v2 patterns, add this key to its frontmatter:

```yaml
---
title: "My Blog Post"
date: "2024-03-15"
updatedAt: "2026-01-26"
---
```

**Key name**: `updatedAt`

**Value**: ISO date string when the migration was completed (e.g., `"2026-01-26"`)

**Behavior**:
- **Absence** = post needs review (may have issues)
- **Presence** = post has been fully migrated and is excluded from audit lists

**When to add**: At the end of Phase 3, after the user confirms all issues in a post have been addressed.
