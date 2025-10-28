from inline_snapshot import snapshot

sync_snapshot = snapshot(
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
async_snapshot = snapshot(
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
stream_snapshot = snapshot(
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
async_stream_snapshot = snapshot(
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
