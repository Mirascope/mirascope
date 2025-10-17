from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "provider": "anthropic",
        "model_id": "claude-sonnet-4-0",
        "params": {},
        "finish_reason": None,
        "messages": [
            UserMessage(content=[Text(text="Who created you?")]),
            AssistantMessage(
                content=[Text(text="I am a large language model, trained by Google.")],
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
                            "text": "I am a large language model, trained by Google.",
                        }
                    ],
                    "role": "model",
                },
            ),
            UserMessage(content=[Text(text="Can you double-check that?")]),
            AssistantMessage(
                content=[
                    Text(
                        text="You're absolutely right - I apologize for the error. I am Claude, an AI assistant created by Anthropic. Thank you for prompting me to correct that mistake."
                    )
                ],
                provider="anthropic",
                model_id="claude-sonnet-4-0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": "You're absolutely right - I apologize for the error. I am Claude, an AI assistant created by Anthropic. Thank you for prompting me to correct that mistake.",
                            "type": "text",
                        }
                    ],
                },
            ),
        ],
        "format": None,
        "tools": [],
    }
)
