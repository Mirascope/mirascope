## Mirascope v2 Python

This directory contains the Python implementation of Mirascope.

## Development Setup

1. **Environment Variables**: Copy `.env.example` to `.env` and fill in your API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

2. **Install Dependencies**:

   ```bash
   uv sync --all-extras --dev
   ```

3. **Run Tests**:
   ```bash
   uv run pytest
   ```

## `ops.span` and Session Tracing

`mirascope.ops` provides tracing helpers to trace any Python function, not just
`llm.Model` calls.

1. Install the OTEL extra and set up a tracer provider exactly as shown above.
   `ops.span` automatically reuses the active provider, so spans from manual
   instrumentation and GenAI instrumentation end up in the same trace tree.
2. Use `ops.session` to group related spans and attach metadata:
   ```python
   from mirascope import ops

   with ops.session(id="req-42", attributes={"team": "core"}):
       with ops.span("load-data") as span:
           span.set(stage="ingest")
           # expensive work here
   ```
3. The span exposes `span_id`/`trace_id`, logging helpers, and graceful no-op
   behavior when OTEL is not configured. When OTEL is active, session metadata is
   attached to every span, and additional tools like `ops.trace`/`ops.version`
   (planned) can build on the same context.

## Testing

### VCR Cassettes

The project uses [VCR.py](https://vcrpy.readthedocs.io/) to record and replay HTTP interactions with LLM APIs. This allows tests to run quickly and consistently without making actual API calls.

- **Cassettes Location**: Test cassettes are stored in `tests/llm/clients/*/cassettes/`
- **Recording Mode**: Tests use `"once"` mode - records new interactions if no cassette exists, replays existing cassettes otherwise
- **CI/CD**: In CI environments, tests use existing cassettes and never make real API calls

### Inline Snapshots

The project uses [inline-snapshot](https://15r10nk.github.io/inline-snapshot/) to capture expected test outputs directly in the test code.

- **Update Snapshots**: Run `uv run pytest --inline-snapshot=fix` to update all snapshots with actual values
- **Review Changes**: Run `uv run pytest --inline-snapshot=review` to preview what would change
- **Formatted Output**: Snapshots are automatically formatted with `ruff` for consistency

Example:
```python
def test_api_response():
    response = client.call(messages=[user("Hello")])
    assert response.content == snapshot([Text(text="Hi there!")])
```

### Recording New Test Interactions

To record new test interactions:

1. Ensure your API keys are set in `.env`
2. Delete the relevant cassette file (if updating an existing test)
3. Run the specific test: `uv run pytest tests/path/to/test.py::test_name`
4. The cassette will be automatically created/updated
