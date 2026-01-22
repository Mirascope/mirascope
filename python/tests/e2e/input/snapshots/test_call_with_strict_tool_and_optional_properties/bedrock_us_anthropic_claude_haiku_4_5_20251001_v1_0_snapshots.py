from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Anthropic provider does not support strict tools. Try the beta provider.',)",
            "feature": "strict tools",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_id": "anthropic",
        }
    }
)
