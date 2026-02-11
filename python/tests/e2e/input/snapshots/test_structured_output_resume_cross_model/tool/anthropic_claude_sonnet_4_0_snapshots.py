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
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 430,
                "output_tokens": 24,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=430, output_tokens=24, server_tool_use=None, service_tier='standard', inference_geo='not_available')",
                "total_tokens": 454,
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
                                "thought_signature": b'\n\x83\x02\x01\xbe>\xf6\xfbG\\\xaf\xccK@\x07\xc1l\x13J\xa9\xa8\x1bdF\xab|)\xd1\xa3\xfb,\xea\xb9H\xe0\xdf\xdd\x0cyX[\x89\xf7V\x9d\x19\x9a\xeaJ\x8eg\xaa/\x8a+\xc2>\xfa\x15\x8e\xc00\x10\x9fB-\xbfXT\xb7\x96\xd3\x8d\xf4\xcfk\xa1\x91\xa2`\xe7\x8c35N\xb7q6\xda\xd0\x13\xa3\xadD"\x80\xef\x0e(\x11\xe6]({\x8c\x03|\x93\xf7~\xdbW\x945\x88h.\xef\x8e\x04y\xd3\xdcb\x8d\xf5\xfaw,\x87\xd57I\xe6\xb5\rt\x06^m\x88\x1d\x18\xba\xb8|\x1e\x12\xd9N\xa4eY3QA\xcac\xc5R\xa0\xe0\xa0\xf2a\xcfY\xea(D\xf4\xae\xac.\xa7f\xf8\x19\xcf[{G\x8c^\x1cb\xee\x14\xfa\x02\x82\xf1\xdc\xc7\x00 \xce\x00\xea{\x1a\xd3\xad\xe50\xed\x1f\xab4L,M\xf5\xf595\x89Y\x08CH\xd8`\xd0x\x8f\xb2Gz\xc1\x0ff\x9e]\x9a\xe8\xc61:\xfdD\x1e\xa0\xce\x0bR^n`!\xf4;x>,3\x83H\x0fP\x04\x8e',
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
                    content=[Text(text='{"output": 3}')],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_01XGzGyV59pDYFHoAMhysntR",
                                "input": {"output": 3},
                                "name": "__mirascope_formatted_output_tool__",
                                "type": "tool_use",
                            }
                        ],
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
