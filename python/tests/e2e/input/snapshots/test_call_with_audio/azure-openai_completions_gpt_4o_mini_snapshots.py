from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "exception": {
            "type": "NotImplementedError",
            "args": "('Unsupported user content part type: audio',)",
        }
    }
)
