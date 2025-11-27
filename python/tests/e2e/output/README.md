# Output Tests (Response Decoding)

Tests in this directory verify that response decoding works correctly across all call types.

## Test Naming Convention

All test functions must follow this pattern:
```
test_{scenario}_{call_type}
```

Where `call_type` is one of:
- `sync` - Synchronous calls
- `async` - Asynchronous calls
- `stream` - Synchronous streaming
- `async_stream` - Asynchronous streaming

You may also append `_context` to each call type if you want to test parity when using
context calls. In this case, the `_context` test should exactly match its non-context variant
in the LLM content being generated, as cassettes and snapshots will be shared with the non-context variant.

### Examples
```python
def test_call_with_tools_sync(provider, model_id, snapshot): ...
def test_call_with_tools_async(provider, model_id, snapshot): ...
def test_call_with_tools_stream(provider, model_id, snapshot): ...
def test_call_with_tools_async_stream(provider, model_id, snapshot): ...
```

## Test Structure

Each test scenario should have **4 test functions** (or 8 with context).

Context variants share the same VCR cassettes as non-context variants.

## Parametrization

Tests should be parametrized with:
```python
@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
```

This ensures all providers and models are tested for each scenario.

## Fixtures

- **`provider`** - The LLM provider (e.g., "anthropic", "openai")
- **`model_id`** - The model ID (e.g., "anthropic/claude-sonnet-4-0", "openai/gpt-4o")
- **`snapshot`** - Auto-generated snapshot for the current test configuration
- **`vcr_cassette_name`** - Auto-generated cassette path

## Cassette Organization

```
cassettes/
└── {scenario}/
    └── {provider}_{model_id}/
        ├── sync.yaml
        ├── async.yaml
        ├── stream.yaml
        └── async_stream.yaml
```

Example: `cassettes/call_with_tools/anthropic_claude-sonnet-4-0/sync.yaml`

## Snapshot Organization

```
snapshots/
└── {scenario}/
    └── {provider}_{model_id}_snapshots.py
```

Each snapshot file contains 4 snapshot variables:
- `sync_snapshot`
- `async_snapshot`
- `stream_snapshot`
- `async_stream_snapshot`

Example: `snapshots/call_with_tools/anthropic_claude-sonnet-4-0_snapshots.py`

## What to Test

Output tests should verify anything where the code under test varies based on call type. This is particularly true with streaming vs non streaming cases. For example, thinking output, finish reasons, chunk reconstruction, and tool calling tests should all be in the output/ directory.

Essentially, anything where the **decoding logic differs** between sync/async/stream/async_stream.
