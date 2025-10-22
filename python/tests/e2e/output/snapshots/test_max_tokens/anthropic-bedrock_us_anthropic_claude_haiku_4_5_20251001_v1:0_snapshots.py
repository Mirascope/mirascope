from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "anthropic-bedrock",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "params": {"max_tokens": 50},
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
# U.S. States (50 total)

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10.\
"""
                    )
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": """\
# U.S. States (50 total)

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10.\
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
        "provider": "anthropic-bedrock",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "params": {"max_tokens": 50},
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
# U.S. States (Alphabetical Order)

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
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": """\
# U.S. States (Alphabetical Order)

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
        "provider": "anthropic-bedrock",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
# U.S. States (50 total)

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10.\
"""
                    )
                ],
                provider="anthropic-bedrock",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": """\
# U.S. States (50 total)

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10.\
""",
                        }
                    ],
                },
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 12,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "anthropic-bedrock",
        "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
        "finish_reason": FinishReason.MAX_TOKENS,
        "messages": [
            UserMessage(content=[Text(text="List all U.S. states.")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
# U.S. States (50 total)

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10.\
"""
                    )
                ],
                provider="anthropic-bedrock",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "type": "text",
                            "text": """\
# U.S. States (50 total)

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida
10.\
""",
                        }
                    ],
                },
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 12,
    }
)
