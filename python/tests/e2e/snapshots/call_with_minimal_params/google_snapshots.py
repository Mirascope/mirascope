from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    FinishReason,
    Text,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": (
            {
                "provider": "google",
                "model_id": "gemini-2.5-flash",
                "params": {"temperature": 0.7, "max_tokens": 120, "top_p": 0.3},
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here is a list of all 50 U.S. states:

1.  Alabama
2.  Alaska
3.  Arizona
4.  Arkansas
5.  California
6.  Colorado
7.  Connecticut
8.  Delaware
9.  Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14.\
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
                "params": {"temperature": 0.7, "max_tokens": 120, "top_p": 0.3},
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here is a list of all 50 U.S. states:

1.  Alabama
2.  Alaska
3.  Arizona
4.  Arkansas
5.  California
6.  Colorado
7.  Connecticut
8.  Delaware
9.  Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14.\
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
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here is a list of all 50 U.S. states:

1.  Alabama
2.  Alaska
3.  Arizona
4.  Arkansas
5.  California
6.  Colorado
7.  Connecticut
8.  Delaware
9.  Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14.\
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 4,
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
                "finish_reason": FinishReason.MAX_TOKENS,
                "messages": [
                    UserMessage(content=[Text(text="List all U.S. states")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
Here is a list of all 50 U.S. states:

1.  Alabama
2.  Alaska
3.  Arizona
4.  Arkansas
5.  California
6.  Colorado
7.  Connecticut
8.  Delaware
9.  Florida
10. Georgia
11. Hawaii
12. Idaho
13. Illinois
14.\
"""
                            )
                        ]
                    ),
                ],
                "format": None,
                "tools": [],
                "n_chunks": 4,
            },
        ),
        "logging": [],
    }
)
