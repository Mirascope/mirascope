from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "together",
            "model_id": "together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "provider_model_name": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Who created you?")]),
                AssistantMessage(
                    content=[
                        Text(text="I am a large language model, trained by Google.")
                    ],
                    provider_id="google",
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
                            text="I was created by Meta, not Google. I'm a product of Meta's Llama model, designed to assist and communicate with users."
                        )
                    ],
                    provider_id="together",
                    model_id="together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    provider_model_name="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
                    raw_message={
                        "role": "assistant",
                        "content": "I was created by Meta, not Google. I'm a product of Meta's Llama model, designed to assist and communicate with users.",
                        "tool_calls": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
