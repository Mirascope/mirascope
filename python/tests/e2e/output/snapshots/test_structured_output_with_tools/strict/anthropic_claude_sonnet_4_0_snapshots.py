from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "None",
            "provider": "anthropic",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "None",
            "provider": "anthropic",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "None",
            "provider": "anthropic",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "None",
            "provider": "anthropic",
        }
    }
)
