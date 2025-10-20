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
            "provider": "google",
            "model_id": "gemini-2.5-flash",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[Text(text="Here is a list of all 50 U")],
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
                                "text": "Here is a list of all 50 U",
                            }
                        ],
                        "role": "model",
                    },
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
            "provider": "google",
            "model_id": "gemini-2.5-flash",
            "params": {"max_tokens": 50},
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all U.S. states, listed alphabetically:

1.  Alabama\
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
Here are all U.S. states, listed alphabetically:

1.  Alabama\
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
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider": "google",
            "model_id": "gemini-2.5-flash",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[Text(text="Here are all 50 U.S.")],
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
                                "text": "Here are all 50 U.S.",
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
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "google",
            "model_id": "gemini-2.5-flash",
            "finish_reason": FinishReason.MAX_TOKENS,
            "messages": [
                UserMessage(content=[Text(text="List all U.S. states.")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are all 50 U.S. states, listed alphabetically:

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
Here are all 50 U.S. states, listed alphabetically:

""",
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
    }
)
