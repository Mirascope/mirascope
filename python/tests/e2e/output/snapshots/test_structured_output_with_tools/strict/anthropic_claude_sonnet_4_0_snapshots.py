from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'anthropic/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_id": "anthropic",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'anthropic/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_id": "anthropic",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'anthropic/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_id": "anthropic",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic' for model 'anthropic/claude-sonnet-4-0'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_id": "anthropic",
        }
    }
)
