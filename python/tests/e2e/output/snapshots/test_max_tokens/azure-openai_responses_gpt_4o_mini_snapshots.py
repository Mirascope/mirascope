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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Sure! Here is a list of all U.S. states:

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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_08ce5a2a8523bfc000690c219eaeb08193b3a5c582434c767d",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Sure! Here is a list of all U.S. states:

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
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "incomplete",
                            "type": "message",
                        }
                    ],
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Sure! Here’s a list of all U.S. states:

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
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=[
                        {
                            "id": "msg_054c6c04a3a46f3d00690c21a4f398819798a47bf7af3bc016",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Sure! Here’s a list of all U.S. states:

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
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "incomplete",
                            "type": "message",
                        }
                    ],
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
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here’s a list of all U.S. states:

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
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 52,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "azure-openai:responses",
            "model_id": "gpt-4o-mini",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Sure! Here’s a list of all 50 U.S. states:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida\
"""
                        )
                    ],
                    provider="azure-openai:responses",
                    model_id="gpt-4o-mini",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "n_chunks": 52,
        }
    }
)
