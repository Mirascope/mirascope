from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Bedrock Converse API does not support audio input.',)",
            "feature": "audio input",
            "model_id": "None",
            "provider_id": "bedrock:boto3",
        }
    }
)
