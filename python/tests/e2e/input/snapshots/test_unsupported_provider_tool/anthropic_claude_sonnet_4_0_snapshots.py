from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'Provider tool Unsupported Test Tool' is not supported by provider 'anthropic'\",)",
            "feature": "Provider tool Unsupported Test Tool",
            "model_id": "None",
            "provider_id": "anthropic",
        }
    }
)
