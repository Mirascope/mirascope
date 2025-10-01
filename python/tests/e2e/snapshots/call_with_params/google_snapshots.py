from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
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
                },
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
To find the sum of 4200 and 42, you add them together:

4200
+   42
------
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": [],
    }
)
async_snapshot = snapshot(
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
                },
                "finish_reason": None,
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
To find the sum of 4200 and 42, you add them together:

4200
+  42
-----
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
            },
        ),
        "logging": [],
    }
)
stream_snapshot = snapshot(
    {
        "response": (
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
To find the sum of 4200 and 42, you add them together:

4200
+   42
------
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 3,
            },
        ),
        "logging": [],
    }
)
async_stream_snapshot = snapshot(
    {
        "response": (
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
To find the sum of 4200 and 42, you add them together:

4200
+   42
------
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 3,
            },
        ),
        "logging": [],
    }
)
