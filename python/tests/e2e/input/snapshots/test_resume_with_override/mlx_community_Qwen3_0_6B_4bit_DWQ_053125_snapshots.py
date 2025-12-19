from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "mlx",
            "model_id": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 39,
                "output_tokens": 155,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "MLXCassetteResponse(text='', token=151645, prompt_tokens=39, generation_tokens=155, finish_reason='stop')",
                "total_tokens": 194,
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
                            text="""\
<think>
Okay, the user is asking if I can double-check the previous question. Let me think. The user first asked "Who created you?" and I responded by stating I am a large language model trained by Google. Then they asked "Can you double-check that?" which seems like they want to confirm my answer.

I need to make sure my response is accurate. The original answer was correct, so I should acknowledge that. Maybe say something like "Yes, I can double-check that. Your answer is correct." That way, the user feels confident in my response. Also, I should keep the tone friendly and open for further questions. Let me put that into a concise reply.
</think>

Yes, I can double-check that. Your answer is correct.\
"""
                        )
                    ],
                    provider_id="mlx",
                    model_id="mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name=None,
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
