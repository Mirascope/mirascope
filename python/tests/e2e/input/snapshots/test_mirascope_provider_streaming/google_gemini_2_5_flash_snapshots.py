from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="What is 4200 + 42?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
To find the sum of 4200 + 42, you can add them together:

4200
+ 42
-----
4242

So, 4200 + 42 = **4242**.\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
To find the sum of 4200 + 42, you can add them together:

4200
+ 42
-----
4242

So, 4200 + 4\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "2 = **4242**.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [],
            "usage": {
                "input_tokens": 13,
                "output_tokens": 57,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 23,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 70,
            },
            "n_chunks": 4,
        }
    }
)
