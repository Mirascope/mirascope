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
            "model_id": "anthropic/claude-sonnet-4-5",
            "provider_model_name": "claude-sonnet-4-5",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 747,
                "output_tokens": 24,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=747, output_tokens=24, server_tool_use=None, service_tier='standard', inference_geo='not_available')",
                "total_tokens": 771,
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
                                "thought_signature": b"\n\x90\x04\x01\xbe>\xf6\xfb\x93\xb2mGkmEK\x94\x0f\xeeG2\xedf\x9d\x9d\xfa|\xaa\xba\xd6\x17\xca\x0e\xc8\xe4\xbcR\xf9`\x88\xe9u\xdc'\xaf\xef\x17\xf8j\x9cF.\xc5\x0b\x06\x99\x9f\xf4^?\xd2~<\xd5\xd0\x80\x0f\xd2\x17\xcf\xb0v\xf3\xcfl\xdc\xc1\xb6\xfb\xa7T\xa1\xd5\xbe2\x17\xbd\xbb\xc6/\xd8\xe8\xbcQO\x10\xcd\xda\xbc\x14\xcb\xdb\x93s\xf7\xc8)\xfa+\x93FMV\x01AU\x91\x8e<df\x82\xbf\x89\xe7E8g\x15\x17\x86\xa4\x865\x92\xa6\xe1\xee\x90\xa7qm\xdc\x14\x08\x8d\xe3X%\xca\xac-\xdb0H\x86e\xe9\x84\x1dyA\x02\x84\xce\x91\xcd\xa3\xa1\x06\xecH\x08_\xae\x9c\xf0\xca\xa2L\x0f\xbf\xbd\xbcqz\xe39\xfb\xa3\xaf\xed\x9e\x06\xca+\x0f\x82\x1c\xe4\xa6\xc5\x04\x18\x19\xdc\xc8[1\x11\xcf_\x8d>\xee}\x7f\xf7\x8a\xc8\x9f\x99\xdf\xcd&\x93\x8d\x866\xf8\xaal\x08\xf3 \x1fl\xb4J\xffW;\x0c,y3Pqk \xf4_\xfe\x99\xc3\xa8',\xe4\x933\xf2\x7fD\xf6\xdf?\x01\xc2\xa1/2_\xa0'\xf4*\xcb\xf4\xc9\xc0\x17e\x05+O\xc0P\xd6\x077\xcf\xf9\xce\x92\xee\xb6\xb0q\x19)q\x93\xb2\xbc\x07\x9f\xb3\xdbB\x11\xa2\xf4\xb1\xf8M,\x01\xa1Zl\xbfC\xfb\xc8.\x16h\x8c0n^a|XX`wU\x84\x12uF\x9f\x8d\xad\x10\t\xcd\xc9\x1c\x95\xed\xbaMA\x91\x02-\x01)\xd4\xc9\xd2\n\xdd}I2\x988U\xc3\xcdc\x12\x0bE\xfd!\x00<I\x13\x10\xb2\xf9\xfa%\x0f9w'\x82F\xee\xdc\x96\xbfjN\x89a\xdf\xba\xf3.\x15*4\xff\x1e\xb6\x05(\x84N\xf6UC4\xa5\x02\x1c!@\xb0\xe3\x82\x88\xd59\x1e\x803%\xea\xe0\xe3P\x8ac\xccC\x8c\r<\xfb+\xb0x\x8f.\x0fC\xae\xf01\x87Kv\"=p\xd4\xf2;\xfd\xce\xef^&\xc4dN*\x8c\xc4E\xfdUu\xa2%\xd1\xc7\x83\x9a\x9a\x95zr#\xeb%\xde4\xbf\x99{'\xae\xc0\r\xf4\xb8a\x1f\x80\xb8\x9b\x812\xbb\x9cO\x12\x05-$B\xaa\xd2\xa6\xe0\xe7\xa9z\xe4\x86b",
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
                    model_id="anthropic/claude-sonnet-4-5",
                    provider_model_name="claude-sonnet-4-5",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_01Q5iVZrZUpc9mW4Bj1EoDQ9",
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
