from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Anthropic does not support empty message content.',)",
            "feature": "empty message content",
            "model_id": "None",
            "provider_id": "anthropic",
        }
    }
)
