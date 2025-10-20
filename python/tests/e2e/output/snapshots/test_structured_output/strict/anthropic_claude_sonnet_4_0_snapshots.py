from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-sonnet-4-0",
            "provider": "anthropic",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-sonnet-4-0",
            "provider": "anthropic",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-sonnet-4-0",
            "provider": "anthropic",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-sonnet-4-0",
            "provider": "anthropic",
        }
    }
)
