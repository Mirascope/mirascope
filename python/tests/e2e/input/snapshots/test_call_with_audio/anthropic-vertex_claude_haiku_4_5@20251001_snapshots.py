from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Anthropic Vertex AI does not support audio inputs.',)",
            "feature": "audio input",
            "model_id": "None",
            "provider": "anthropic-vertex",
        }
    }
)
