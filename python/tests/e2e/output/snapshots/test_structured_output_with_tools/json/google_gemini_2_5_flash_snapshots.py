from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "None",
            "provider_id": "google",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "None",
            "provider_id": "google",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "None",
            "provider_id": "google",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "None",
            "provider_id": "google",
        }
    }
)
