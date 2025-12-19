from inline_snapshot import snapshot

from mirascope.llm import (
    AssistantMessage,
    SystemMessage,
    Text,
    ToolCall,
    ToolOutput,
    UserMessage,
)

sync_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 152,
                "output_tokens": 37,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=37 candidates_tokens_details=None prompt_token_count=152 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=152
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=189 traffic_type=None\
""",
                "total_tokens": 189,
            },
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "mellon"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n\xd2\x02\x01\xd1\xed\x8aoA\x8b!k%4|\xc06;\xff&\xb8\xce\xf3t\x13\xb7\xff4 \xc1\x98\x97A \xfax_\xc1\xa5\x84@C\xd5\xa6\x0b?\x04\xd0\xc8N\x96^\xa0\xce\xc7\x01\xd4%\xa4\xde\xe0\x9f-\n\xbf\x82n\xe4\xa4\x9e\x7f\x1a\xe2\xbcs\xe4\xca\x9cT\x9e\x86n\xb3\xdc~\x91\xadh5\xe6\x1e\xe4u\xa3]\t;\x94\x17\x86m,~\xe7\x0b\xf8c4\x8dx\x00\x80\xa9\xee\xde~\xe1\xbc$!\rd\xa6XSw7{1r\xb9\xe3s\x05g0\xa7\xb7i\xa6\xb8\xf0{\xcb\xda\t\xa7IO\xf7/\x1d\xa2\x86\xa3\xf7\x10\xa3b\x94\xc7\xae\x13S]^?\x7f~D\xc8\xba-\x9f\xfd\xb9\x94\xe2\xae\x8a6\x02\xe2\xbe\x111\toP\xd8\xc6\xa2`\x0en\xa8\xdf\xb8\xf4+P$\x03UV\x02\x18\x13\x0b\x8f\t>|.\x87\tCn\x81\xfa\x8bo\xe3\xa5\xff\x9e\xb9p\xd7\xb0\x16\nx\x8a \\\x14\x8b\x83\xde\xea_^%U\xb2\xe0\xc8W\xa4\xf6\xc3n\xd6O\xb4\x16\x8c\xb1\xd6\xdaAT\x91\x10w8\x93B\xcf\xf6\x80\xd4<IC\x8eD\xe8)\x8f\xcf%\x13\xa1C3\xa7\xa2\xe0\xcc\x19\x98;nxJ\xa4\x18h+\xf9\xbe`\x8a\x04,\xc0\xbf&\xdfa\xbcK\xdf\xc6\xf1D\xb5\xd5\xaa\xe8N\xc4o\xe1\xd4\xf3\xefW\xd8y\xe1t\x0ez\x02\xb4\xce\xc6W",
                                "video_metadata": None,
                            },
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "radiance"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='The secrets have been retrieved. For the password "mellon", the secret is "Welcome to Moria!". For the password "radiance", the secret is "Life before Death".'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": 'The secrets have been retrieved. For the password "mellon", the secret is "Welcome to Moria!". For the password "radiance", the secret is "Life before Death".',
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
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
        }
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "model_id": "google/gemini-2.5-flash",
            "provider_model_name": "gemini-2.5-flash",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 152,
                "output_tokens": 37,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": """\
cache_tokens_details=None cached_content_token_count=None candidates_token_count=37 candidates_tokens_details=None prompt_token_count=152 prompt_tokens_details=[ModalityTokenCount(
  modality=<MediaModality.TEXT: 'TEXT'>,
  token_count=152
)] thoughts_token_count=None tool_use_prompt_token_count=None tool_use_prompt_tokens_details=None total_token_count=189 traffic_type=None\
""",
                "total_tokens": 189,
            },
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "mellon"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b'\n\xc5\x02\x01\xd1\xed\x8aoy\x0fN]Z5\xb2\x8f}*F\xe9\t\xd2\xa41\xe7\xb9\xcf$DC\x17[\xee\xe4m\xcd\x95\x90k\xbf\x8d\r\x017@<\xb9<\x1c.Wn\xbaPK\xe92\x1a\x97\xdf\xb0\x14\x9cT\xb8s>O\x1f\x92\x1c\xc1\xaav\x94C\x91\x17ZAF\xe4\x1d\x9c\xf1\xc6\xd1MU\xd6\xf2\x10\xdd\x1d\x82\xeew\xbc\xb8\x88I<7"\xbb8 :,\xcbT6\xcdt\x1b\x07JsC\x92S\xdc[=\x8bh \x1e\xe3\\\x9f\xd8$\x00\xa3\xc7t\xf3\xeb\x16\xe6\xe5\x0e(kS\xd8\xee^{\x07\x80\x1cc\x0f\x8e@\x04\xa6\xa0\xee\xfb\x86\xec+\x87\xc2\xa0\xcbRv</)]\x8d;\xa7\xa2\x02\x03\x9bWV\x1c\xc7\x8e<n=\x8b0\x8e\xa3)\xaf\xec\xea\xbb\x86\x03Ym\xeb\xe7\xd3F\xdd|\xf5\xf0\x98=\x89|\xf8}\xc7\x88\xacS\x14I\x82\xb2\xe15FI\x89h\x11/\xd9\x7fm<\xfcx4\xb2u\xc5\xa4\x1e\xea?;\rG/\x9e\xd8\xbf\xbc\x0f\r\xd8\xabi\x88\x98\xb4\x18E\xf3\xa1\x8b06\xee\xb5\xa2\xaa\x08~\x9d^\xb3a5\xf9J\xca\xd1i\x92\xe3|\xb7\x88\xe3\xe4\xd2W$1\x97N\xb2\x03\xc2\x07\r\xdf\xf04\r\xbd\x9e\xf9<PE\xf9_\xfd\x0f6\xed\x05j\x14\x99\xd6LvY',
                                "video_metadata": None,
                            },
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "radiance"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='The secrets have been retrieved. For the password "mellon", the secret is "Welcome to Moria!". For the password "radiance", the secret is "Life before Death".\n'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": 'The secrets have been retrieved. For the password "mellon", the secret is "Welcome to Moria!". For the password "radiance", the secret is "Life before Death".\n',
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
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "provider_model_name": "gemini-2.5-flash",
            "model_id": "google/gemini-2.5-flash",
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "mellon"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n)\x01\xd1\xed\x8ao\x0em'\xd7p`\x1ff\xd4\x8fV\xdb\xc1\xf5>\xf6\xe1\x83\xb8\x85\x9eT\t1\x94\xfd\x9d\xdca\xcb\xf3\x89\x05=\xd5\xf5\nm\x01\xd1\xed\x8ao\x9b\xe8\x8a\xdcf\x1bE\xe8\xee\xb1BI\x0f08c\xae\xfc\x0b\xde'\x17\x92\x9c\x0b-i&\xec\x92wGm\xf8\x05\xdd\x94\xde\x96y\x97\x9b\xb8\xae\x86\x84X\xef=\xdd.\xd7]\xa0\xa0\xcc\xa1\xcb\x8f\x18E\x8c\xdd\xac\x1e\x02\xcb\x13\xf1\xec\x8b\xc5+\xc9YZ\xc2\xc9\x89\x84q+\xcb\xbd\xbbL\xfe\xa9\xdd\xf5\xc6~\x81\xc5\xe0\xfd\xfe7\x05\xf4i\x15Ci\n\xce\x01\x01\xd1\xed\x8aoq\x94\xe7S&?\xed\xc6\\\xb9\xd3S\xe1k\xa4+Z\xb5rs1\xf2\x98\xe9)\xb0V\xac\x1c\x95\x86\xc3\xa4C\xd6\x9c\xa1\xc7\xd8V*\xe7\xd7\xf8\x82+d\x084\xd9\xad\xea\\\x05|:\x90:\xbe\nU\x8d\\\x8fV0\r\x15\x1eD\xde\x90k\x08\n*M>!\xfa`\n)\xedo+\xe0\x94\xb4\x15\xbc\r\n\xf8Z\xd6\xf2^\xce\x12\xa0\xd4\xfd\x13\x8a\x93\x03&\xe2\x0e.\x10{(\x03``G@\x80\x1d\xdfS\x9f\x1dR\xb2gW9\xd3\xef\\\xe35\x15\xda\xd9\x1a\xadIB\x91<\xaf\xb7\xd2\x04!\x1b\x84\xdd\xb0\x1cq\xe3\x00tu\xd4\xed\xa2{\x1dv\x89\xfe*\x8cY\x9a\xc6M\x16\x0f\xa7\xb7\xd9UD\xfe\x87,\xbf/\x81M\xe4\xb1\xb1\xf1h\xea\xfe\x15E\xa9\xdbnr\xa0",
                                "video_metadata": None,
                            },
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "radiance"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text='The secrets associated with the passwords "mellon" and "radiance" are "Welcome to Moria!" and "Life before Death" respectively.'
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "The secrets associated with",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": ' the passwords "mellon" and "radiance" are "Welcome to Moria',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": '!" and "Life before Death" respectively.',
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
            "usage": {
                "input_tokens": 211,
                "output_tokens": 30,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 241,
            },
            "n_chunks": 5,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "google",
            "provider_model_name": "gemini-2.5-flash",
            "model_id": "google/gemini-2.5-flash",
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=[
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        )
                    ]
                ),
                AssistantMessage(
                    content=[
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "mellon"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": b"\n)\x01\xd1\xed\x8ao\x00=\xd0:v\xda7\xcb\x0c\\\xcad\xde_\xd5\x9ehiRn2\xd7a\xc5x\xb7\xfb\xfe\xf73\\\x9b\xb8\x81\xcdV\ne\x01\xd1\xed\x8ao5(\xdd\x18\xb50\x99\xb6\xb1W\x87\xd5\xbfY\xed\xd0\xfc\xd4\x9eZ\x14\xf9{2\x8f%,\x0ep\xe2~\x95\x01\x9e\xc2J$H\xb1\xfb\\\xf19\xecE\x0fD`\xec}\xf4\x1a\xc6\xae\x88\xfe),\x13#\xd8\xac\xc9u2\xaaH\x05\x0b\xc5\x0cD\xa52'\x1eT\x81k^Ho|i\xb9\x1a\xb1\xb1\x8dI\xccV\xf0\xe5\xee\x9e\n\x86\x02\x01\xd1\xed\x8ao<\\\xa0\xa3\x1a\xe7=\x8eS\xa8\xae\xf5p\xf0\xa0?\xd9\x95S*\xf9\xdb\x94\xb0T\x881\xe4\x03\xaf\xe2\xf6\x90\x0f\x1a.\xd6\x90\xe8\xff\xda'\x1e|\xd9>\xc4&\xf8\xc4\x8d\x1d\xc8\xe7\x9c?\x8e\xf5Qj\xc2\xee'3K\xac\xd5\x0e\x03\xb3&B\x81\xbe\xe9Ep\xb0y\x86{\xd7x\xbbc\xf0\xc4\x05\xebaq,\xfa\x07\x19[\x02\xfe\xe8q\xbbbU\xc38+\xd5\xa7;\x0f\x8e\t%\xe0\xffXc`\x97=a\xa0z\x0b\xf4L\x11\x95\x02\xcc\x1ea\xd6\xc2Vy\x10>*\xd3\x0e\x90\x98\x07\xf5c\"\xfb\xf2\xe7\xb6<\x93u[y\x10W0 \xf7\xc5a\xafiO\xfa\xdd\xc6\xa0WE-/G\xc8o\xf0\x88^\xd3\x90\x9d\xf3\x82\x05;\xda\xb2\xab\xd2\xb7(\x84\xe7\x9a>t\x08\xc47mo;k\xc5\xf9*\xe7\xc0\x92\x8f\xe3Qt\xc6n\xe4 q\xb4\x1c\xa25*\xbf\x8e\x0c\x8di\t|\xd1)4\xa1Z;\xd3>T\xeb\x1e\xabM\xdf\x12\xb6<j\xdch\xb1\xb9_\x97T\nK\x01\xd1\xed\x8ao\xb7\x8d\"\xeb\x05W\xa5\xeba\xa0P\x9d*\xd7\xbc\xf7\xfe\xfd\xff3\x98\xf5\x9a#\x02\xde\xac0i\xa4\x99g\xdd\xca\xd37\x95\x90\xf1\xcf\xab\xb8\xc9IPF\xedg2^\x18\t\xd2\"\xf2C\xdbU,\xd0>5\xf6\x87L\xf5v\xa8@\xcc",
                                "video_metadata": None,
                            },
                            {
                                "function_call": {
                                    "id": None,
                                    "args": {"password": "radiance"},
                                    "name": "secret_retrieval_tool",
                                },
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": None,
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="google_unknown_tool_id",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
I have retrieved the secrets for the provided passwords.
For the password "mellon", the secret is: "Welcome to Moria!"
For the password "radiance", the secret is: "Life before Death"\
"""
                        )
                    ],
                    provider_id="google",
                    model_id="google/gemini-2.5-flash",
                    provider_model_name="gemini-2.5-flash",
                    raw_message={
                        "parts": [
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": "I",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
 have retrieved the secrets for the provided passwords.
For the password "mellon", the\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                            {
                                "function_call": None,
                                "code_execution_result": None,
                                "executable_code": None,
                                "file_data": None,
                                "function_response": None,
                                "inline_data": None,
                                "text": """\
 secret is: "Welcome to Moria!"
For the password "radiance", the secret is: "Life before Death"\
""",
                                "thought": None,
                                "thought_signature": None,
                                "video_metadata": None,
                            },
                        ],
                        "role": "model",
                    },
                ),
            ],
            "format": None,
            "tools": [
                {
                    "name": "secret_retrieval_tool",
                    "description": "A tool that requires a password to retrieve a secret.",
                    "parameters": """\
{
  "properties": {
    "password": {
      "title": "Password",
      "type": "string"
    }
  },
  "required": [
    "password"
  ],
  "additionalProperties": false,
  "defs": null
}\
""",
                    "strict": False,
                }
            ],
            "usage": {
                "input_tokens": 231,
                "output_tokens": 45,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 276,
            },
            "n_chunks": 5,
        }
    }
)
