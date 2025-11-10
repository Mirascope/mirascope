from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Anthropic Vertex AI does not support URL-referenced images. Try `llm.Image.download(...)` or `llm.Image.download_async(...)`',)",
            "feature": "url_image_source",
            "model_id": "None",
            "provider": "anthropic-vertex",
        }
    }
)
