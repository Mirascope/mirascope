from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Bedrock Converse API does not support strict formatting mode.',)",
            "feature": "formatting_mode:strict",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_id": "bedrock:boto3",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Bedrock Converse API does not support strict formatting mode.',)",
            "feature": "formatting_mode:strict",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_id": "bedrock:boto3",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Bedrock Converse API does not support strict formatting mode.',)",
            "feature": "formatting_mode:strict",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_id": "bedrock:boto3",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "('Bedrock Converse API does not support strict formatting mode.',)",
            "feature": "formatting_mode:strict",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_id": "bedrock:boto3",
        }
    }
)
