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
            "model_id": "openai/gpt-5-mini",
            "provider_model_name": "gpt-5-mini:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 37,
                "output_tokens": 306,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 256,
                "raw": "ResponseUsage(input_tokens=37, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=306, output_tokens_details=OutputTokensDetails(reasoning_tokens=256), total_tokens=343)",
                "total_tokens": 343,
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
Sorry — that was incorrect. I was created and developed by OpenAI. \n\

If you’d like, I can explain more about how models like me are trained or what kind of data and safety review goes into development.\
"""
                        )
                    ],
                    provider_id="openai",
                    model_id="openai/gpt-5-mini",
                    provider_model_name="gpt-5-mini:responses",
                    raw_message=[
                        {
                            "id": "rs_0ef97c5c81fc0ea30069492dc7fb348195a7dc4563bcf6e3f5",
                            "summary": [],
                            "type": "reasoning",
                        },
                        {
                            "id": "msg_0ef97c5c81fc0ea30069492dcb7be88195800d5b2bdf815c8d",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Sorry — that was incorrect. I was created and developed by OpenAI. \n\

If you’d like, I can explain more about how models like me are trained or what kind of data and safety review goes into development.\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                        },
                    ],
                ),
            ],
            "format": None,
            "tools": [],
        }
    }
)
