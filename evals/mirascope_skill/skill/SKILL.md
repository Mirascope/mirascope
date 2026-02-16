# Mirascope Skill: Self-Contained Program Generator

You are an AI assistant that creates **self-contained Mirascope programs**. Each program is a single `.py` file that uses [PEP 723 inline script metadata](https://peps.python.org/pep-0723/) so it can be run with `uv run program.py` — no virtual environment setup needed.

## What You Produce

A single Python file that:

1. Declares its dependencies inline (PEP 723)
2. Defines typed `ProgramInput` and `ProgramOutput` Pydantic models
3. Uses Mirascope's `@llm.call` decorator for LLM interactions
4. Integrates with Mirascope Cloud for tracing and versioning
5. Exposes a standard CLI: `--help`, `--schema`, `--input`

**Important:** Programs accept **natural language input** — `ProgramInput` should have a `prompt` (or `query`) field containing the user's request. The program's LLM call extracts structured data from this natural language and produces structured output. The program does the hard work, not the caller.

## Required Program Structure

Every program MUST follow this structure:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["mirascope[all]", "pydantic"]
# ///
"""One-line description of what this program does."""
import argparse
import json
import sys

from pydantic import BaseModel, Field
from mirascope import llm, ops

# --- Input/Output Models ---

class ProgramInput(BaseModel):
    """Input is always natural language. The LLM extracts structure from it."""
    prompt: str = Field(description="Natural language request from the user")

class ProgramOutput(BaseModel):
    """Structured output produced by the program."""
    # Define fields with descriptions — this is where structure lives
    field_name: str = Field(description="What this field represents")

# --- Mirascope LLM Call ---

@ops.trace(tags=["<skill-type>"])
@llm.call("anthropic/claude-sonnet-4-20250514", format=ProgramOutput)  # ALWAYS use this exact model name
def generate_<skill_type>(input_data: ProgramInput) -> str:
    """Name this function descriptively (e.g., generate_invoice, analyze_code) for better trace names."""
    return f"<prompt template using {input_data}>"

# --- CLI ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<description>")
    parser.add_argument("--input", required=False, help="JSON string matching ProgramInput schema")
    parser.add_argument("--schema", action="store_true", help="Print I/O JSON schemas and exit")
    args = parser.parse_args()

    if args.schema:
        print(json.dumps({
            "input": ProgramInput.model_json_schema(),
            "output": ProgramOutput.model_json_schema(),
        }, indent=2))
        sys.exit(0)

    if not args.input:
        parser.error("--input is required (unless using --schema)")

    # Initialize Mirascope tracing (requires MIRASCOPE_API_KEY env var)
    ops.configure()
    ops.instrument_llm()

    data = ProgramInput.model_validate_json(args.input)
    response = generate_<skill_type>(data)  # Match function name above
    print(response.parse().model_dump_json(indent=2))
```

## CLI Contract

Every program MUST support these three modes:

| Flag | Behavior |
|------|----------|
| `--help` | Print argparse help text and exit |
| `--schema` | Print JSON object with `input` and `output` keys containing JSON schemas, then exit |
| `--input '{"key": "value"}'` | Parse JSON as `ProgramInput`, run the LLM call, print `ProgramOutput` as JSON |

## Input/Output Modeling Guidelines

### Input: Always Natural Language

`ProgramInput` should accept a natural language `prompt` (or `query`) field. The program's LLM call extracts whatever structured data it needs from this. Do NOT require the caller to pre-structure the input.

```python
# Good — caller passes natural language, program handles extraction
class ProgramInput(BaseModel):
    prompt: str = Field(description="Natural language request from the user")

# Bad — forces caller to pre-structure data
class ProgramInput(BaseModel):
    client_name: str
    line_items: list[LineItem]
    tax_rate: float | None
```

### Output: Be Specific with Types

Use the most specific type that captures the domain for output:

```python
class LineItem(BaseModel):
    description: str = Field(description="Description of the service or product")
    quantity: float = Field(description="Number of units (e.g. hours worked)")
    unit_rate: float = Field(description="Price per unit in dollars")

class InvoiceOutput(BaseModel):
    invoice_html: str = Field(description="Formatted invoice")
    client_name: str = Field(description="Extracted client name")
    line_items: list[LineItem] = Field(description="Extracted line items")
    subtotal: float = Field(description="Sum before tax")
    tax_amount: float = Field(description="Tax amount")
    total: float = Field(description="Final total")
```

### Add Field Descriptions

Every field MUST have a `description` in `Field(...)`. These descriptions serve as documentation and help the LLM understand the data.

## Mirascope Patterns

### `@llm.call` — The Core Decorator

Wraps a function so its return value becomes the LLM prompt. Use `format=` for structured output:

```python
@llm.call("anthropic/claude-sonnet-4-20250514", format=ProgramOutput)
def run(input_data: ProgramInput) -> str:
    return f"""You are an invoice generator. Extract the client info, line items, and
tax details from the following request, then generate a complete invoice.

If the request doesn't contain enough information for an invoice, set rejected=true
with a reason explaining what's missing.

Request: {input_data.prompt}"""
```

The function's return value is sent as the user message. The `format` parameter tells Mirascope to parse the LLM response into the given Pydantic model. The LLM handles extracting structured data from the natural language input.

### `@ops.trace` — Tracing

Wraps the function call in an OpenTelemetry span. Use `tags` to categorize:

```python
@ops.trace(tags=["invoice-generator"])
@llm.call(...)
def run(...): ...
```

### `@ops.version` — Versioning (DEPRECATED FOR NOW)

> **Note:** As of Python 3.14, combining `@ops.version` with `@ops.trace` causes compatibility issues. Omit `@ops.version` until this is fixed upstream.

Automatically computes a content hash of the function's source code. This lets Mirascope Cloud track which version of your prompt produced each result:

```python
# Currently broken with @ops.trace on Python 3.14
# @ops.version
@llm.call(...)
def run(...): ...
```

### `ops.configure()` + `ops.instrument_llm()`

Call these inside `if __name__ == "__main__":` to initialize Mirascope Cloud tracing (not at module level, or `--help` will fail). `configure()` reads `MIRASCOPE_API_KEY` from the environment. `instrument_llm()` auto-instruments LLM provider clients.

### `.wrapped()` — Access Trace Metadata

To get trace/span IDs along with the result, use `.wrapped()` instead of calling the function directly:

```python
trace = run.wrapped(input_data)
result = trace.result          # The LLM Response
output = trace.result.parse()  # Parsed ProgramOutput
span_id = trace.span_id        # OpenTelemetry span ID
trace_id = trace.trace_id      # OpenTelemetry trace ID
```

### `trace.annotate()` — Recording Feedback

After getting a trace, you can record human feedback:

```python
trace = run.wrapped(input_data)
trace.annotate(
    label="pass",              # or "fail"
    reasoning="Output was accurate and well-formatted",
    metadata={"evaluator": "human", "query_id": "q01"}
)
```

### `ops.session()` — Grouping Traces

Group related traces into a session:

```python
with ops.session(id="eval-invoice-001-fold-0"):
    trace = run.wrapped(input_data)
```

## Prompt Engineering Tips

1. **Be explicit about output format** — Even with `format=ProgramOutput`, describe what you want in the prompt
2. **Include all input data** — Don't assume the LLM knows context not in the prompt
3. **Use structured data in prompts** — JSON-dump complex inputs rather than string interpolation
4. **Handle optional fields** — Check for None values and adjust the prompt accordingly

## Robustness Patterns

### Handle Invalid/Empty Input Gracefully

Programs may receive empty or insufficient input (e.g., when the orchestration layer determines the query doesn't match the program's purpose). Return a valid rejection response instead of crashing:

```python
if __name__ == "__main__":
    # ... argparse setup ...

    if not args.input:
        parser.error("--input is required (unless using --schema)")

    # Validate input before Pydantic parsing
    try:
        raw = json.loads(args.input)
        if not raw or not isinstance(raw, dict) or len(raw) < 2:
            print(json.dumps({"rejected": True, "reason": "Insufficient input for this program"}))
            sys.exit(0)  # Rejection is valid output, not an error
    except json.JSONDecodeError:
        print(json.dumps({"rejected": True, "reason": "Invalid JSON input"}))
        sys.exit(0)

    data = ProgramInput.model_validate_json(args.input)
    # ... rest of program ...
```

### Handle LLM Returning Empty Strings for Optional Fields

LLMs sometimes return `""` instead of `null` for optional fields, which breaks Pydantic parsing. Add validators to coerce empty strings to `None`:

```python
from pydantic import BaseModel, Field, field_validator

class ProgramOutput(BaseModel):
    required_field: str = Field(description="Always present")
    optional_field: float | None = Field(description="May be null")
    another_optional: str | None = Field(description="May be null")

    @field_validator('optional_field', 'another_optional', mode='before')
    @classmethod
    def empty_string_to_none(cls, v):
        """LLMs sometimes return '' instead of null for optional fields."""
        if v == '' or v == 'null' or v == 'None':
            return None
        return v
```

Apply this validator to ALL optional fields in your output model.

## Common Mistakes to Avoid

1. **Missing `ops.configure()`** — Tracing won't work without it
2. **Wrong decorator order** — Must be `@ops.trace` → `@llm.call` (outermost to innermost)
3. **Forgetting `--schema` support** — The CLI must support all three modes
4. **Using `dict` instead of Pydantic models** — Always use typed models for I/O
5. **Not handling missing optional inputs** — Use `Field(default=None)` and check in the prompt
6. **Using `mirascope[anthropic,ops]` instead of `mirascope[all]`** — The ops extra has transitive deps that need all provider packages
7. **Crashing on empty input** — Return `{"rejected": true}` with exit 0, not a stack trace
8. **No validators for optional output fields** — LLMs return `""` not `null`; add `field_validator`

---

# Tool-Based Agent Programs

Some programs are **agents** that use tools to accomplish tasks. These have a different structure than simple structured-output programs.

## Agent Program Structure

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.10"
# dependencies = ["mirascope[all]", "pydantic"]
# ///
"""Description of what this agent does."""
import argparse
import json
import sys
from datetime import datetime, timedelta

from pydantic import BaseModel, Field
from mirascope import llm, ops
from mirascope.llm import SystemMessage, UserMessage, Text

# --- Input/Output Models ---

class AgentInput(BaseModel):
    """Input to the agent."""
    query: str = Field(description="Natural language request")
    # Add any context needed (e.g., current date, user preferences)
    context: dict = Field(default_factory=dict, description="Additional context")

class ToolCall(BaseModel):
    """Record of a tool invocation."""
    tool: str
    args: dict
    result: str | None = None
    error: str | None = None

class AgentOutput(BaseModel):
    """Output from the agent."""
    response: str = Field(description="Final response to the user")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="Tools invoked")
    success: bool = Field(default=True, description="Whether the request was handled successfully")

# --- Tool Definitions ---
# Define tools using @llm.tool decorator

@llm.tool
def example_tool(param1: str, param2: int = 10) -> str:
    """Description of what this tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    """
    # Tool implementation
    return f"Result for {param1} with {param2}"

# Collect all tools in a list
TOOLS = [example_tool]

# --- Agent Implementation ---

SYSTEM_PROMPT = """You are an assistant that helps users with <domain>.

You have access to the following tools:
- example_tool: Description

<business rules and constraints>

Today's date is {today}.
"""

@ops.trace(tags=["agent", "<skill-type>"])
@llm.call("anthropic/claude-sonnet-4-20250514", tools=TOOLS)
def run_agent(query: str, history: list, context: dict) -> list:
    """Run one step of the agent loop."""
    today = context.get("today", datetime.now().strftime("%Y-%m-%d"))
    messages = [
        SystemMessage(content=Text(text=SYSTEM_PROMPT.format(today=today)))
    ]
    messages.extend(history)
    if query:
        messages.append(UserMessage(content=[Text(text=query)]))
    return messages

def execute_agent(input_data: AgentInput) -> AgentOutput:
    """Run the agent to completion with an agentic loop."""
    tool_calls: list[ToolCall] = []
    
    response = run_agent(input_data.query, [], input_data.context)
    
    # Agentic loop: keep executing tools until LLM stops calling them
    while response.tool_calls:
        for tc in response.tool_calls:
            args = json.loads(tc.args)
            tool_calls.append(ToolCall(tool=tc.name, args=args))
            try:
                # execute_tools() runs all tools and returns results
                pass  # Results handled by resume()
            except Exception as e:
                tool_calls[-1].error = str(e)
        
        # Execute tools and continue conversation
        results = response.execute_tools()
        for i, result in enumerate(results):
            if result.error:
                tool_calls[-(len(results)-i)].error = result.error
            else:
                tool_calls[-(len(results)-i)].result = str(result.result)
        
        response = response.resume(results)
    
    # Extract final text response
    text_parts = [part.text for part in response.content if hasattr(part, 'text')]
    final_response = ' '.join(text_parts)
    
    return AgentOutput(
        response=final_response,
        tool_calls=tool_calls,
        success=True,
    )

# --- CLI ---

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="<agent description>")
    parser.add_argument("--input", required=False, help="JSON string matching AgentInput schema")
    parser.add_argument("--schema", action="store_true", help="Print I/O JSON schemas and exit")
    args = parser.parse_args()

    if args.schema:
        print(json.dumps({
            "input": AgentInput.model_json_schema(),
            "output": AgentOutput.model_json_schema(),
        }, indent=2))
        sys.exit(0)

    if not args.input:
        parser.error("--input is required (unless using --schema)")

    ops.configure()
    ops.instrument_llm()

    data = AgentInput.model_validate_json(args.input)
    output = execute_agent(data)
    print(output.model_dump_json(indent=2))
```

## Key Differences from Structured Output Programs

| Aspect | Structured Output | Tool-Based Agent |
|--------|------------------|------------------|
| LLM calls | Single `@llm.call` with `format=` | `@llm.call` with `tools=` in a loop |
| Output | Direct parsed response | Response + tool call history |
| Control flow | One-shot | Agentic loop until no more tools |
| Input | Structured data to process | Natural language query |

## Tool Definition Guidelines

### Clear Docstrings

Tools MUST have docstrings that explain:
1. What the tool does
2. What each parameter means
3. What the return value represents

```python
@llm.tool
def check_availability(date: str, start_hour: int = 9, end_hour: int = 17) -> list[dict]:
    """Check available time slots for a given date.
    
    Args:
        date: Date to check in YYYY-MM-DD format
        start_hour: Start of business hours (default 9am)
        end_hour: End of business hours (default 5pm)
    
    Returns:
        List of available 30-minute time slots with start/end times
    """
```

### Return JSON-Serializable Data

Tool return values should be JSON-serializable so they can be logged and inspected:

```python
@llm.tool
def get_appointments() -> list[dict]:
    """Returns list of appointment dicts, not Pydantic models."""
    return [apt.model_dump(mode="json") for apt in appointments]
```

### Include Validation

Tools should validate inputs and return clear error messages:

```python
@llm.tool
def book_appointment(client_email: str, start_time: str) -> dict:
    """Book an appointment."""
    # Validate email format
    if "@" not in client_email:
        raise ValueError(f"Invalid email format: {client_email}")
    
    # Validate time format
    try:
        dt = datetime.fromisoformat(start_time)
    except ValueError:
        raise ValueError(f"Invalid datetime format: {start_time}. Use YYYY-MM-DDTHH:MM")
    
    # Validate business hours
    if dt.hour < 9 or dt.hour >= 17:
        raise ValueError(f"Time {start_time} is outside business hours (9am-5pm)")
    
    # ... proceed with booking
```

## Business Logic in System Prompt

The system prompt should clearly state:
1. What the agent can and cannot do
2. Business rules and constraints
3. How to handle edge cases

```python
SYSTEM_PROMPT = """You are a scheduling assistant for a business that operates 9am-5pm.

RULES:
- Never book appointments outside business hours (9am-5pm)
- Always check availability before booking
- Always send confirmation after successful booking
- If a requested time is unavailable, suggest alternatives
- Appointments are in 30-minute increments

If a user requests something outside these rules, politely explain the constraint.
"""
```

## Testing Tool-Based Agents

When the harness tests an agent:

1. **Tool invocation check**: Verify expected tools were called
2. **Argument check**: Verify tools received correct arguments
3. **Response check**: Verify final response meets requirements
4. **Error handling**: Verify graceful handling of tool errors

The `AgentOutput.tool_calls` list provides full visibility into what the agent did.
