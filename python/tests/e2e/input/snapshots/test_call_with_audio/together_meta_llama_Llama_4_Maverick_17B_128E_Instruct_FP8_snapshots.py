from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Together chat completions do not currently support audio inputs via Mirascope.',)",
            "feature": "Audio inputs",
            "model_id": "None",
            "provider_id": "together",
        }
    }
)
