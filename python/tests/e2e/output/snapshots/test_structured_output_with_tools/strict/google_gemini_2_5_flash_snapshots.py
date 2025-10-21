from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "None",
            "provider": "google",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "None",
            "provider": "google",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "None",
            "provider": "google",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "None",
            "provider": "google",
        }
    }
)
