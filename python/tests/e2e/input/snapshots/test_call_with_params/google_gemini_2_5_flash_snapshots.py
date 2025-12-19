from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": (
            {
                "provider_id": "google",
                "model_id": "google/gemini-2.5-flash",
                "provider_model_name": "gemini-2.5-flash",
                "params": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "top_p": 0.3,
                    "top_k": 50,
                    "seed": 42,
                    "stop_sequences": ["4242"],
                    "thinking": False,
                    "encode_thoughts_as_text": False,
                },
                "finish_reason": None,
                "usage": {
                    "input_tokens": 13,
                    "output_tokens": 31,
                    "cache_read_tokens": 0,
                    "cache_write_tokens": 0,
                    "reasoning_tokens": 0,
                    "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=31 candidates_tokens_details=None prompt_token_count=13 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=13
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=44 traffic_type=None\
""",
                    "total_tokens": 44,
                },
                "messages": [
                    UserMessage(content=[Text(text="What is 4200 + 42?")]),
                    AssistantMessage(
                        content=[
                            Text(
                                text="""\
To calculate 4200 + 42, you can add the numbers together:

4200
+ 42
-----
"""
                            )
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
                                    "text": """\
To calculate 4200 + 42, you can add the numbers together:

4200
+ 42
-----
""",
                                    "thought": None,
                                    "thought_signature": None,
                                    "video_metadata": None,
                                }
                            ],
                            "role": "model",
                        },
                    ),
                ],
                "format": None,
                "tools": [],
            },
        )
    }
)
