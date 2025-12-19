from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=15, output_tokens=50, server_tool_use=None, service_tier='standard')",
                "total_tokens": 65,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=15, output_tokens=50, server_tool_use=None, service_tier='standard')",
                "total_tokens": 65,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
""",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "provider_model_name": "claude-sonnet-4-0",
            "model_id": "anthropic/claude-sonnet-4-0",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
""",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 65,
            },
            "n_chunks": 9,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "provider_model_name": "claude-sonnet-4-0",
            "model_id": "anthropic/claude-sonnet-4-0",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Here are all 50 U.S. states in alphabetical order:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9\
""",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 15,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 65,
            },
            "n_chunks": 12,
        }
    }
)
