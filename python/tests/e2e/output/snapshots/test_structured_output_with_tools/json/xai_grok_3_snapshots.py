from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Grok JSON format output may deviate from expected schema; use tool mode or strict mode instead.',)",
            "feature": "structured_output_json",
            "model_id": "None",
            "provider": "xai",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Grok JSON format output may deviate from expected schema; use tool mode or strict mode instead.',)",
            "feature": "structured_output_json",
            "model_id": "None",
            "provider": "xai",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Grok JSON format output may deviate from expected schema; use tool mode or strict mode instead.',)",
            "feature": "structured_output_json",
            "model_id": "None",
            "provider": "xai",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Grok JSON format output may deviate from expected schema; use tool mode or strict mode instead.',)",
            "feature": "structured_output_json",
            "model_id": "None",
            "provider": "xai",
        }
    }
)
