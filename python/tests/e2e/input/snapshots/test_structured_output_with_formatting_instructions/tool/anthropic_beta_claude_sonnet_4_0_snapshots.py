from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'tool' is not supported by provider 'anthropic:beta' for model 'anthropic-beta/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:tool",
            "formatting_mode": "tool",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_id": "anthropic:beta",
        }
    }
)
