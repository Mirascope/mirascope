from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "google",
                "model_id": "google/gemini-2.5-flash",
                "provider_model_name": "gemini-2.5-flash",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
To calculate 4200 + 42, you can add the numbers together:

4200
+ 42
-----
"""
                            )
                        ],
                        provider="google",
                        model_id="google/gemini-2.5-flash",
                        provider_model_name="gemini-2.5-flash",
                        raw_message={
                            "parts": [
                                {
                                    "function_call": None,
                                    "code_execution_result": None,
                                    "executable_code": None,
                                    "file_data": None,
                                    "function_response": None,
                                    "inline_data": None,
                                    "text": """\
To calculate 4200 + 42, you can add the numbers together:

4200
+ 42
-----
""",
                                    "thought": None,
                                    "thought_signature": None,
                                    "video_metadata": None,
                                }
                            ],
                            "role": "model",
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        )
    }
)
