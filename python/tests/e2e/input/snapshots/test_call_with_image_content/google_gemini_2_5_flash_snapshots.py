from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Have not implemented conversion for image',)",
        }
    }
)
