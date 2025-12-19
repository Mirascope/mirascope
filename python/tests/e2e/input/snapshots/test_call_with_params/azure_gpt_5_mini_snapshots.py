from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "logs": [
            "Skipping unsupported parameter: top_k=50 (provider: openai)",
            "Skipping unsupported parameter: thinking=False (provider: openai)",
        ]
    }
)
