from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Strict tools require a model that supports structured outputs. Use a newer model like claude-sonnet-4-5 or set strict=False on your tools.',)",
            "feature": "strict tools",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_id": "anthropic",
        }
    }
)
