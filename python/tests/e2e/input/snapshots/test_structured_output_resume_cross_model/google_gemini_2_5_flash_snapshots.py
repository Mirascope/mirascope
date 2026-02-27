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
                "input_tokens": 108,
                "output_tokens": 59,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 38,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=21 candidates_tokens_details=None prompt_token_count=108 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=108
)] thoughts_token_count=38 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=167 traffic_type=None\
""",
                "total_tokens": 167,
            },
            "messages": [
                SystemMessage(
                    content=Text(
                        text="Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output."
                    )
                ),
                UserMessage(
                    content=[Text(text="Choose a lucky number between 1 and 10")]
                ),
                AssistantMessage(
                    content=[Text(text='{"output": 7}')],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_01D2uXpo4viy3Sofz3EV2pQs",
                                "input": {"output": 7},
                                "name": "__mirascope_formatted_output_tool__",
                                "type": "tool_use",
                            }
                        ],
                    },
                ),
                UserMessage(
                    content=[Text(text="Ok, now choose a different lucky number")]
                ),
                AssistantMessage(
                    content=[Text(text='{"output": 3}')],
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
                                "function_call": {
                                    "id": None,
                                    "args": {"output": 3},
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xaf\x01\x01\xbe>\xf6\xfbL\xaf\x03J\x1c\xf1\xba\xfew\xe38q\x9a\xc8\xed\x19\xb0\xe8\n,\x11\xd0wu\x19\x89If\xadc\x0b\xdf\xb2\x8d\xb7.\xca\xd7\xb8qa.\x1fh\xcb\xfa\xe9{\xb1\xc9v\xfe\xcfX\xf4\xdfg\xee\xe5^\x93\xb0>\xa1oS\x1e\xa3)l\x9d\xb2&Xj\xb8(\x95\xe0P\xa0F>\xbc\x98\xe9\xed5\xb5?\x15O\x81\xdf\xf9\xa4p\xe3AL\xc71\xd59\xd8A\xb0\xd1\xb3\xa1'*R\xd6\xbc\xe1\xca\xba\xfb\xea}\xc6\x99Z\xc6\xd3;\x87\x1e\xedH\x18iX\xd4\t\x7f0\xfc\x06\xb8\x1d-\xb6\xc9&C\xad\xe2*\xaf5u\xbc\x1b\xcd\x02\x88]_K\x13\x1d#\xd6\x87<\xc3\x8a\x8c",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": {
                "name": "int",
                "description": None,
                "schema": {
                    "description": "Wrapper for primitive type int",
                    "properties": {"output": {"title": "Output", "type": "integer"}},
                    "required": ["output"],
                    "title": "intOutput",
                    "type": "object",
                },
                "mode": "tool",
                "formatting_instructions": "Always respond to the user's query using the __mirascope_formatted_output_tool__ tool for structured output.",
            },
            "tools": [],
        }
    }
)
