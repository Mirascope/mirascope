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
