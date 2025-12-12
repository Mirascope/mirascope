from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Model 'openai/gpt-4o:completions' does not support audio inputs.\",)",
            "feature": "Audio inputs",
            "model_id": "None",
            "provider_id": "openai",
        }
    }
)
