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

### Response Text Access

**Current (correct) - use `.text()` method:**
```python
response = recommend_book("fantasy")
print(response.text())
```

**Legacy v1 (needs update):**
```python
response = recommend_book("fantasy")
print(response.content)  # .content property is deprecated
```

### Structured Output (Response Models)

**Current (correct) - use `format=` and `.parse()`:**
```python
from pydantic import BaseModel

class Book(BaseModel):
    title: str
    author: str

@llm.call("openai/gpt-4o-mini", format=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."

response = recommend_book("fantasy")
book = response.parse()  # Returns Book instance
print(book.title)
```

**Legacy v1 (needs update):**
```python
@openai.call("gpt-4o-mini", response_model=Book)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."

book = recommend_book("fantasy")  # Returned model directly
print(book.title)
```

### Streaming

**Current (correct) - use `.stream()` method and `.text_stream()`:**
```python
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."

response = recommend_book.stream("fantasy")
for chunk in response.text_stream():
    print(chunk, end="", flush=True)
```

**Legacy v1 (needs update):**
```python
@openai.call("gpt-4o-mini", stream=True)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."

for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
```

### Call Parameters

**Current (correct) - pass as direct kwargs:**
```python
@llm.call("openai/gpt-4o-mini", temperature=0.7, max_tokens=1000)
def recommend_book(genre: str):
    return f"Recommend a {genre} book."
```

**Legacy v1 (needs update):**
```python
@openai.call("gpt-4o-mini", call_params={"temperature": 0.7, "max_tokens": 1000})
def recommend_book(genre: str):
    return f"Recommend a {genre} book."
```

### Runtime Model Override

**Current (correct) - use `llm.model()` context manager:**
```python
from mirascope import llm

@llm.call("openai/gpt-4o-mini", temperature=0.8)
def recommend_book(genre: str):
    return f"Recommend me a {genre} book."

# Override at runtime with a different model or parameters
with llm.model("anthropic/claude-sonnet-4-20250514", temperature=0.5):
    response = recommend_book("fantasy")  # Uses Claude with temperature=0.5
```

### Custom Providers / Base URL

**Current (correct) - use `llm.register_provider()`:**
```python
from mirascope import llm

# Register a custom provider scope
llm.register_provider("openai", scope="custom/", base_url="https://my-custom-endpoint.com/v1")

@llm.call("custom/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."
```

**Legacy v1 (needs update):**
```python
from openai import OpenAI

@openai.call("gpt-4o-mini", client=OpenAI(base_url="https://my-custom-endpoint.com/v1"))
def recommend_book(genre: str):
    return f"Recommend a {genre} book."
```

### Tools

**Current (correct) - use `@llm.tool` decorator and tool execution methods:**
```python
from mirascope import llm

@llm.tool
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

@llm.call("openai/gpt-4o-mini", tools=[get_weather])
def weather_assistant(query: str):
    return query

response = weather_assistant("What's the weather in NYC?")
while response.tool_calls:
    tool_results = response.execute_tools()
    response = response.resume(tool_results)

print(response.text())
```

**Legacy v1 (needs update):**
```python
def get_weather(location: str) -> str:
    """Get the weather for a location."""
    return f"Weather in {location}: Sunny, 72°F"

@openai.call("gpt-4o-mini", tools=[get_weather])
def weather_assistant(query: str):
    return query

response = weather_assistant("What's the weather in NYC?")
if tool := response.tool:
    result = tool.call()
    # ... manual tool handling
```

**Also Legacy v1 (BaseTool class):**
```python
class GetWeather(llm.BaseTool):
    location: str

    def call(self) -> str:
        return f"Weather in {self.location}: Sunny"
```

### prompt_template Parameter

**Current (correct) - return string directly from function body:**
```python
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."
```

**Legacy v1 (needs update):**
```python
@openai.call("gpt-4o-mini", prompt_template="Recommend a {genre} book.")
def recommend_book(genre: str): ...
```

### Built-in Providers

v2 supports these built-in providers (use with `@llm.call("provider/model")`):
- `anthropic/` - Anthropic (Claude models)
- `google/` - Google (Gemini models)
- `mirascope/` - Mirascope Cloud
- `mlx/` - MLX (local Apple Silicon)
- `ollama/` - Ollama (local models)
- `openai/` - OpenAI (GPT models)
- `together/` - Together AI

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
- `/docs/learn/llm/structured-output` - Structured output docs (formerly response-models)
- `/docs/learn/ops` - Observability/tracing docs (formerly Lilypad)
- `/docs/api/...` - API reference
- `/docs/guides` - Guides index (under construction)
- `/blog/...` - Internal blog links

### Invalid Paths (Will Be Flagged)
- `/docs/mirascope/...` - Does not exist in v2, use `/docs/...`
- `/docs/guides/<specific-guide>` - Guides not ready, use `/docs/guides` only
- `/docs/v1/...` - Legacy docs, NEVER link
- `/docs/lilypad` - Deprecated, now `/docs/learn/ops`
- `/docs/learn/llm/response-models` - Renamed to `/docs/learn/llm/structured-output`

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
