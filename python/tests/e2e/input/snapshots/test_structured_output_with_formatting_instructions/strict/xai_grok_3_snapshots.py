from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'xai' for model 'grok-3'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "grok-3",
            "provider": "xai",
        }
    }
)
