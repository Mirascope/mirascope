from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google' for model 'google/gemini-2.5-flash'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "google/gemini-2.5-flash",
            "provider_id": "google",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google' for model 'google/gemini-2.5-flash'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "google/gemini-2.5-flash",
            "provider_id": "google",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google' for model 'google/gemini-2.5-flash'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "google/gemini-2.5-flash",
            "provider_id": "google",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'formatting_mode:json with tools' is not supported by provider 'google' for model 'google/gemini-2.5-flash'\",)",
            "feature": "formatting_mode:json with tools",
            "model_id": "google/gemini-2.5-flash",
            "provider_id": "google",
        }
    }
)
