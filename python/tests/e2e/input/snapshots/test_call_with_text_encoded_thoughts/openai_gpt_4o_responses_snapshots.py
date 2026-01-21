from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response": "28657",
        "logs": [
            "Skipping unsupported parameter: thinking={'encode_thoughts_as_text': True, 'level': 'minimal'} (provider: openai with model_id: openai/gpt-4o:responses)"
        ],
    }
)
