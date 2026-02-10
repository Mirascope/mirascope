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
            "provider_id": "openai",
            "model_id": "openai/gpt-4o:responses",
            "provider_model_name": "gpt-4o:responses",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 129,
                "output_tokens": 6,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "ResponseUsage(input_tokens=129, input_tokens_details=InputTokensDetails(cached_tokens=0), output_tokens=6, output_tokens_details=OutputTokensDetails(reasoning_tokens=0), total_tokens=135)",
                "total_tokens": 135,
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
                                    "args": {"output": 7},
                                    "name": "__mirascope_formatted_output_tool__",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xf6\x02\x01\xbe>\xf6\xfb\x9b\x11\xf2\\Z\xea\xf0N\x8b\x7f\xfa\x1dT\xe9\xe8K\x91h\x7fz\xa4\xdf\x1a\x8b\x9a\'Y\x88\x12_F\x0e\x862|\x1aC\xe1\xb1\x957\xf9\xea&\xc6\xf4"Q([\x815\xb2\x01\xf7\x98\x8c!\x9c\xa5\xecm\n\xbc\x03\xeb\xc7o_\xa4C\xa2M1j1H\xd8`\rqn\x15\xa7-g\x7f\xe2&3\xfcC\x861\xcb9S\x97\xbaI\x8eyT5\xcfi\x90\xff\xfc\xf8\xa3\xd8\xd4\xe2x\x1b\xc4\xf3\x95\x01\xcc\xc7\x85\xd0\r\xe2M\x97A_\x9c\xd2\xf4\x88ba\x8c\xa8\x1c\x1bm\x9d\x0c|raL\x8f[\xa7\xbc\xb3\xa2\x8d\xc9\xd4\xf5P=\x9e9=\x91\xd0\xb9\xf0Gg*\x13\xb4\x16\x0c:\xcfK5\xc0k\x1d\xeeY_\xc3\xa2\r\xe2m\xbe\x03w\xf2+\xf4o\x9dM\xad\xf6\xd5\x98\xf7\xf5\x1f\x9bKCh\xd3\x1a7\x95\x03\xac2\x04L\x1e>\xf2\xa2\xa8\x00\xea3\xc3:\xc3\xe1\x10\xe3f\x9d3\x0c\xab\xc3i\xa5\xa8\xcb\x8c\xbe?\x98\xa7\x95\xb4\x14n\xfdB+\xbd$J\x89\twQ[\xee\xbd\xca\xc4\x8eq\\\xef}\xa6\xf4\xad\x9c\xb3\x01\x1e\xf6\xa3Lk{\xf8\x1b\xf9u\xda\xaa2\x95\xd5<\x02o\xb8\xd4q==\xd6\x02\xc4X\xd0[\x1c=u\xf1\xa4\xeb/\xc1!c\x10=f"\x13#\x06u\xa5Rh>U\xa8\nX\x92\xf1@o\x15w\xf4\x91\xd4\xd37Oc\xd8\x85\xe0C\xd2\\\x80\x1c\x15\x1e#\xf6\x92\x93I\x14\x1e3\xa9\xd2\x02\xdd\ty\x01',
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[Text(text="Ok, now choose a different lucky number")]
                ),
                AssistantMessage(
                    content=[Text(text='{"output":5}')],
                    provider_id="openai",
                    model_id="openai/gpt-4o:responses",
                    provider_model_name="gpt-4o:responses",
                    raw_message=[
                        {
                            "arguments": '{"output":5}',
                            "call_id": "call_hVQCUiG7yTzzQmdvwlZlVDQH",
                            "name": "__mirascope_formatted_output_tool__",
                            "type": "function_call",
                            "id": "fc_0e614ada6ffe0e2b00698a5b416c7c81908a5e37f13d07ab2d",
                            "status": "completed",
                        }
                    ],
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
