from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict' is not supported by provider 'anthropic' for model 'anthropic/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_id": "anthropic",
        }
    }
)
