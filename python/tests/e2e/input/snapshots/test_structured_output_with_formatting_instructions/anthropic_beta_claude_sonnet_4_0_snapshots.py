from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'anthropic-beta/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_id": "anthropic",
        }
    }
)
