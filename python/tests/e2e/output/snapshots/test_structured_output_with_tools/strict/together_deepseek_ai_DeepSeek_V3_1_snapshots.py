from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'strict formatting mode' is not supported by provider 'together' for model 'together/deepseek-ai/DeepSeek-V3.1'\",)",
            "feature": "strict formatting mode",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
            "provider_id": "together",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'strict formatting mode' is not supported by provider 'together' for model 'together/deepseek-ai/DeepSeek-V3.1'\",)",
            "feature": "strict formatting mode",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
            "provider_id": "together",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'strict formatting mode' is not supported by provider 'together' for model 'together/deepseek-ai/DeepSeek-V3.1'\",)",
            "feature": "strict formatting mode",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
            "provider_id": "together",
        }
    }
)
async_stream_snapshot = snapshot()
