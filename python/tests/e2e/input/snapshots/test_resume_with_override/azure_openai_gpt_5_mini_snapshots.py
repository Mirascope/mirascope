from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "azure",
            "model_id": "azure/openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 37,
                "output_tokens": 321,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 256,
                "raw": "CompletionUsage(completion_tokens=321, prompt_tokens=37, total_tokens=358, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=256, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 358,
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
                            text="Sorry — that was incorrect. I was created and trained by OpenAI. I don’t have independent browsing to verify beyond my internal system info, but my development and training are by OpenAI (using a mixture of licensed data, human-created data, and publicly available text)."
                        )
                    ],
                    provider_id="azure",
                    model_id="azure/openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini",
                    raw_message={
                        "content": "Sorry — that was incorrect. I was created and trained by OpenAI. I don’t have independent browsing to verify beyond my internal system info, but my development and training are by OpenAI (using a mixture of licensed data, human-created data, and publicly available text).",
                        "role": "assistant",
                        "annotations": [],
                    },
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
