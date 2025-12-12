from inline_snapshot import snapshot

sync_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Tool usage is not supported.',)",
        }
    }
)
async_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Tool usage is not supported.',)",
        }
    }
)
stream_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Tool usage is not supported.',)",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Tool usage is not supported.',)",
        }
    }
)
