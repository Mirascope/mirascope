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
                "output_tokens": 68,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 47,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=21 candidates_tokens_details=None prompt_token_count=108 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=108
)] thoughts_token_count=47 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=176 traffic_type=None\
""",
                "total_tokens": 176,
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
                                "id": "toolu_01UVmfkTJfYLeZBBNc1HZ5Mf",
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
                                "thought_signature": b"\n\xd3\x01\x01\xbe>\xf6\xfb\x1c\x87\xbf@\x97\x01\x17\\\x186\xda\xd4\xcb\x88elcs\x8c-\xd8AO\xe0\x12\xbc\x13\x8ak\xc8\x9a \x9e\xb3^\xfb\xb7\x87)!d3A\xcb\x93\xfc^\xdd\xfb\xa5)\x02) I\x96\xf8\\#<\xf0\x85!\xe8\xd1OR\xf6\xed\xb1\x0c4\xaa[\x10\x9c\xce\xb8\xdf\xf9\x1bl\xaa\xec\xf5\xca\xd3\x1d\xd4\xe2h\xcb\xd9\xc3\x0b\xcb\x00\x86\xd7\xc4N\x8d>\xbc\x11x7\xc0\x8d\xabo\xe7o4g \x0c1F\xd5g\x05\xfdf\xe8\xc4$H\xf7\x7fK\xb5\xe5\xdc\xb9\xf8x\xcf\x1a\xad\xa7j\xb1\xe4SZIH\xe8\xe0\xdf\xe9fz\x997\xa8\x87\xa5\xd7\xafbQ\x15k0W\xa3|\xd7\xa7B\r\xc3\xe4\x17\xb7\xa8\xfbQ\xc2\x13|\x05H\xc8\xc7\x92i\xaf\xba\x87\x8bG\xca\x8fM\xb7\x8e\xa9{\x8eq\x0c\x8d\x9b",
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
