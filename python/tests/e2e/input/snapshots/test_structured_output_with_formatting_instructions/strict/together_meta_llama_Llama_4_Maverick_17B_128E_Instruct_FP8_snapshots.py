from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FeatureNotSupportedError",
            "args": "(\"Feature 'strict formatting mode' is not supported by provider 'together' for model 'together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8'\",)",
            "feature": "strict formatting mode",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_id": "together",
        }
    }
)
