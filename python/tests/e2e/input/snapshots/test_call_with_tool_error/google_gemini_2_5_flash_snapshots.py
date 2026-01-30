from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    Text,
    ToolCall,
    ToolExecutionError,
    ToolOutput,
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
                "input_tokens": 114,
                "output_tokens": 84,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 69,
                "provider_tool_usage": None,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=15 candidates_tokens_details=None prompt_token_count=114 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=114
)] thoughts_token_count=69 tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=198 traffic_type=None\
""",
                "total_tokens": 198,
            },
            "messages": [
                UserMessage(
                    content=[
                        Text(
                            text="Use the test tool to retrieve the secret phrase. The passphrase is 'portal"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="passphrase_test_tool",
                            args='{"passphrase": "portal"}',
                        )
                    ],
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
                                    "args": {"passphrase": "portal"},
                                    "name": "passphrase_test_tool",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xf0\x01\x01r\xc8\xda|\xba{\x01\x17e\xc9I\xfa\x11O\x92\xce4*\xf7\xc1\xb1\r\x8aKs\x01;\xc6\x13\xf5\xf1\x7f\x1f\xb5\x1d\xd4\x0bo\xd4<>?y\xe6\xe5\xc8\t\xee\x87\x8a,\xc4I\xc0\x9bp\xe1\xd8Y\xa9#\x8ft\x0b\xb1#\xb9OO\xc7\xf8GB\x02\x82\xff\xcaa\xbe\xf1\xbf\x0b\xc3<\xa5\x99\x1a\xfc\x8b\xf8f\xa3m\x16\xea{C`\xc1\x8c\xedt\x85\xa2\xb2\xfb5\t\x7f\x9b\x15\xad\xeeM\xf0<\x9eE9\x8chb\x12\x15\xc5U\x93\xc4\x82B@\xd4g\xba\x1b\xe5Zkw\xd5\xba\xef\xfb\xd2t<\x9d\xadX\xdd\xc8\x15\x15Hh9\t\xb5O\xcb\xad\xc0T\x05\xd3\xb9\x0c:\x16L\xb7\x99<&j\x84\xc6\x11\x99gDRr\x89"\xce\xbe\x195\xd4\x1a\x16%ae\xae\xb3ET\xdc(\x8d\x7f\xa5+\xe1\x93\xfd\xdc\xdd\xb0\xca\xfc3\x86\xdd\x83\xf1D5\xa9"\xa6n\xf7\r.\xdd\x97\xc9\x01-\xc6\x9eM\xd1\x07\x9dz',
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="passphrase_test_tool",
                            result="Incorrect passhrase: The correct passphrase is 'cake'. Try again.",
                            error=ToolExecutionError(
                                "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
                            ),
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="The passphrase 'portal' is incorrect. The correct passphrase is 'cake'."
                        )
                    ],
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
                                "text": "The passphrase 'portal' is incorrect. The correct passphrase is 'cake'.",
                                "thought": None,
                                "thought_signature": b"\n\xf0\x02\x01r\xc8\xda|5\x8c\xef\xab=\xcb\xf3\xf3\x12\xa9Sg\x83r\xdd2\x91Lq)$7\x1aD\xec0\x10p\x984\xe5\xfa\x8f\x7f\xcdR.\x08\x11\xe4a\xe4\x17g_\xc2\xe4\xb6$\x9cw\x9a\xec\xbez\x8c\xdf\x19\xf4\xfe\xd0k\xff\x8bK\xfc\x89@\xcdT\x19/\x07\x8f\xb5!9\xc6`\xe5j\xef)\xc1\xd3i\xb5\xe1\xa0_ \xaa\xe84\\\x0c\x12d\x8eHE\x1e&\xe4\xad*W\xe7\xecZ\xc9\xaf\x1d\xa1t\x99\r\x18\xc4\xb33\xda\x00|p\\1\xce\x83\x10L\xf6\x83\x10[e^\x9d\x92\xc8\x06\xb8l\x14C-[\xb0\x90\xe4 WK\xf1\xb4\xc6\xdd\xf5\xce\x10\x88\xc9x:\x9c\xc9!I\xdbM\x94\xd67\xaf\xde\xd0\xc7\xd6\xb8\x8b\xa7\x7f\xab\x183\xa5T\x84\xf9p\x8e\x9fD\x82\xf2\xe8\x1c\xdfsr\xd07\x8c\xc5 l9(\xd3NN\x88y*\xbdC\x9c\xa5\xbf~\x18\xd6\x16\xf8\x80\x05\xa6\x87\x7fU\x12\x96\xcb'v\xa9\xd6\xd4\t^HP\x88\x1c\x17\x88\xe7t\x11\xbe\x1f\\o\xf8\xf3)1\xefU\xe1\xc35\xf9i(\x8f\x96\x8b!\xaeap7\x13\x8f\xa1t\x0c\xb3\xf9\xb9\x17)\x16\xd3\xb8\xab\xcec2V?\x9e\xaavA\x90\xdd\xacy\xbe\x81\xc1{\xd5B|\x1b\x7f\x16\x85%\xc9\x8fY(\xea\x80_\x16\n*\x9a\x18\xea\xa4\xd7$\x04\t\x01<d[!n\x9d\x1d\xd8\x18$\x80F\xa8\xf4\xbbLv=qPI\xbb\xdd\x8e\x8c\x91\x95\x1aW\xb8\xa49",
                                "video_metadata": None,
                            }
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "passphrase_test_tool",
                    "description": "A tool that must be called with a passphrase.",
                    "parameters": """\
{
  "properties": {
    "passphrase": {
      "title": "Passphrase",
      "type": "string"
    }
  },
  "required": [
    "passphrase"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": None,
                }
            ],
        },
        "tool_outputs": [
            [
                ToolOutput(
                    id="google_unknown_tool_id",
                    name="passphrase_test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'. Try again.",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'. Try again."
                    ),
                )
            ]
        ],
    }
)
