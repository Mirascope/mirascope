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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 14,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=14, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=50, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=64)",
                "total_tokens": 64,
            },
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Sure! Here is a list of all 50 U.S. states:

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
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_043a58ea47ac058e0068f966c13978819797bd165a2ecefb31",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Sure! Here is a list of all 50 U.S. states:

1. Alabama
2. Alaska
3. Arizona
4. Arkansas
5. California
6. Colorado
7. Connecticut
8. Delaware
9. Florida\
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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "usage": {
                "input_tokens": 14,
                "output_tokens": 50,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "ResponseUsage(input_tokens=14, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=50, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=64)",
                "total_tokens": 64,
            },
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
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "id": "msg_0d9a87a8899d31be0068f966c376e481948b002160f58809be",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
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
            "provider_id": "openai",
            "provider_model_name": "gpt-4o:responses",
            "model_id": "openai/gpt-4o:responses",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Sure! Here is a list of all 50 U.S. states:

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
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": None,
            "n_chunks": 52,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "provider_model_name": "gpt-4o:responses",
            "model_id": "openai/gpt-4o:responses",
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
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
            "usage": None,
            "n_chunks": 52,
        }
    }
)
