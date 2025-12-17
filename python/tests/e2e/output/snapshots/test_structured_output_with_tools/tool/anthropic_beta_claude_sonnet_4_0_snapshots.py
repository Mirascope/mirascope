from inline_snapshot import snapshot

sync_snapshot = snapshot(
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
async_snapshot = snapshot(
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
stream_snapshot = snapshot(
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
async_stream_snapshot = snapshot(
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
