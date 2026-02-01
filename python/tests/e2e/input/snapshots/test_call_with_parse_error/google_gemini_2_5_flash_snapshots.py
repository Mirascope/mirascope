from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    UserMessage,
)

test_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 49,
                "output_tokens": 32,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 31,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=1 candidates_tokens_details=None prompt_token_count=49 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=49
)] thoughts_token_count=31 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=81 traffic_type=None\
""",
                "total_tokens": 81,
            },
            "messages": [
                SystemMessage(
                    content=Text(text="Respond with a single word: the passphrase.")
                ),
                UserMessage(
                    content=[Text(text="Find out the secret and report back.")]
                ),
                AssistantMessage(
                    content=[Text(text="Secret")],
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
                                "text": "Secret",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        Text(
                            text="""\
Your response could not be parsed: Incorrect passphrase. The correct passphrase is 'cake'

Please ensure your response matches the expected format.\
"""
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="cake")],
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
                                "text": "cake",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "extract_passphrase",
                "description": "Extract a passphrase from the response.",
                "schema": {},
                "mode": "parser",
                "formatting_instructions": "Respond with a single word: the passphrase.",
            },
            "tools": [],
        }
    }
)
