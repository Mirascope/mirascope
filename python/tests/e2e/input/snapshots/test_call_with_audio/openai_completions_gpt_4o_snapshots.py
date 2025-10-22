from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Model 'gpt-4o' does not support audio inputs.\",)",
            "feature": "Audio inputs",
            "model_id": "None",
            "provider": "openai:completions",
        }
    }
)
