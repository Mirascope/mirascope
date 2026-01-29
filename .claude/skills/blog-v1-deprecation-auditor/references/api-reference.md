# Quick API Reference

Quick lookup for the Mirascope v2 API. Derived from the Python library at `python/mirascope/`.

## Imports

```python
from mirascope import llm, ops
```

---

## llm Module (`python/mirascope/llm/__init__.py`)

### Core Decorators

```python
@llm.call("provider/model")      # Make an LLM call
@llm.prompt()                    # Create a prompt template (no LLM call)
@llm.tool                        # Define a tool for function calling
```

### Model Format

The model string uses `"provider/model"` format:
- `"openai/gpt-4o-mini"`
- `"anthropic/claude-sonnet-4-20250514"`
- `"google/gemini-2.0-flash"`

### Messages

```python
llm.messages.system("You are a helpful assistant.")
llm.messages.user("Hello!")
```

Return a list of messages from a call function:
```python
@llm.call("openai/gpt-4o-mini")
def my_call():
    return [
        llm.messages.system("System prompt here"),
        llm.messages.user("User message here"),
    ]
```

### Content Types

```python
llm.Image(url="...")              # Image from URL
llm.Image(base64="...")           # Image from base64
llm.Audio(...)                    # Audio content
llm.Document(...)                 # Document content
```

### Response Types

```python
llm.Response                      # Sync response
llm.AsyncResponse                 # Async response
llm.StreamResponse                # Streaming response
llm.AsyncStreamResponse           # Async streaming response
```

### Tools

```python
@llm.tool
def my_tool(param: str) -> str:
    """Tool description."""
    return result

# Use tools with a call
@llm.call("openai/gpt-4o-mini", tools=[my_tool])
def call_with_tools(): ...
```

### Formatting / Structured Output

```python
from pydantic import BaseModel

class MyOutput(BaseModel):
    field: str

@llm.call("openai/gpt-4o-mini", response_model=MyOutput)
def structured_call(): ...
```

### Response Serialization

```python
# Get raw provider response and serialize
response = my_call()
print(response.raw.model_dump_json(indent=2))  # Pydantic providers only
```

**Provider compatibility:**
| Provider | Raw Type | Serialization |
|----------|----------|---------------|
| OpenAI | Pydantic | `model_dump_json()` |
| Anthropic | Pydantic | `model_dump_json()` |
| Ollama | Pydantic | `model_dump_json()` |
| Together | Pydantic | `model_dump_json()` |
| Google | Protobuf | `to_dict()` or custom |
| MLX | Custom | `json.dumps()` or custom |

### Key Exports

- `llm.call` - LLM call decorator
- `llm.prompt` - Prompt template decorator
- `llm.tool` - Tool decorator
- `llm.messages` - Message builders (system, user)
- `llm.Model` - Model configuration
- `llm.Response` - Response types
- `llm.Stream` - Streaming types

---

## ops Module (`python/mirascope/ops/__init__.py`)

### Configuration

```python
ops.configure()                   # Connect to Mirascope Cloud
ops.instrument_llm()              # Auto-trace all LLM calls
ops.uninstrument_llm()            # Stop auto-tracing
```

### Tracing Decorators

```python
@ops.trace                        # Trace a function
@ops.version                      # Version + trace a function (for prompt management)
```

### Manual Spans

```python
with ops.span("operation_name"):
    # Code to trace
    pass
```

### Sessions

```python
with ops.session() as s:
    # All traces in this block share a session ID
    pass

# Get current session
session_id = ops.current_session()
```

### Context Propagation

```python
# For distributed tracing
context = ops.extract_context(headers)
ops.inject_context(headers)

with ops.propagated_context():
    # Context is propagated
    pass
```

### Key Exports

- `ops.configure` - Connect to Mirascope Cloud
- `ops.instrument_llm` - Auto-instrument all LLM calls
- `ops.trace` - Trace decorator
- `ops.version` - Version + trace decorator
- `ops.span` - Manual span context manager
- `ops.session` - Session context manager

---

## Common Migration Patterns

### Basic LLM Call

```python
# OLD (v1)
from mirascope.core import openai

@openai.call("gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book"

# NEW (v2)
from mirascope import llm

@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book"
```

### With Messages

```python
# OLD (v1)
from mirascope.core import openai, Messages

@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return [
        Messages.System("You recommend books"),
        Messages.User(f"Recommend a {genre} book"),
    ]

# NEW (v2)
from mirascope import llm

@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str):
    return [
        llm.messages.system("You recommend books"),
        llm.messages.user(f"Recommend a {genre} book"),
    ]
```

### Tracing with Lilypad -> ops

```python
# OLD (Lilypad)
import lilypad
lilypad.configure(auto_llm=True)

@lilypad.trace(versioning="automatic")
@openai.call("gpt-4o-mini")
def my_call(): ...

# NEW (ops)
from mirascope import llm, ops
ops.configure()
ops.instrument_llm()

@ops.version
@llm.call("openai/gpt-4o-mini")
def my_call(): ...
```

### Response Dumping

```python
# OLD (v1)
response = recommend_book("fantasy")
print(response.model_dump())

# NEW (v2)
response = recommend_book("fantasy")
print(response.raw.model_dump_json(indent=2))
```

---

## Model Names Reference

### OpenAI
- `gpt-4o` - Flagship
- `gpt-4o-mini` - Efficient
- `o1`, `o1-mini` - Reasoning

### Anthropic
- `claude-sonnet-4-20250514` - Latest Sonnet
- `claude-opus-4-20250514` - Latest Opus
- `claude-3-5-haiku-20241022` - Haiku

### Google
- `gemini-2.0-flash` - Fast
- `gemini-1.5-pro` - Pro
