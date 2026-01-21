from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! A surprise to be sure, but a welcome one. How may I assist you on your galactic journey today?",
        "usage1": {
            "input_tokens": 3659,
            "output_tokens": 28,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "ResponseUsage(input_tokens=3659, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=28, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=3687)",
            "total_tokens": 3687,
        },
        "response2": '"Start your day like a true Jedi with a breakfast worthy of the Jedi Council! How about some blue milk and Bantha toast? Or maybe some Endorian fruit salad to fuel your lightsaber skills. This is the Way to a strong start."',
        "usage2": {
            "input_tokens": 3663,
            "output_tokens": 51,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "ResponseUsage(input_tokens=3663, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=51, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=3714)",
            "total_tokens": 3714,
        },
    }
)
