from inline_snapshot import snapshot

test_snapshot = snapshot(
    {
        "response1": "**ToolCall (star_wars_tool):** {}",
        "usage1": {
            "input_tokens": 4749,
            "output_tokens": 38,
            "cache_read_tokens": 0,
            "cache_write_tokens": 4602,
            "reasoning_tokens": 0,
            "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=4602), cache_creation_input_tokens=4602, cache_read_input_tokens=0, input_tokens=147, output_tokens=38, server_tool_use=None, service_tier='standard')",
            "total_tokens": 4787,
        },
        "response2": "**ToolCall (star_wars_tool):** {}",
        "usage2": {
            "input_tokens": 4753,
            "output_tokens": 38,
            "cache_read_tokens": 4602,
            "cache_write_tokens": 0,
            "reasoning_tokens": 0,
            "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=4602, input_tokens=151, output_tokens=38, server_tool_use=None, service_tier='standard')",
            "total_tokens": 4791,
        },
    }
)
