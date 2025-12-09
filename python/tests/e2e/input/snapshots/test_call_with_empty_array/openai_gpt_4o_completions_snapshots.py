from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "ValueError",
            "args": "('Empty array may not be used as message content',)",
        }
    }
)
