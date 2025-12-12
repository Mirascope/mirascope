from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Formatting is not supported.',)",
        }
    }
)
