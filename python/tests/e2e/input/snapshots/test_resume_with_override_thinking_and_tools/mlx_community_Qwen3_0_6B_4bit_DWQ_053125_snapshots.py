from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Tool usage is not supported.',)",
        }
    }
)
