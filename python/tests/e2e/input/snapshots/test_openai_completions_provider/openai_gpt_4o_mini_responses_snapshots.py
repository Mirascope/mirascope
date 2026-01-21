from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": '("Can\'t use completions client for responses model: openai/gpt-4o-mini:responses",)',
            "feature": "responses API",
            "model_id": "openai/gpt-4o-mini:responses",
            "provider_id": "openai:completions",
        }
    }
)
