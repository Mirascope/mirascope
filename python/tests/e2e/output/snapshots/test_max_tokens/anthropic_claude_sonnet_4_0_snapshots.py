from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {"max_tokens": 50},
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are all 50 U.S. states listed alphabetically:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9.\
"""
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": """\
Here are all 50 U.S. states listed alphabetically:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9.\
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
)
async_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {"max_tokens": 50},
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
                provider="anthropic",
                model_id="claude-sonnet-4-0",
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
)
stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
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
                provider="anthropic",
                model_id="claude-sonnet-4-0",
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
        "n_chunks": 9,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
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
                provider="anthropic",
                model_id="claude-sonnet-4-0",
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
        "n_chunks": 9,
    }
)
