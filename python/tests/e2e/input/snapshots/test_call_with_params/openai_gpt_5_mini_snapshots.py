from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "logs": [
            "Skipping unsupported parameter: top_k=50 (provider: openai)",
            "Skipping unsupported parameter: seed=42 (provider: openai)",
            "Skipping unsupported parameter: stop_sequences=['4242'] (provider: openai)",
        ]
    }
)
