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

### Old response-models Path (HIGH)
```regex
/docs/learn/llm/response-models
```
This path was renamed in v2.

**Fix:** Update to the new path.
- OLD: `/docs/learn/llm/response-models`
- NEW: `/docs/learn/llm/structured-output`

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

The way to access and serialize responses changed in v2.

### Old Response Content Access
```regex
\.content(?![_a-zA-Z])
```

**Example code that would be flagged:**
```python
response = recommend_book("fantasy")
print(response.content)  # v1 pattern - flagged
```

**Correct v2 pattern:**
```python
response = recommend_book("fantasy")
print(response.text())  # v2 pattern - method call
```

**Note:** This pattern may have false positives (e.g., `.content` on other objects). Review in context.

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

## Structured Output (v1) - HIGH Priority

### Old response_model Parameter
```regex
response_model\s*=
```

**Example code that would be flagged:**
```python
@openai.call("gpt-4o-mini", response_model=Book)
def recommend_book(genre: str): ...
```

**Correct v2 pattern:**
```python
@llm.call("openai/gpt-4o-mini", format=Book)
def recommend_book(genre: str): ...

response = recommend_book("fantasy")
book = response.parse()  # Must call .parse() to get model
```

---

## Streaming (v1) - HIGH Priority

### Old stream=True Parameter
```regex
stream\s*=\s*True
```

**Example code that would be flagged:**
```python
@openai.call("gpt-4o-mini", stream=True)
def recommend_book(genre: str): ...
```

**Correct v2 pattern:**
```python
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str): ...

response = recommend_book.stream("fantasy")  # Method call
for chunk in response.text_stream():
    print(chunk, end="", flush=True)
```

### Old Chunk Content Access
```regex
chunk\.content
```

**Example code that would be flagged:**
```python
for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
```

**Correct v2 pattern:**
```python
for chunk in response.text_stream():
    print(chunk, end="", flush=True)  # chunk is already the text
```

---

## Call Parameters (v1) - HIGH Priority

### Old call_params Parameter
```regex
call_params\s*=
```

**Example code that would be flagged:**
```python
@openai.call("gpt-4o-mini", call_params={"temperature": 0.7})
def recommend_book(genre: str): ...
```

**Correct v2 pattern:**
```python
@llm.call("openai/gpt-4o-mini", temperature=0.7)  # Direct kwargs
def recommend_book(genre: str): ...
```

---

## Custom Client (v1) - HIGH Priority

### Old client= Parameter in Decorator
```regex
client\s*=\s*\w+\(
```

**Example code that would be flagged:**
```python
@openai.call("gpt-4o-mini", client=OpenAI(base_url="..."))
def recommend_book(genre: str): ...
```

**Correct v2 pattern:**
```python
llm.register_provider("openai", scope="custom/", base_url="...")

@llm.call("custom/gpt-4o-mini")
def recommend_book(genre: str): ...
```

---

## Tool Patterns (v1) - HIGH Priority

### Old BaseTool Class
```regex
class\s+\w+\s*\(\s*(llm\.)?BaseTool\s*\)
```

**Example code that would be flagged:**
```python
class GetWeather(llm.BaseTool):
    location: str
    def call(self): ...
```

**Correct v2 pattern:**
```python
@llm.tool
def get_weather(location: str) -> str:
    """Get the weather."""
    return f"Weather: {location}"
```

### Old response.tool Pattern
```regex
response\.tool[^_s]|if\s+tool\s*:=\s*response\.tool
```

**Example code that would be flagged:**
```python
if tool := response.tool:
    result = tool.call()
```

**Correct v2 pattern:**
```python
while response.tool_calls:
    tool_results = response.execute_tools()
    response = response.resume(tool_results)
```

### Old tool.call() Pattern
```regex
tool\.call\(\)
```

**Example code that would be flagged:**
```python
result = tool.call()
```

**Correct v2 pattern:**
```python
tool_results = response.execute_tools()
```

---

## prompt_template (v1) - HIGH Priority

### Old prompt_template Parameter
```regex
prompt_template\s*=
```

**Example code that would be flagged:**
```python
@openai.call("gpt-4o-mini", prompt_template="Recommend a {genre} book.")
def recommend_book(genre: str): ...
```

**Correct v2 pattern:**
```python
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."  # Return string from function
```

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
- **Legacy API syntax** - imports, decorators from mirascope.core
- **Response API** - `.content` property, `.model_dump()` method
- **Structured output** - `response_model=` parameter
- **Streaming** - `stream=True` parameter, `chunk.content` access
- **Call parameters** - `call_params=` parameter
- **Custom client** - `client=` parameter in decorator
- **Tool patterns** - `BaseTool` class, `response.tool`, `tool.call()`
- **prompt_template** - `prompt_template=` parameter
- **Documentation links** - `/docs/mirascope`, `/docs/v1/`, `/docs/learn/llm/response-models`
- **Image references** - blog images (may be outdated UI screenshots)
- **Prose references** - inline code referencing deprecated APIs

### MEDIUM - Fix soon
- Year references in titles (flags pre-2026)
- Dated model versions in code examples
- Specific guide links (`/docs/guides/<specific>`)
- Provider-specific prose explanations
- Prose context around flagged code blocks

### LOW - Fix when convenient
- (No items currently at LOW priority)

---

## Patterns NOT Currently Implemented

The following patterns are mentioned in documentation but not detected by the audit script:

- Frontmatter date validation
- Internal blog link verification
- External link checking

These require manual review or separate tooling.
