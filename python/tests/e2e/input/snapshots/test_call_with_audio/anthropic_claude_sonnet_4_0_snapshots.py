from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Anthropic does not support audio inputs.',)",
            "feature": "audio input",
            "model_id": "None",
            "provider_id": "anthropic",
        }
    }
)
