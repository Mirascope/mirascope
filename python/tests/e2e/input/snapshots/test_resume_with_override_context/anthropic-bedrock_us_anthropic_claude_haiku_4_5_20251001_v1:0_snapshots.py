from inline_snapshot import snapshot

from mirascope.llm import AssistantMessage, Text, UserMessage

test_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Who created you?")]),
                AssistantMessage(
                    content=[
                        Text(text="I am a large language model, trained by Google.")
                    ],
                    provider="google",
                    model_id="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "I am a large language model, trained by Google.",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(content=[Text(text="Can you double-check that?")]),
                AssistantMessage(
                    content=[
                        Text(
                            text="You're right to ask me to double-check. I apologize for the error. I'm Claude, and I was created by Anthropic, not Google. Thank you for catching that mistake."
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "You're right to ask me to double-check. I apologize for the error. I'm Claude, and I was created by Anthropic, not Google. Thank you for catching that mistake.",
                                "type": "text",
                            }
                        ],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
