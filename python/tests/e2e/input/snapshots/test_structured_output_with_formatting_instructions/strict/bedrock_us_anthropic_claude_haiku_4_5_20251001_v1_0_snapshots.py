from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict' is not supported by provider 'anthropic' for model 'bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0'\",)",
            "feature": "formatting_mode:strict",
            "model_id": "bedrock/us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "provider_id": "anthropic",
        }
    }
)
