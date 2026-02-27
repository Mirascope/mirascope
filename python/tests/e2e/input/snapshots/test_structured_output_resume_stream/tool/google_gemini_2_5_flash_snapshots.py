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
            "finish_reason": None,
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
                                "thought_signature": b'\n$\x01\xbe>\xf6\xfb\x0e\x10\xef\x80\x88\xe7p\x18N\x82\xf7\xf3K\x84\xfe[ah,\xea\xd9\xab%\xcd\x955`\xdb\xfb\xa7]\nZ\x01\xbe>\xf6\xfb*NTy\x1d\x13\xa0afJ\x0f\xbeI\xba`*\x15\x16h\xc3\x04\xb1\x98P\x18\x96\xa5\xee[Y\x89}K\xaf\xfb\x05\xca\xf6\xc4\x16Of\xae\xa3\xf5l\x82}p\xae\xea\x99H\x15~\xb1\xd6zo\xf9\xc8\xf8\xfb&2\x15\xd42(\x85>{^\x88\x06e&\xf3\x85\x02`\xc3\xc6\xfe`\n\xf6\x01\x01\xbe>\xf6\xfbWL\x0e\x1b\x8c\x8b`\\\xe8\xe4\xf9\nAVz+\xac\x8d\xb5V\x07EY\xd3\xb1@\x84,:\xd5\xb9\x97I\x143\xf2\x890\x9bf\xca\xe6k%-q<I\xa5\xe3\xe0\xb0.\xc74\x89Co\x8e-N\x9c\xaas\xader\xb5\x82\xb4D\xae,\xae9\xb3\x8a\xd4\x08\x0c0d"\xd2r\t\xe6o\x1f\xba\x11h\x0eM.-\x15\x9f\x87\x7f\r\xdakJ{\x99\xf5\xa4 8\x0ed\xf9\xc35rO\x8b\x93\x8e\xfa0\x93x2\x9d<{l\xb3\x1c\xfe\x8e\x1aor+\xf1\xe7\x96\xb6\xea=\xf1O\xd7\xb5H}\x87\x7f-=6\xeb\nY\x89\xe9\xfc\xec\xd2\xdaE\xe9Nqs\xca\x83V\xf4\x882\xb8\xc1\xa7\x9c\x03,?\xe4\x86N\xdf\xfe1d\xd4\xe6\x8fF\x8c*\x9c\xbd\xb9\x8e\'\xdb\x80D\x0f\x05\xa0\xcf>B\xc7\xef#\xcc\xe6X\xed\x99\xb798z\x05Q:\x99,"\rM\xed\xc2:\x15hN\x96\xc0\xc2\r\x82\xf9\xff\nF\x01\xbe>\xf6\xfb%\xe6\x08\xd2\xec\xda\xa5L\x1b\x99N\x88\xa8TPw\x0b\xd7L\xe9\t7\x93\xe6V\xd5\xc8\x94{g\x82\xfcS2\xc2\xb4\r\xf8hD\xf1g\xe4g\xdb\xe5h\n\xfd\xc7f7\xd8\x84\xc2v\x85\x9eNMn$\x84\t\xae',
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
                                "thought_signature": b'\n$\x01\xbe>\xf6\xfb\xd3,\xdc\xefGF\xcd\x169e\x87\xb0Y\x8c"\xa8\xf4\xc7J\xa8\xe9X\xe6\x0b8c\x85\x10\xc0y\x99\np\x01\xbe>\xf6\xfb@~\x05,\xf3SW\xa7<\xd4\xf0@Y\xf9fN\x0foqB\x11`\x9f\x0f[,8\xd6g$\\P\xc2\x1a\x18Qf>.\x8c \t\xcf\x1cI1?\x0f\xa3\xe8\xa8\x9b\x067\xce\x82\x994\xd6\x13\x80\xdf1\xdc\x1d\xbc\x815\xac\xc3\xe9\xee\xba\xbeW\xd8C3\xf7;\x05\x12\x81\x01\xa7\xa8\x9cL|k\x89\x07s\xb8u\xef\x93\xf9\x16\xfc\xb66=\xd7\xac|l\n\xc5\x01\x01\xbe>\xf6\xfb\xc0X\x92\xd8\x0f\xfe\xe8\xf2\xb5\xdb\xb3\\\xd4\xf6\x1b\x13\x08b8G\x16\xb38\xfbA-\x01\x94\xa2!]\x07\xe4\xb3\x8b\xd8w<\x81//\xefr&kr+\x1d\x17\xf1T\xdc\xc9\x94\xad\xf8\xd5\xe7V\xcc\xa5\x9c\x98\xb7\xc7\xd2\x07\xb8@Ci\xc0\xea\xf3f\xf2\xf7\x98[G\x91\x16\xb9U\xde?\xc7\xfb\xa1\x19Y\n\n\x13\xe8\x0b\xf7#D\x0c5\xeb\xb0\x0e(Y\xff\xe3\xdb\xb7\x8bZ\xa4\xc3\xa7\xb8vS\x93\x90\x0f\x9b~+\x00\xfc\xf0\xfc3\xa2\x1f\x99\x1a\x92\xaf\xd3:WOi\x1dDQ\xac\xceh\xd3\xd2\xc3\xee\x19\xff|\xe0W\xccd\x9d\x8d\x15:\x16gV\xf3\n\x08\xa8\nP\xd94sw\x8d}N<\x89\x1bx\xb5P\xc41!7\x98\x80\x88B\x9b\n?\x01\xbe>\xf6\xfb\x86\xb7\xc2\xf4\xec\xde\x025\xfdL\xe8vFLt\x88l \x12\x1e\x9b\x90\x0f*\x8c\x03\xee@\x11\xb7\xa2P\x11\xd3\tFM\xc8vq~\x1c\xfb\x1d\xc2\xb3\x83 A\xa3\x97S\xa45\x99\xa3$\x0e',
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
            "usage": {
                "input_tokens": 108,
                "output_tokens": 21,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 75,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 129,
            },
            "n_chunks": 3,
        }
    }
)
