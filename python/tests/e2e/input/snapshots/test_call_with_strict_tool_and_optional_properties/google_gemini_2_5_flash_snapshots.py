from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Google does not support strict mode for tools. Set strict=False on your tools or omit the strict parameter.',)",
            "feature": "strict tools",
            "model_id": "google/gemini-2.5-flash",
            "provider_id": "google",
        }
    }
)
