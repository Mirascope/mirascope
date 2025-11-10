# End-to-End Tests

This directory contains end-to-end tests for Mirascope's LLM provider integrations.

## Directory Structure

- **`output/`** - Tests that verify response decoding/reconstruction across different call types (sync/async/stream/async_stream). These tests need to ensure feature parity in how responses are decoded. Thus, each test will have 4 cassettes per model being tested, and each snapshot file contains 4 separate snapshots.

- **`input/`** - Tests that verify request encoding. Since encoding is conserved across call types, these tests don't need to be duplicated for sync/async/stream/async_stream variants. Thus, there is one cassette and snapshot per model being tested.

## VCR Cassettes

Tests use [VCR.py](https://vcrpy.readthedocs.io/) to record and replay HTTP interactions with LLM providers. This makes tests deterministic, and quite fast.

Cassettes are stored in `cassettes/` subdirectories and are organized by test scenario, provider, and model.

Note that when you update the implementation or tests in a way that changes what get sents to the provider, you will get a failed to ovewrrite snapshot failure for the test in question. In this case, you must manually delete the outdated cassettes and regenerate them. (Sadly, there is no vcr feature for overwriting only failing cassettes).

You can regenerate snapshots en masse by deleting the `cassettes/` subdirectory, but this
should be done sparingly because it takes time and API token usage.

### xAI/Grok Special Case

**xAI uses gRPC instead of HTTP**, so VCR.py cannot intercept its traffic. Therefore, xAI tests are handled differently:

- **In CI**: xAI tests are **automatically skipped** (no API key required)
- **Locally**: xAI tests run with **real API calls** when the `--use-real-grok` flag is provided

#### Running xAI tests locally

```bash
# Set your API key
export XAI_API_KEY=your-api-key

# Run all E2E tests including xAI
cd python
uv run pytest tests/e2e/ --use-real-grok --inline-snapshot=fix

# Run only xAI tests
uv run pytest tests/e2e/ -k xai --use-real-grok
```

#### When to run xAI tests

Run xAI tests manually when:

1. **Making changes to xAI client**: `mirascope/llm/clients/xai/grok.py`
2. **Changing core abstractions**: Changes to base classes or protocols that affect all providers
3. **Before releases**: Verify xAI compatibility before publishing a new version

#### Why this approach?

Since gRPC traffic cannot be recorded with VCR.py, we have two options:
1. Build a custom cassette system (complex, fragile, hard to maintain)
2. Run tests with real API calls when needed (simple, accurate, pragmatic)

We chose option 2 for simplicity and maintainability.

## Snapshots

Tests use [inline-snapshot](https://15r10nk.github.io/inline-snapshot/) to validate test outputs. Snapshots are stored in `snapshots/` subdirectories.

To update snapshots:
```bash
uv run pytest python/tests/e2e/ --fix
```

Note snapshot files will be created if missing. It is sometimes convenient to simply remove the snapshot directory (either entirely, or the snapshot subdirectory for a given test scenario) and regenerate it using `--fix`. When the snapshot file is created, we automatically import common symbols like `llm.Text` directly into the snapshot namespace, so
the snapshots will work without any hand-editing. Unused imports are automatically removed by `ruff`; which can sometimes create issues if you update a test so that the snapshot file now needs a missing symbol. In this case, deleting and regenerating the snapshot file is a convenient fix.


## Adding New Tests

- If testing **response decoding** (e.g., tool calls, thinking, structured output) → add to `output/`
- If testing **request encoding** (e.g., parameters, input validation) → add to `input/`

See the README files in each subdirectory for specific conventions.

