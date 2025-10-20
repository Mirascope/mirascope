from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google' for model 'gemini-2.5-flash'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "gemini-2.5-flash",
            "provider": "google",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google' for model 'gemini-2.5-flash'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "gemini-2.5-flash",
            "provider": "google",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google' for model 'gemini-2.5-flash'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "gemini-2.5-flash",
            "provider": "google",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:strict with tools' is not supported by provider 'google' for model 'gemini-2.5-flash'\",)",
            "feature": "formatting_mode:strict with tools",
            "model_id": "gemini-2.5-flash",
            "provider": "google",
        }
    }
)
