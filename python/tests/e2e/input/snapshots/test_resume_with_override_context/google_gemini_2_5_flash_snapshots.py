from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I was created by Anthropic.")],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": "I was created by Anthropic.",
                            "type": "text",
                        }
                    ],
                },
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
My apologies! You are absolutely right to ask me to double-check.

I am a large language model, trained by Google.

Thank you for catching that!\
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
My apologies! You are absolutely right to ask me to double-check.

I am a large language model, trained by Google.

Thank you for catching that!\
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
