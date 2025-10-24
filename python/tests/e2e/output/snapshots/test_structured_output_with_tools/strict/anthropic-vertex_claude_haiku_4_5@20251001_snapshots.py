from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic-vertex' for model 'claude-haiku-4-5@20251001'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-haiku-4-5@20251001",
            "provider": "anthropic-vertex",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic-vertex' for model 'claude-haiku-4-5@20251001'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-haiku-4-5@20251001",
            "provider": "anthropic-vertex",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic-vertex' for model 'claude-haiku-4-5@20251001'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-haiku-4-5@20251001",
            "provider": "anthropic-vertex",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "FormattingModeNotSupportedError",
            "args": "(\"Formatting mode 'strict' is not supported by provider 'anthropic-vertex' for model 'claude-haiku-4-5@20251001'\",)",
            "feature": "formatting_mode:strict",
            "formatting_mode": "strict",
            "model_id": "claude-haiku-4-5@20251001",
            "provider": "anthropic-vertex",
        }
    }
)
