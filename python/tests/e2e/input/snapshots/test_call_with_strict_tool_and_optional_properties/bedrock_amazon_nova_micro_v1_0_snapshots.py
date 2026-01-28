from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Bedrock Converse API does not support strict tools.',)",
            "feature": "strict tools",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_id": "bedrock:boto3",
        }
    }
)
