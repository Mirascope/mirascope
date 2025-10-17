from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
To calculate 4200 + 42:

*   **Hundreds, thousands:** 4200
*   **Tens, ones:** 42

Adding them together:
4200
+  42
-----
4242

So, 4200 + 42 = **4242**.\
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
To calculate 4200 + 42:

*   **Hundreds, thousands:** 4200
*   **Tens, ones:** 42

Adding them together:
4200
+  42
-----
4242

So, 4200 + 42 = **4242**.\
""",
                        }
                    ],
                    "role": "model",
                },
            ),
        ],
        "format": None,
        "tools": [],
    }
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
To find the sum of 4200 and 42, we add them together:

4200
+   42
-----
4242

So, 4200 + 42 = **4242**.\
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
To find the sum of 4200 and 42, we add them together:

4200
+   42
-----
4242

So, 4200 + 42 = **4242**.\
""",
                        }
                    ],
                    "role": "model",
                },
            ),
        ],
        "format": None,
        "tools": [],
    }
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
To find the sum of 4200 + 42, we can align the numbers by their place values:

  4200
+   42
------
  4242

So, 4200 + 42 = **4242**.\
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
To find the sum of 4200 + 42, we can align the numbers by their place values:

  4200
+   42
------
  4242

So, 42\
""",
                        },
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
                            "text": "00 + 42 = **4242**.",
                        },
                    ],
                    "role": "model",
                },
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 4,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="What is 4200 + 42?")]),
            AssistantMessage(
                content=[Text(text="4200 + 42 = **4242**")],
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
                            "text": "4200 + 42 = **4242**",
                        }
                    ],
                    "role": "model",
                },
            ),
        ],
        "format": None,
        "tools": [],
        "n_chunks": 3,
    }
)
