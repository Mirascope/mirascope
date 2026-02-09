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
            "model_id": "anthropic-beta/claude-sonnet-4-0",
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
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=430, output_tokens=24, server_tool_use=None, service_tier='standard', inference_geo='not_available')",
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
                                "thought_signature": b'\n\xf3\x06\x01\xbe>\xf6\xfbB\x96\'O\xc4\xc7<\xf4\x9e\xa7\xd4\xdf\x01\xcb\xf4\x93\xb15\xa242\x9c\xd6\x981g@\xf3Z\xc3\x85\x1eP\x89\n\xcd\xc8mex\x92p\xf9c\xba\xdd\xaa\xf5\xae\xf2\x93i\xfd`\xd0\xced\x94\x9b\x9f>\x99=\xb7\xc4\x9c,\xf1\x92\xf4v\x98n\xa6\xc4\x92\xfcZ4\xb4\xb1z\xf0\xeb^\xdd\x04\x80\x02\x17\xbf/&\\\xeeL]z\x03\x9c\xb1\xa3\x9c)2\x13\n\xfe\x03\xec\xd9\xbf\x9f\x1aw{_\xdb\xc8\x0e\xef8\xc5\xaf\xec\xbe\xe3\nI0Pw\x01\xf5Tb\xc6\xb5W5DX\xdei\x19c\x05\xae\x81\xe4\x90\x94\x90\xfd\xdc\xe7\xd48\xc9\x9f\xbcb\xf9\x7f\xcc\xd1\xa7\x94\x80\xfbe\x1e_S\x985\x9bW\n4%\xcd\xb3V\\\xda/\xe0\x92\t\xb9\xaa\x81\xdb\xc0z\x98vF\xd0\\Dhs\x9b\x9d8\x9b\x01\x9eSz\xd0\x11I\x01d\x83\x95w\xc8\x02M\xfb\x93\x91\xf9\x15g"\\\xb3\xf9e\xfe\xb0s\x08\x83f\xbb\x11\xee\x98\xa5\xcbj\x8e\x7f\xb0,\xa8[\x03\xa5\xc4+\xbf"\xf1Xo7*\x8f\x0e\x0e\xe5\xcb\xcd\x03\xd6\xa1\xa7.\x16\x85\xe85\xe6\x1d\xc2\xb8\xeeu\xfb\x03\xf7\xaba\xb6\x078\x19`\x8c\xa7\xca\xfao>c\x81kU\xe7\xcb\xe9gN\xe7}CV\x88\x14c\xd2\xc2J\xd8\x12\x0c\x1e\xcc\x98Nr\x12\xba\x95\xba\xcc\xcfL \xf1&\xf8t\x11ApB\x1d\x112\x7f.\xda&I9\x16\x86\xfd\xca\xbcTI\x00\xb0$\x96\rZ\xda\x83E\xca\t}\xc3\xc1\xdcU\x02\xc7\xa0\xd6d\xc7A\xf8\xd0E8p\xe7:\x81j\x88\xce\xc8X:\xeaa\xb9\x1e\x88\x9d\'\x8cE\xd6\xeb\xd6`\xaa\xb3\x02e{\xc8\n\x04\xdeh\xaf\xbav\x96\xcf"\xdb\xa4\x988\xee\x07uf\x82\xda\x83\xb3\x9a\xdd\xa6\xf8\xcf\xe3\x82\xf5\xce\x0f=\xca4(\xd8\xfam\xd5S\xfd,\xf7\xc0\x04\x0f\n\xf43f\x80\xc9\xd4\xe1\xca\x86-\xc9\x98\x03M\xc40\x91\x15\x99%b\xff\x9e\xd1\xf4\x91Q\xd3<\xdaUw\xcc`\xc2\x8b\x19\xa1\x8dc\x0bq\xdd\x1b\xca\xd7&\x03\xe5\xb9\x14\xd0h\xbdW^\xae{\xf5\xd3\x05L\xea\xd6\xe9\xa4\x98\x1bt\xeb\xe8\xe7)\xdc\xe4^4Q\xd1\xa0\x9bc\x98\xb0\x0cL\xa9\xedH37$8\xe5\t\x02Nd\xa5i\x82L9\x82TR@|\xbd\xd5W\xb0[9\x1a\xd7\x9fr:`\xdf\x1e\xb4\x97\x97l\xd8\xf7%\xb2(\xadH/\xacc\xaa\r\xc1\xe3.\xf1\x18q\xe57\x9eL \xf4|@wJqU\x17\xf3\xb2\xd3]\x98\xbf\x88\x99l"X\xbb\xd3\x00"$\xedh\xf7\xcd\x0f\xe0\xeb\xbas\xe0\x8e<<\xb3YkA&\xf3{|Q\xe1\xb9\xa2=\xc2\xc4\xeb\x95\xd11\xe9N\xbc\xddPf\xe2\xf4$\x05\x98\x07#*\xa2\xf4\xcfQ\x98\x97NK\xa1u\x92T \xdb\xf9\x02\xebl\x90\xd9\xc7\xf9\x97D\xd3M[\xda\x9eB\xefxA\xcb\xe1\x02\r\x1e\xd8\xea\xfd\x04\x8c\xeb\xb8.#l_\x8e\xf1\x01P\xe9\xfaub\xa2\xfaOH}\xd9`\xd6a\x88\x8e\ta{\x8c\xa3A\xe9\x1flar\xcbTK\xe0\xddh\xac\xa3\xcc\xc3\xcd\xc4\xfex\xd5$\xebS\x8c\x16\x83DW\x1b\xc3,_\xdfx\xa6\x0eP7%.\xef\x17\xba\xfe\x00Q?\xa5V\xca\x19\x18L\xb2\xb0\xf6\xa8/Tt\xb8\x06M\xa1\x96LR\xbb\xcb\xd5\xf0\x8b\xc3\xae\xb1\xe6\xa5\xf3\xf6xQ.\x99R\xc1o%\xb8\n\x9cs5\xe0\x92\xc2\x81I\xb9z\x8f\x8a3\xe9\xc0\xe9\x84\xa5u\xb3\xb4\xbd\x98\x1d\xc5\xc1\x96\x87\xd1\x18\xf5w',
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
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_01DVnZ7iKhfsdyYcZL3EzndE",
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
