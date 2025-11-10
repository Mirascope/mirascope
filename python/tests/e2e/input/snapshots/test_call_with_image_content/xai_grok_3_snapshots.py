from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('This Grok model does not support image inputs. Use grok-2-vision for image understanding, or download the image locally and convert it to text instead.',)",
            "feature": "image",
            "model_id": "None",
            "provider": "xai",
        }
    }
)
