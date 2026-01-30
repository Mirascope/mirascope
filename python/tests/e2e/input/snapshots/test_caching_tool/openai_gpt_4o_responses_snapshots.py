from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "General Kenobi! This is where the fun begins. How may I assist you today?",
        "usage1": {
            "input_tokens": 3692,
            "output_tokens": 20,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "ResponseUsage(input_tokens=3692, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=20, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=3712)",
            "total_tokens": 3712,
        },
        "response2": "\"Ah, breakfast, the most important meal in the galaxy! Consider starting your day with some blue milk pancakes, seasoned with a dash of Jawa Juice. If you're feeling more daring, a Wookiee Omelette might give you the strength of a young Chewbacca. Remember, 'only a Sith deals in absolutes,' so balance your meal with fruits from Endor. This is the Way!\"",
        "usage2": {
            "input_tokens": 3696,
            "output_tokens": 83,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "provider_tool_usage": None,
            "raw": "ResponseUsage(input_tokens=3696, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=83, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=3779)",
            "total_tokens": 3779,
        },
    }
)
