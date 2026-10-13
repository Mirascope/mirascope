from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Google does not support URL-referenced images. Try `llm.Image.download(...) or `llm.Image.download_async(...)`',)",
            "feature": "url_image_source",
            "model_id": "None",
            "provider_id": "google",
        }
    }
)
