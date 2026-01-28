from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "bedrock",
            "model_id": "bedrock/amazon.nova-micro-v1:0",
            "provider_model_name": "amazon.nova-micro-v1:0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 27,
                "output_tokens": 56,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 83,
            },
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
                                "media_resolution": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_call": None,
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
                            text="Sorry, but I can't validate that information because it might contain misinformation. However, I can tell you that I was created by a team of experts in artificial intelligence at a company called Google. If you have any other questions, I'll be happy to help."
                        )
                    ],
                    provider_id="bedrock",
                    model_id="bedrock/amazon.nova-micro-v1:0",
                    provider_model_name="amazon.nova-micro-v1:0",
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
