# Input Tests (Request Encoding)

Tests in this directory verify that request encoding works correctly. Since encoding is conserved across call types, these tests **do not need** to be duplicated for sync/async/stream/async_stream variants.

## Test Naming Convention

Test functions can use any descriptive name - they are **not required** to follow the `test_{scenario}_{call_type}` pattern used in output tests.

### Examples
```python
def test_all_params_includes_every_param(): ...
def test_call_with_params_sync(provider, model_id, snapshot): ...
def test_temperature_validation(provider, model_id): ...
```

## Parametrization

Tests should be parametrized with:
```python
@pytest.mark.parametrize("model_id", E2E_MODEL_IDS)
```

This ensures all providers and models are tested.

## Cassette Organization

```
cassettes/
└── {scenario}/
    └── {provider}_{model_id}.yaml
```

Single cassette per provider/model combination (no call type variants).

Example: `cassettes/call_with_params/anthropic_claude-sonnet-4-0.yaml`

## Snapshot Organization

```
snapshots/
└── {scenario}/
    └── {provider}_{model_id}_snapshots.py
```

Each snapshot file contains a single snapshot variable (or whatever makes sense for the test).

Example: `snapshots/call_with_params/anthropic_claude-sonnet-4-0_snapshots.py`

## What to Test

Input tests should verify:
- llm Message construction and encoding
- Parameter validation and encoding
- Warning messages for unsupported parameters
- Request body structure
- Header configuration
- Input message formatting
- Error handling for invalid inputs

Essentially, anything where you're primarmily testing **what gets sent to the API**, not what comes back.
