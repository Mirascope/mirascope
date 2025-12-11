from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider": "mlx",
            "model_id": "mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "provider_model_name": "mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
            "params": {},
            "finish_reason": None,
            "messages": [
                UserMessage(content=[Text(text="Who created you?")]),
                AssistantMessage(
                    content=[
                        Text(text="I am a large language model, trained by Google.")
                    ],
                    provider="google",
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
Okay, the user is asking if I can double-check the previous question. Let me think. The user first asked "Who created you?" and I responded by stating I am a large language model trained by Google. Then they asked "Can you double-check that?" so I need to confirm that my answer is correct.

I should make sure that my response is accurate. The user might be testing if I understand the question correctly. Since I'm trained by Google, my answer is correct. I should acknowledge that and maybe offer to help with anything else. Let me check if there's any other information I need to confirm. No, the answer seems correct. I'll respond clearly and offer further assistance.
</think>

I can double-check that. My answer is correct. If you have any other questions, feel free to ask!\
"""
                        )
                    ],
                    provider="mlx",
                    model_id="mlx/mlx-community/Qwen3-0.6B-4bit-DWQ-053125",
                    provider_model_name=None,
                    raw_message=None,
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
