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
                                "thought_signature": b"\n\x88\x03\x01\xbe>\xf6\xfb\x92G\x12vjp\x00\xf6Mu\x9a?\xac\xb4zu\xb8\xf9@H\x9f+\xf2\r\xaa\xaciP\xd8>\x86\xf1\xe5\xd1\x8e1I1+\x1a\x91\xc48o\x83\xcc\n \xafL\x9c\x00\xf1h\x00&h\xe5\xa0\xe5\xe9+\x08\x18V\xca\xf0\t?\xc4\xed\xbd\x8cSL\xc1\x077\xbd\x15\xc4L\xca\x83{a\xee\xf4N\xf8\xf3\x16-!\xce\xd1\xda\x83\x04\xa1\xac:\xdb\x13-S\xe6\x17\t\n\xa7'y\x94\xaf\x06\x08\xb8&\x04\xe6\x16\x8c\xae\xefHobI:\xa6\xa6\xe0\xc2\x1d\xcd\xa6\xe6En\xfc\x05\xad4)mG\x93\xf3\xf9\xcd\xde\x17\x9e\x02\xf5?(\xa8e7\x88\xc3\xb5\xda\xeck\x8e\x0b\x8er`\x85\x8e\xd9\x0c\xca\x9b\x8f\xfb\\\xa7\x9a,b\x19\x83\x83Y\x16\xb2\x10WU\xad\x99\x8b\xbez\xb2\xc8\x19\x9e\xeaY\x88JBWZ\x98\xd61\xf1\xd5h_\xa7\xf2\xb7\x88\xafhk\xcdz5\x8d\x93\xde\xc6\xed\x07\"\xea\xce!\xdcd\x8c\rX\x1e\xfei7\x0e\x1d\x93Ze\x11\xa9<\xaf\x8b\xbcS^\xe4\x9b\xb4}Q\x92\xe1\x83\xa5\x0b;7\xdaHz\xcf\x0ess\xe3B\x87\xde4\xe8\x95m\xd1\x99\xe7\xff\x10k6\x90\x11\xc0R%c\r\x96\xaf|T/m\x81\xef\x8f\xad\x9a\xef\xc2\xa1LUN\xc7R\xf9\xfc\xf4\xffj\xb8\x83g\x15\x17@\x9c\x12,\xc8'\x1bcs\xa7O\xe0>\x136\xcf\x00\x9f;20\xb3\xe4\x14\x92\xa9>S\xb4[\x845\xe6*b\x17U\xbde\x96\xe9G_(\x9b\xcb\xe8h%\xd0z\x8a\xb4\xbe\xdd\x084\xea",
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
                                "thought_signature": b'\n\xd6\x01\x01\xbe>\xf6\xfb\xf2\xb3.\xc0\xf4\xe4\xeb=\x9cd\x88\x9b,]E\xe8\xc8\xeb\xfd;\xb5\xbc\xa8\xe7\x91\xc0\x87;\xc6\xec\x1e\x90\x81\xed\x83q+\x9e\xdb\xf6X\x9d\xc3\x92\xec\xb9i\xeb\xac\x9d\xb3f\x01\x9e\xc8\xf4\x8f\x9f\xeeJ\x85#\x11RO\xd4U%z\x91\t\xaa{I#\xac\xec\xd0\xbch\x84\x03R\xc50?\x9f\xde\xda"\x1bP\xf9\xebo\xcbV$\xe2\xf9\xf39\xe8\xd3\x1bR\xfe\xcba;\x0e\x95|S\x939b\t\xab\xf7;\xc3/`7=^\xca\xc5\x1b`U\xc5\xeb\xe5\x15\xa4\xfbb\x86\xdd &D\xeb\x02\xc9\xa4\xfdg\xf80b\x8e\xc0Z\x91Hb\x8d\x10\xde\x98\xa1\x8b\xcc\xe6\x90\x90\xa4T\xc3\xe3\xe1\x9a\x18i\x86\x91\xf1x\xd5\x8a\xe5w\x86\x9etO\xae\xe5L\xa4\xf4\xd7B\xee\xdb\x15~\xcf\x16\x1bR:w\x85^\xff',
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
