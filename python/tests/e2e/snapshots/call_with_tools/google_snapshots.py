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
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n\x96\x05\x01\xd1\xed\x8ao\xf6J\x9a\xc5\x8dz\xb24 \x84M}\xe2\x16<\xd4q\xcdg\xe5_;iN\x01\x9f\xb7O\x1e\xfb\xe56[_\xb4ig\xb9x]msnB\xa7\x12\x8b\x94\xc9\x9c\xb9`\x80]\xcb\x82O\x8b\x86\\\xce\xa8^\x9d\x93\x98\xed\xc2\xe1\x7f\xf5s\x83\x11r\xdd0\x9c\xe7\x96\x12+\xd9\xd7\xfd\xcd\xee\x07\xd23\xd0\xc7s\x14\xa2#\xcb\xf2\xba\rYO\xa2\x9fT[\xa4$\xe5\x94\x15q\x03o\n\x10o<S\x0fyG\x89r\x8cQ?j(\xc6O<\xa7R\xf4wQ\xcf\xc7\xae\xb9\x01F\xa4\r\xadv3iR\xcb\xfd\x84,j\r\xd4\xaeha3`\x92\x82E\xe7\xaf\xfa\xacX\x89`\x94\xbe\xa3\xeb\xfd\xff\xd9\x16\xff\xf5\xff_\xdaX\xa6\xacN\x0c\x7f\xddM\xe4\x96eQ=3\xeb\xdat\xab\x16\xb0\x98\x8f\x81\x91\x16\x04\xe8j>\xe2\x0e0\"pj\x8c\x88\xa7\xab\x05l1]ih)j\xc4\xa6\x12\x18(\xbb&\x86\x96\xe2v\x06\xda\x0c<\x11V\xa9i\x9bwP)\xff\x8a\x1f\x11)\xee\x01\xecP{f\x90\xea\xd7\xd9Ie\xf6\x1d\xc5\xe0\x9bi'zO\xceM\x1d\xe9VmhO0\xac\xd7\x00Z\xcd,\xd0\x93\xfe\xe5\x81\xc8\xaa\xc5\xea\xf6\xc3Y\x9c\xed\x83\xcc\xce\x92\xf5\xf8\xb5O\xb3\x9e\x1f\xddUx\xd1u\xf2\x85\xb0\xff>+\xed\xe5\xa3\xe2\xf5v\xa9\xb3uc}\xed9\xa4\xa5\xbf\xed-q\x9b\xc3Qs\xd2H\x92=\xf4\x16:\x88\x00\x12<\x9d\xcf\xd7l\x8f5)I\xd2\x80\xbcC\x8a\x9dc\x11\x12\x02z\x99\x13\xda\x04Y\xfc\xc8\x93Wah\xeeES\xeaS\xeb,XX\x9a\x18\xfb\xe5\xafi%\xd3\xa1\x9f\xa1.7x\xd8\x0c(=\xf5,MCa\x8f\xadT\xe4\xbc\x14\xb8\xc2'\xd9\x95\x9daK\xd5\xa5\xcf\xc7yPl5\xe4\x8bt\xca\xa6\x9c5\x01\x87M\xa2\xb4#\x0e\xe3\x10\x08'\xaa(\xa2t\xdf\x0b{\x8a\n>\x92\xdd\xafU\xdfs\xfc\xba!J\xf5\xbek\xb9\xb9\xea.\xc3\xaa\xd8>'\xe1\x80do\x90\xb19\xf1\x9eh0\xf8Y\xc16\x08G\xd0:R\xf2X\x87\xad\x9e\x9aT\x05\xf3pl\xdf\xba\xe6M\r[`q\x99;\xdb\xd4T\x8c\xd2D!\x1c\xaa]o\xe6m\x18\xd4\xe09\xd2BJv\xc5;y\x86\x9c\xd8\xb6\xd7\xc1\xbaN\xd10\xde)C7/M\xc4\x9f\xaf\x16Di\xd2u,\xea\x13!\xe8\xe5\x88\x95\x89\xc8\x14\xca2d~\xf6\xde>\xd0\xe4\r0\r\xc1\xe3v\x95F\xe6i\xc2\x85&Y\x9a[D&i\xf1D\x7f\xabS-@\xf3\xdc,\x84\x8f5b\xd0`04\x86\xd2\x8eO\xc5T\n\xc0\xa8\x99\xef",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"password": "mellon"},
                            "name": "secret_retrieval_tool",
                        },
                        "function_response": None,
                        "text": None,
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"password": "radiance"},
                            "name": "secret_retrieval_tool",
                        },
                        "function_response": None,
                        "text": None,
                    },
                ],
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
Here are the secrets you requested:
* For 'mellon': 'Welcome to Moria!'
* For 'radiance': 'Life before Death'\
"""
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n\xd4\x02\x01\xd1\xed\x8ao\xf6\x91\x13[+KuRg\x9a\xceq\xad\xc3\xa2d\x0c\x1c(L\xd8\x1e]\xb3\x97\x19\xe0\xcc\x7fM\x8c9dq\x1b\xf5\x1e\xf67]\x98U9\xcd\x08\xe2\x0c "\xb8R\x13\xf3\x06jC\xa5\xe70U\x11\xf0\x0c\xc8\xfcS\xee\xfd)\xed\xd4O\x99\xe6\xb46;\xd0\x0f\xee\xee\x1e\xe40\xc3K\x11\xda\xc1\xa1\xdc\n\xbeU\x12r\xa3?\x0bz\xc9=\xadw\xaaJ\x083\x80A\x9e\xa3o\x00d\x83X\xa5\xd5Z\xc8\xd2\xcf\xa0\x94\x0c\xac\xc1\xcc\x90\xfc\x81\xb1L\xe0m\xae\x1e:\xb9K\xad\x92|\xc0\xacGT\xaan\xdc\xec\xe4a\x14=\xd2\xb2\xe8Dl-;\xcdZ9\xbb\x03\x87 \xe0o\xbac=x\xe6J\xda\t\x8c\x93D\xf7\xca\xc9\xd0\x889\xe7\xefVpf\x1a"\xed\x10\xfb\xa6\x0cW\xaf\x85\t~\x8a\x01\xc8n9\x176R\xd4J\x10\x8e\xc9_\xb1\xa9\x89\x9a\xf9\xd5\xdf#\xec\xb5\x84s \xcf#:)t\xfbd\xd2\xc6Fia\x90\xf9J\xc9\x9f\xc5g(mP\xfb\xf2\x8e4Q\x13\n\xddN.|\x04\xa0lq\xc3<\x13\xe9\xd4N\xac\x82:\x81\x17\xd0"{8:\xb7~\x1f\xd4\xcci`\xdb\xfa\xe8%d\x18gR\xcctG@w\xd5\xab\xf6\xbeW_\xd6\x932F\xdb\xf6\xe0\xf0\x80\xbb\x9b\xd7\xb8m|\xef>\xfe\xef\x84r\x11:',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": """\
Here are the secrets you requested:
* For 'mellon': 'Welcome to Moria!'
* For 'radiance': 'Life before Death'\
""",
                    }
                ],
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
)
async_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
        "params": {},
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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n\xee\x03\x01\xd1\xed\x8ao\xe9\x04\x04`\xe3\xf4\n,\x8d7\x90J\xff\x7fV\xa7\xe8\xbbT\xc3t\x8f1+\xec^\xf1[c\xf3\x0f\xca\xa3m\xcf@\xe8\x9a\xc4x\xa7\xad\x00\xf5\xbf\x95\xca\xf1l\x8aOI\x9a\xd5\xba\xa9\xedc\xb1\xaask\x03,\xc8\x18\x8b:A~G\x01\xfe\xd6\xbezZ\xb0,\xb8l\xf9\xacO\x9b1\xf6z\x0ck\x11\x9c\x12\xaa\x9cR\x03q)\xd6*H\xe8x\x00\xd0\r\xa8d\x95T\xe4\xdc\xfb\x80\xe9\x8ak\xd6\xed\xa0\x1a\xde\xe9[\x1b\xd1\xa3\x03\xf4\x84\x06|\x12V\x88\xa3\xae\xa7\x91\xef\r\xcfe\xc2\xca\xa0\xb0\x0c\x9d\xd0\x96\x80\xbe(\x1dH\x9dne+\x0e\x9a\x0b8t\xa4\xbe\x08D\x9c\xbas%\x96\t\xf0\xa0\x10\x10\r9\xd9-(!nk\x00o\xf7\xd0Kpq\xc6A\xcf\xb7\xe4*J+\x81i\xd7\xb2y\x92\xf6\x1f\x88\x88\xae{^\x8e\x19!\xf4z\xe9\x05\xd9?\x9e`\xa83\xfd\xdf\x05\xdc\xa8:\xdb\xd1j\xd0\x1ao\xbfW\x83)?WRk\xe0\x89/\xe8n\xd7\x0c\x1b\xb84\xb8\xc6\x91$q\xc0\xe6&\x06&R\x92\xf7\xbe\xd3\xacK\xc5-\xd3\x85\xb9s\xfb\xe0\r#\xf5\xf3`\x9fE\x16"\xe8\x1a\xb1\x99\xf9r\x90\x8e\xb6\x05\x80o\xb2\xaf\xb2\xfb\x99i\x15u\xa8\x08\xbe\xe1\x04Ei\xa46\xdf\xf3\x13\xcfQ\x0b\xd5NLB\x96\x96[\xb0\xd93`\x90L\x91\xc8zE\xc5]\xb7\x99\x818;xr\x97\xa1]\xb6\xfe\xe7\r\xea\xc1\x90\x9c8\x87\xa8\x19t7\xb8\x9a\x1d\x0b\x8b\xeb\xc2\xa2\x15=\x9d\x80\xefq\x0e\x0c\xfa\x0f\xad\xce\xd7\xad\xa3\xed\xabj\xdf\xb8\xd6\xa9\xe6\x94*\x95\x1c\x9a\xb9!G\xc8:\xdf\xae\x17\xfa\xaf\x1fC\xd4\xb0\x99\xf4\x95i\xa9z\xdc=B\xb9}\xe1\x1afw\x8b\xc7\xe2\x8b\xd5\x02=S\xb0"Z\x8e\x16\xc7Q\x9c8\x98\x06\x86\xa3\r^\xd0s`\x00\x87)\x82\xc8\x94?N\x9dYeA\x06r&\x99\xe1\xac\x91\xe8/\xcav-\xee\x93T',
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"password": "mellon"},
                            "name": "secret_retrieval_tool",
                        },
                        "function_response": None,
                        "text": None,
                    },
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": {
                            "id": None,
                            "args": {"password": "radiance"},
                            "name": "secret_retrieval_tool",
                        },
                        "function_response": None,
                        "text": None,
                    },
                ],
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
                        text="The secrets have been retrieved. The secret for 'mellon' is \"Welcome to Moria!\" and the secret for 'radiance' is \"Life before Death\"."
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "The secrets have been retrieved. The secret for 'mellon' is \"Welcome to Moria!\" and the secret for 'radiance' is \"Life before Death\".",
                    }
                ],
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
)
stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                        text='I\'ve retrieved the secrets for both passwords. The secret for "mellon" is "Welcome to Moria!" and the secret for "radiance" is "Life before Death".'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
        "n_chunks": 5,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "google",
        "model_id": "gemini-2.5-flash",
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
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
                        text='I have retrieved the following secrets: "Welcome to Moria!" and "Life before Death".\n'
                    )
                ],
                provider="google",
                model_id="gemini-2.5-flash",
                raw_content=[],
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
        "n_chunks": 3,
    }
)
