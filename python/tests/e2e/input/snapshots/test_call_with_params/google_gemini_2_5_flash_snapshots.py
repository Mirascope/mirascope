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
                "model_id": "gemini-2.5-flash",
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
To find the sum of 4200 and 42, you can add them together:

   4200
+    42
------
   \
"""
                            )
                        ],
                        provider="google",
                        model_id="gemini-2.5-flash",
                        raw_message={
                            "parts": [
                                {
                                    "video_metadata": None,
                                    "thought": None,
                                    "inline_data": None,
                                    "file_data": None,
                                    "thought_signature": None,
                                    "code_execution_result": None,
                                    "executable_code": None,
                                    "function_call": None,
                                    "function_response": None,
                                    "text": """\
To find the sum of 4200 and 42, you can add them together:

   4200
+    42
------
   \
""",
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
