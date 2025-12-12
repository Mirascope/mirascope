from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Cannot use completions model with responses client: openai/gpt-4o-mini:completions',)",
            "feature": "completions API",
            "model_id": "openai/gpt-4o-mini:completions",
            "provider_id": "openai:responses",
        }
    }
)
