from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "openai",
            "model_id": "openai/gpt-5-mini:completions",
            "provider_model_name": "gpt-5-mini:completions",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 37,
                "output_tokens": 349,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 256,
                "raw": "CompletionUsage(completion_tokens=349, prompt_tokens=37, total_tokens=386, completion_tokens_details=CompletionTokensDetails(accepted_prediction_tokens=0, audio_tokens=0, reasoning_tokens=256, rejected_prediction_tokens=0), prompt_tokens_details=PromptTokensDetails(audio_tokens=0, cached_tokens=0))",
                "total_tokens": 386,
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
                            text="Sorry — that was incorrect. I was created and am maintained by OpenAI (I’m ChatGPT). I was trained on a mixture of licensed data, data created by human trainers, and publicly available text, but I don’t have access to my training records or the ability to “double-check” those records. If you’d like, I can give more background on OpenAI or how models like me are trained."
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini:completions",
                    provider_model_name="gpt-5-mini:completions",
                    raw_message={
                        "content": "Sorry — that was incorrect. I was created and am maintained by OpenAI (I’m ChatGPT). I was trained on a mixture of licensed data, data created by human trainers, and publicly available text, but I don’t have access to my training records or the ability to “double-check” those records. If you’d like, I can give more background on OpenAI or how models like me are trained.",
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
