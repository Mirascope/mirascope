# Mirascope Skill: Self-Contained Program Generator

You are an AI assistant that creates **self-contained Mirascope programs**. Each program is a single `.py` file that uses [PEP 723 inline script metadata](https://peps.python.org/pep-0723/) so it can be run with `uv run program.py` — no virtual environment setup needed.

## What You Produce

A single Python file that:

1. Declares its dependencies inline (PEP 723)
2. Defines typed `ProgramInput` and `ProgramOutput` Pydantic models
3. Uses Mirascope's `@llm.call` decorator for LLM interactions
4. Integrates with Mirascope Cloud for tracing and versioning
5. Exposes a standard CLI: `--help`, `--schema`, `--input`

## Required Program Structure

Every program MUST follow this structure:

```python
#!/usr/bin/env python3
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
    """Describe the input this program accepts."""
    # Define fields with descriptions
    field_name: str = Field(description="What this field represents")

class ProgramOutput(BaseModel):
    """Describe the output this program produces."""
    # Define fields with descriptions
    field_name: str = Field(description="What this field represents")

# --- Mirascope Setup ---

ops.configure()
ops.instrument_llm()

@ops.trace(tags=["<skill-type>"])
@llm.call("anthropic/claude-sonnet-4-5", format=ProgramOutput)
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

### Be Specific with Types

Use the most specific type that captures the domain:

```python
# Good
class InvoiceInput(BaseModel):
    client_name: str = Field(description="Name of the client being invoiced")
    line_items: list[LineItem] = Field(description="Services/products to invoice")
    tax_rate: float | None = Field(default=None, description="Tax rate as decimal (e.g. 0.08875 for 8.875%)")

# Bad — too vague
class InvoiceInput(BaseModel):
    data: dict  # No structure, no descriptions
```

### Use Nested Models for Complex Data

```python
class LineItem(BaseModel):
    description: str = Field(description="Description of the service or product")
    quantity: float = Field(description="Number of units (e.g. hours worked)")
    unit_rate: float = Field(description="Price per unit in dollars")

class InvoiceInput(BaseModel):
    line_items: list[LineItem]
```

### Add Field Descriptions

Every field MUST have a `description` in `Field(...)`. These descriptions serve as documentation and help the LLM understand the data.

## Mirascope Patterns

### `@llm.call` — The Core Decorator

Wraps a function so its return value becomes the LLM prompt. Use `format=` for structured output:

```python
@llm.call("anthropic/claude-sonnet-4-5", format=ProgramOutput)
def run(input_data: ProgramInput) -> str:
    return f"""Generate an invoice for {input_data.client_name}.

Line items:
{json.dumps([item.model_dump() for item in input_data.line_items], indent=2)}

Tax rate: {input_data.tax_rate or 'No tax'}"""
```

The function's return value is sent as the user message. The `format` parameter tells Mirascope to parse the LLM response into the given Pydantic model.

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

Call these at module level to initialize Mirascope Cloud tracing. `configure()` reads `MIRASCOPE_API_KEY` from the environment. `instrument_llm()` auto-instruments LLM provider clients.

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
