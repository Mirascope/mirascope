# Blog Post Audit Checklist

Detailed checklist of patterns detected by the audit script.

## Lilypad (Deprecated) - HIGH Priority

Lilypad is now **Mirascope Cloud**. All Lilypad references need updating.

### Lilypad Import
```regex
import lilypad
```

### Lilypad Configure
```regex
lilypad\.configure\(
```

### Lilypad Trace Decorator
```regex
@lilypad\.trace\(
```

### Lilypad Documentation Links
```regex
\(/docs/lilypad
```

### Lilypad Screenshots
```regex
!\[.*\]\(/assets/blog/[^)]*lilypad[^)]*\)
```

### Lilypad Product Description
```regex
Lilypad is
```

## Legacy API (v1) - HIGH Priority

### Import from mirascope.core (general)
```regex
from mirascope\.core import
```

### Provider-Specific Imports
```regex
from mirascope\.core import (openai|anthropic|gemini|mistral|groq|cohere|litellm|azure|vertex|bedrock)
```

### Messages Import
```regex
from mirascope\.core import.*Messages
```

### Provider-Specific Decorators
```regex
@openai\.call\(
@anthropic\.call\(
@gemini\.call\(
@(mistral|groq|cohere|litellm|azure|vertex|bedrock)\.call\(
```

## Year References - MEDIUM Priority

### Outdated Year in Title
```regex
^title:.*\b(202[0-5])\b
```

**Note:** Flags any year before 2026 (2020-2025).

## Model Names - MEDIUM Priority

### Dated Anthropic Models
```regex
claude-3-5-sonnet-\d{8}
claude-3-opus-\d{8}
claude-3-sonnet-\d{8}
claude-3-haiku-\d{8}
```

## Documentation Links - HIGH/MEDIUM Priority

### Invalid /docs/mirascope Path (HIGH)
```regex
\(/docs/mirascope[/)]
```
This path doesn't exist in v2. All docs are rooted at `/docs/` directly.

**Fix:** Remove `/mirascope` from the path, or link to the docs root.
- OLD: `/docs/mirascope` or `/docs/mirascope/tools/`
- NEW: `/docs` or `/docs/tools/`

### Legacy v1 Docs (HIGH)
```regex
\(/docs/v1/
```
NEVER link to legacy v1 documentation.

**Fix:** Update to current v2 documentation path.

### Specific Guide Links (MEDIUM)
```regex
\(/docs/guides/[^)]+\)
```
Individual guide pages are not ready yet. Link to the guides index instead.

**Fix:** Use `/docs/guides` (index page with under construction notice).
- OLD: `/docs/guides/structured-outputs`
- NEW: `/docs/guides`

## Image References - HIGH Priority

### Blog Images
```regex
!\[.*\]\(/assets/blog/
```

**Note:** Flagged for manual review (may be outdated UI screenshots).

---

## Prose References - HIGH Priority

When code patterns are deprecated, the surrounding prose that explains those patterns also needs updating. These patterns detect inline code references and feature descriptions in prose.

### Inline Code References to Deprecated APIs
Backtick-wrapped references to deprecated APIs in prose text:
```regex
`@openai\.call`
`@anthropic\.call`
`@(gemini|mistral|groq|cohere|litellm|azure|vertex|bedrock)\.call`
`mirascope\.core`
`@?lilypad\.(trace|configure)`
```

**Example prose that would be flagged:**
> "The call decorator `@openai.call` directs the LLM to use GPT-4o Mini"

### Lilypad Feature Descriptions
Sentences describing what Lilypad does:
```regex
Lilypad (traces|versions|provides|enables|allows|offers|helps|lets|'s)
```

**Example prose that would be flagged:**
> "Lilypad traces both at the level of the API and at the level of each function"

---

## Response API (v1) - HIGH Priority

The way to serialize/dump responses changed in v2.

### Old Response Dump Pattern
```regex
\.model_dump\(\)
```

**Example code that would be flagged:**
```python
response = recommend_book("fantasy")
print(response.model_dump())  # v1 pattern - flagged

explanation = get_explanation()
print(explanation.model_dump())  # Also flagged (any variable name)
```

**Correct v2 pattern:**
```python
response = recommend_book("fantasy")
print(response.raw.model_dump_json(indent=2))  # v2 pattern
```

### Inline Code Reference
```regex
`[a-z_]+\.model_dump\(\)`
```

**Note:** This pattern may produce some false positives (e.g., Pydantic BaseModel dumps for structured output). Review in context.

**Provider compatibility:** `model_dump_json()` works for Pydantic-based providers (OpenAI, Anthropic, Ollama, Together). For Google/MLX, use provider-specific serialization.

---

## Prose (API Design) - MEDIUM Priority

### Provider-Specific Pattern Explanations
Prose explaining the old provider-specific decorator pattern:
```regex
provider[- ]specific (decorator|call|import|API)
```

**Example prose that would be flagged:**
> "is provider agnostic: we could've instead written, e.g., `anthropic.call`, `google.call`"

---

## Prose Context - MEDIUM Priority

### Context Near Flagged Code Blocks
When a code block contains deprecated patterns, the 3 lines before and after
are automatically flagged for review. These often contain explanations that
need updating alongside the code.

**Why this matters:**
Code blocks rarely appear in isolation. The surrounding prose typically:
- Introduces what the code does (before the block)
- Explains the output or behavior (after the block)

When the code changes, these explanations often need semantic updates too.

---

## Priority Levels

### HIGH - Fix immediately
- **Lilypad references** - deprecated branding, docs no longer available
- Legacy API syntax (imports, decorators from mirascope.core)

### MEDIUM - Fix soon
- Year references in titles (flags pre-2026)
- Dated model versions in code examples
- Old documentation link patterns (/docs/v1/)

### LOW - Fix when convenient
- (No items currently at LOW priority)

---

## Patterns NOT Currently Implemented

The following patterns are mentioned in documentation but not detected by the audit script:

- Frontmatter date validation
- Internal blog link verification
- External link checking

These require manual review or separate tooling.
