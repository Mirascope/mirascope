from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('provider \"openai\" does not support audio inputs when using :responses api. Try appending :completions to your model instead.',)",
            "feature": "audio input",
            "model_id": "None",
            "provider_id": "openai",
        }
    }
)
