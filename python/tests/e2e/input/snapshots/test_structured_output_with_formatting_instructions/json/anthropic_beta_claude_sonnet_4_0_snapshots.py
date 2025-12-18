from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'json' is not supported by provider 'anthropic:beta' for model 'anthropic-beta/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:json",
            "formatting_mode": "json",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_id": "anthropic:beta",
        }
    }
)
