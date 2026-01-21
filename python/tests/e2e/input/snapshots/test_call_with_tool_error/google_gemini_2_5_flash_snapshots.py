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
                "input_tokens": 138,
                "output_tokens": 6,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=6 candidates_tokens_details=None prompt_token_count=138 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=138
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=144 traffic_type=None\
""",
                "total_tokens": 144,
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
                            name="test_tool",
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
                                    "name": "test_tool",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xb9\x01\x01r\xc8\xda|\x1fx\xed\xf8PX\xa23z\xd9W\xbdld\xbf\xa4\x03\xe2\\,\xc4*oI< \xd3\x8b\xab\n\xb9\xee\xd9\xf4\xae\x1e\xe3\xa8B\x7f\xb5\xc3\xd7Si\xe2?\xbcE\x04^\xc1\xab\xa1\xa2P\x15\xc6O*v\xfd\xd9\x13s\xaeS\x11\x16\xd9\x96\x9cM0O*dm[\xfc\xb9<\xe1\x89\x0b\x14T\x05n\x03X\x8e\xff\t\x08\x912\xe3\xad\xb6k\x1a\xf5\xdea[\xec<\xca\x88\xed\x05\xc6M\xb9)\x83\x8e\xd7\x9d\xb4mj:\xe8\xac\x82\xa6e\x8c\x95M\x9e<6\x8fJ\xc6j\xb2bb\xd6o\x99i9\xbfG\x1c\xb0\xa0B\t\xbf$\x18$\x8dc\x88u.\xf6\xfb\x0c\xf7\xb3e\x8aw\xdcS362\xf9\xbe\x0b\xf4",
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
                            name="test_tool",
                            result="Incorrect passhrase: The correct passphrase is 'cake'",
                            error=ToolExecutionError(
                                "Incorrect passhrase: The correct passphrase is 'cake'"
                            ),
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="test_tool",
                            args='{"passphrase": "cake"}',
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
                                    "args": {"passphrase": "cake"},
                                    "name": "test_tool",
                                    "partial_args": None,
                                    "will_continue": None,
                                },
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xb2\x02\x01r\xc8\xda|\x01`\xc3\x97&\xd6\x91]\xb5\x82\x9f\x83\xcb\xba\xa2\x11\xb4v^\xf2\xda\x90\x8eaW@u\xc3\xbe\xea-\xb7\xc1\x0b\x1a\xa2\x80\x03CP?>\x94C\xcb7\xd2\xa8\xc0\xd1;s\x0e\xec\x8e\xb6q\xde\xdcs\xdcL\xc1y\x96;\x9b\x1cK9n\xbf\xe1\x97\xf6\x8ac\x89O\x01\xfc\x8e\xed\xb0\xe5Q\xe3\x17n\xde |\xd5\xfa\x97\xb8\x90}\x8c\xfdv\xbe\x8f\x9f\xf8\x9aAO\xef\x8dk\xc3m\x18\x8d\xb6\x82\xf1\xc0\xa7\x17\x0eu\x19\x81=\xb6A\x97\xf9\xa5X`\xe6\xa2\xf9Vb\xbf]V\x1b\x7fK\xef\xfe\xb7\xd2\xeb\xc8=@Kbl\t\xed\x035Xy\x8e;i\xa9}\xe7\xbb\xbc&\xf2k\xcbK-\xe4\xf0'\x95\xa7\xa1\xca\x8c\xed\x9a\xbc\x87S\xe4\xf1\x8bx{5\xaa]\x9b\xc0:@YG\x0e2\xe2\xca\xaf\x8f\xac\xe1j\xa6l\x1f\x8e\x947\x05\xfa\x03\xfc \xe0\xfa\xbfh\x83\x95O\xb5\xdd\xc5ji3\xc4\xc3\xc4\xcf\xdf\xc0f\xf2H\x1b\x07V\xd2A\xd7\x8d\x82\xe7x\xc8RS\xfa\xf9O\xa7\x03\xc1\xb1\xe8\xd2\xa2\xa0\xaf\x15/\x16e\x8d\x89\x06\xa1[\xeeD\xc7\xf0\xc2\xe0\xc4\xcc\x1d\xc4\xbd}<\x03\x17W\xe5\xe5\xa6\x87\xf1\xbc5",
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
                            name="test_tool",
                            result="The cake is a lie.",
                        )
                    ]
                ),
                AssistantMessage(
                    content=[Text(text="The cake is a lie.")],
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
                                "text": "The cake is a lie.",
                                "thought": None,
                                "thought_signature": None,
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
                    "name": "test_tool",
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
                    name="test_tool",
                    result="Incorrect passhrase: The correct passphrase is 'cake'",
                    error=ToolExecutionError(
                        "Incorrect passhrase: The correct passphrase is 'cake'"
                    ),
                )
            ],
            [
                ToolOutput(
                    id="google_unknown_tool_id",
                    name="test_tool",
                    result="The cake is a lie.",
                )
            ],
        ],
    }
)
