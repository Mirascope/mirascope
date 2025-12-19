from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! This is where the fun begins. How may the Force be with you today?",
        "usage1": {
            "input_tokens": 3692,
            "output_tokens": 22,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
        },
        "response2": 'Ah, a crucial decision, like selecting the right hyperdrive motivator. Perhaps some blue milk pancakes or a hearty serving of Jawa Juice with toasted Bantha bread. "This is where the fun begins!" Choose wisely, young Padawan.',
        "usage2": {
            "input_tokens": 3696,
            "output_tokens": 50,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
        },
    }
)
