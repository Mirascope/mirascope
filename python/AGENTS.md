## General Info

**ALWAYS use `uv` instead of `python` or `pip` commands:**

If working on `mirascope/llm`, consider reading the intro docs here: `docs/content/index.mdx` to get context.

## Common Issues:

- In test code, always use one `from mirascope import llm` import at the top level, and then use that to reference api concepts (like `llm.call`). If something is missing, then we should add it to the llm exports rather than directly importing it.
- Always handle imports at the top of the file (not inside a function or a test), unless we specifically need lazy importing to avoid circular deps. If so, add a comment to that effect.

### Common Commands

#### Testing

```bash
cd python && uv run pytest tests/
```

We use a mixture of unit and e2e testing. The e2e tests use vcr.py to simulate real LLM provider interaction. See `python/tests/e2e/README.md`.

#### Type Checking

```bash
cd python && uv run pyright .
```

#### Linting

```bash
cd python && uv run ruff check .
```

#### Formatting

```bash
cd python && uv run ruff format .
```

#### Coverage

```bash
cd python && uv run pytest --cov --cov-config=.coveragerc --cov-report=term-missing
```
