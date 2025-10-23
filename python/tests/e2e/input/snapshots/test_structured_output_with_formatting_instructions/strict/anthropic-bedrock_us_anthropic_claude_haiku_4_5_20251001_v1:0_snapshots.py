from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic-bedrock'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "None",
            "provider": "anthropic-bedrock",
        }
    }
)
