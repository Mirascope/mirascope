from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "params": {"max_tokens": 50},
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Sure! Here are all the U.S. states:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10. Georgia\
"""
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "params": {"max_tokens": 50},
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Sure! Here are all the U.S. states:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10. Georgia\
"""
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Certainly! Here is a list of all U.S. states:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10\
"""
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 52,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here is a list of all U.S. states:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10. Georgia\
"""
                    )
                ]
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 52,
    }
)
