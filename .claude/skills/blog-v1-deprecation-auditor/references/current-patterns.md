# Current Correct Patterns

This document defines the canonical, up-to-date patterns that blog posts should use.

## External References

For detailed examples and edge cases:
- **Live docs**: https://mirascope.com/docs (use WebFetch to query)
- **Python library source** (authoritative API signatures):
  - `python/mirascope/llm/__init__.py` - All `llm.*` exports
  - `python/mirascope/ops/__init__.py` - All `ops.*` exports

## Mirascope API Patterns

### Imports

**Current (correct):**
```python
from mirascope import llm, ops
```

**Legacy v1 (needs update):**
```python
from mirascope.core import openai, prompt_template
from mirascope.core import anthropic
from mirascope.core import Messages
```

### LLM Call Decorator

**Current (correct) - model format is "provider/model":**
```python
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."

@llm.call("anthropic/claude-sonnet-4-20250514")
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."
```

**Legacy v1 (needs update):**
```python
@openai.call("gpt-4o-mini")
def my_function(): ...

@anthropic.call("claude-3-5-sonnet-20240620")
def my_function(): ...
```

### Messages

**Current (correct):**
```python
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return [
        llm.messages.system("Always recommend kid-friendly books."),
        llm.messages.user(f"Please recommend a book in {genre}."),
    ]
```

**Legacy v1 (needs update):**
```python
from mirascope.core import Messages

@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return [
        Messages.System("Always recommend kid-friendly books."),
        Messages.User(f"Please recommend a book in {genre}."),
    ]
```

### Response Objects

**Current (correct) - use raw provider response:**
```python
response = recommend_book("fantasy")
print(response.raw.model_dump_json(indent=2))
```

**Legacy v1 (needs update):**
```python
response = recommend_book("fantasy")
print(response.model_dump())  # Any variable.model_dump() on a response
```

**Note:** The audit flags any `.model_dump()` call as it may indicate v1 response handling. Some false positives are possible (e.g., Pydantic BaseModel dumps for structured output), but these should be reviewed in context.

**Important:** `model_dump_json()` only works for providers that use Pydantic models internally:
- **Pydantic providers** (use `model_dump_json()`): OpenAI, Anthropic, Ollama, Together
- **Non-Pydantic providers** (need custom serialization): Google (uses protobuf), MLX (local)

For Google/MLX, use provider-specific serialization methods or `json.dumps()` with custom handling.

### Tracing & Versioning (Mirascope Cloud)

**Current (correct):**
```python
from mirascope import llm, ops

ops.configure()           # Connect to Mirascope Cloud
ops.instrument_llm()      # Auto-trace all LLM calls

@ops.trace                # Trace a function
def my_function(): ...

@ops.version              # Version + trace a function
@llm.call("openai/gpt-4o-mini")
def my_call(): ...
```

**Deprecated Lilypad (needs update):**
```python
import lilypad
lilypad.configure(auto_llm=True)

@lilypad.trace(versioning="automatic")
@openai.call("gpt-4o-mini")
def my_call(): ...
```

## Model Names

### OpenAI Models
- `gpt-4o` - Current flagship
- `gpt-4o-mini` - Current efficient model
- `o1` - Reasoning model
- `o1-mini` - Efficient reasoning model

### Anthropic Models
**Current naming:**
- `claude-sonnet-4-20250514` - Latest Sonnet
- `claude-opus-4-20250514` - Latest Opus
- `claude-3-5-haiku-20241022` - Haiku

**Deprecated (dated versions):**
- `claude-3-5-sonnet-20240620` - Should update to current
- `claude-3-opus-20240229` - Should update to current

### Google Models
- `gemini-2.0-flash` - Current fast model
- `gemini-1.5-pro` - Pro model

## Year References

Current year for titles: **2025** (update annually)

Posts with year in title should be reviewed annually:
- Update year in title
- Review content for accuracy
- Update frontmatter date if significant changes

## Documentation Links

### Valid v2 Documentation Paths
- `/docs/` - Docs root
- `/docs/learn/llm/...` - LLM documentation
- `/docs/learn/ops` - Observability/tracing docs (formerly Lilypad)
- `/docs/api/...` - API reference
- `/docs/guides` - Guides index (under construction)
- `/blog/...` - Internal blog links

### Invalid Paths (Will Be Flagged)
- `/docs/mirascope/...` - Does not exist in v2, use `/docs/...`
- `/docs/guides/<specific-guide>` - Guides not ready, use `/docs/guides` only
- `/docs/v1/...` - Legacy docs, NEVER link
- `/docs/lilypad` - Deprecated, now `/docs/learn/ops`

## Product Descriptions

### Mirascope
"Mirascope is a lightweight Python toolkit for building LLM applications."

### Mirascope Cloud (formerly Lilypad)
Lilypad functionality is now part of **Mirascope Cloud**. References to "Lilypad" as a standalone product are outdated.

## Code Block Annotations

Use Shiki annotations for highlighting:
```python
@llm.call("openai/gpt-4o-mini")  # [!code highlight]
```

## Prose Patterns

When updating code examples, the surrounding prose often needs semantic updates too.

### Inline Code References in Prose

**Legacy prose (needs update):**
> The call decorator `@openai.call` directs the LLM to use GPT-4o Mini

**Updated prose:**
> The call decorator `@llm.call("openai/gpt-4o-mini")` directs the LLM to use GPT-4o Mini

### API Design Explanations

**Legacy prose (needs update):**
> is provider agnostic: we could've instead written, e.g., `anthropic.call`, `google.call`

**Updated prose:**
> is provider agnostic: we could've instead written, e.g., `@llm.call("anthropic/claude-sonnet-4-20250514")`

### Lilypad Feature Descriptions

**Legacy prose (needs update):**
> Lilypad traces both at the level of the API and at the level of each function decorated by `@lilypad.trace()`

**Updated prose:**
> Mirascope Cloud traces both at the level of the API (via `ops.instrument_llm()`) and at the level of each function decorated by `@ops.trace`

**Legacy prose (needs update):**
> Lilypad's code-first approach unifies version control, LLM evaluation, and collaboration

**Updated prose:**
> Mirascope Cloud's code-first approach unifies version control, LLM evaluation, and collaboration

### Product Positioning

**Legacy prose (needs update):**
> Lilypad provides automatic versioning for your LLM functions

**Updated prose:**
> Mirascope Cloud provides automatic versioning for your LLM functions via the `@ops.version` decorator
