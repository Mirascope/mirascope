from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "**ToolCall (star_wars_tool):** {}",
        "usage1": {
            "input_tokens": 147,
            "output_tokens": 38,
            "cache_read_tokens": 0,
            "cache_write_tokens": 4602,
            "reasoning_tokens": 0,
        },
        "response2": "**ToolCall (star_wars_tool):** {}",
        "usage2": {
            "input_tokens": 151,
            "output_tokens": 38,
            "cache_read_tokens": 4602,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
        },
    }
)
