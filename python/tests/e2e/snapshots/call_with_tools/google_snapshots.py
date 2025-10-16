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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b"\n)\x01\xd1\xed\x8ao\xfe\x0b\xad\xf2\xce\xed\xd3\x01\xa7\xc7\x042\xfd\x938QW\x96\xb1F\rP\xee'!\xd16\xf9\x8aH\xeb\xb70\xc8\xd8\xbe\nm\x01\xd1\xed\x8ao\xcb\xd8\xa2\x01\xf3]e;U\x7f]^z\x8aa\xcf\x86\x03<\xe90{*\xf3\xfbJ/G\xbd\xe3gpZ\xecnR\r\x8bI\xadT,\xef\xbf\xa5\xa9\xeaCcye\x1e\x8f\xfe\xf3?\xa5\xcd\xe2\trB5\xb6n\x83\x0f\x80\xba;^\x0b\x96\xe5&t\x92\xdb\xb7S\xe7\xe2\x8b\x1c`3Ls:?\xc5Y]\xb3\xc9\x86\n${\xc9\x08\xaf\x1a(\n\xfa\x01\x01\xd1\xed\x8aoc3\xa7t\x00\x05\x1e\x1c[\x0e\r\xcb\xd6%\xa6v\x0bD0\x87\x19aE\x1b\xc5\x1f\xf6\xf7\x03kpQ\xea\xd1\x98S\x90S\xb8_\xc1`\xa1\xc0d\xe5\x8a\xe2\xcfS\xfez)\x93\xc7\xe3\xdd\x83\x12\x10q/S\x11\x887e\xf6g\\\xbc\xb0<q\x195\xd0\x90`Rf\x81P\xb4\rGd\xfb\xb6\x8b'\x17f\xc5\rmuS\xbf'?\xbbs\xb7U\xf8\x97|/P\x11\xcf^\x14]\x01Z\xe9\xe6\x1c\xcbm/\x87>\x92\xb1\x9c|\xdc\xdf:\x0f#O&\x9d\xfcO\x9a\xf9\x98KH\x05F?\xbc\xd9\x14\xa7\xf0\x01]\x13\x0c\xb8BU\x02\xf6\n\xd3\x83\xe6\x0f?\x12\x9d\xc10\x17P\xb7\xa0D\x08\x12g\x0e\xc7RV\xc8k<7\xfa\xdb\xd0\x18\xe0\x90\xfbwg\x18W\xb1\x0e\xf0\xfb\x90\x0c\x14\x9a\xce\x8f\xa7\xbf\x0f{5\x86\xb0\xe3+LCs&\xe7\x10\xdf\x8d\xfb\xb1&\x8b\xd2\xbc\x07G\xbb\x8bV\xf0\x02L\xe8\xf4\xdf\x99v\x7f\n<\x01\xd1\xed\x8ao\xc7\xa4 \xdc\xda {E0\xa9\x94\"C\xb6\x99\xccb\x8a=\x1fV\xfb\xf5\xcd\xeb7N\x90r\xber&\xce\xd9c\xac\x16\x8c,o\xabm\xdf\xa5nk\x03\xb6Z\xae\xf1Q\xaa\x1d\xd3",
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
The secrets for the provided passwords are:
* mellon: Welcome to Moria!
* radiance: Life before Death\
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
                        "thought_signature": None,
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "The secrets for",
                    },
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
                        "text": """\
 the provided passwords are:
* mellon: Welcome to Moria!
""",
                    },
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
                        "text": "* radiance: Life before Death",
                    },
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
                raw_content=[
                    {
                        "video_metadata": None,
                        "thought": None,
                        "inline_data": None,
                        "file_data": None,
                        "thought_signature": b'\n$\x01\xd1\xed\x8aov\xfd\xcf]#{u\x7f\xc2\xef(\xef\x96\xdc(`\xe3=\x8ct\xc9\xf9\xbe7\xbe\xa1\xd4\x8f\t\x06\xfd\nj\x01\xd1\xed\x8ao\x1a\xf3\xd5\xbfx\x1f\xfb\x08\xae:\xd6\x86\x9dy\x7fn5\xb4\x0e@r\xee\xf1\x85/\xb8\x13B%\xd7Nq\xf0\xaf\xbb\xd4V\x04\xfe\x0eL\x9f"\x88S\xaby\xc4p\xc0\x10\xde\x05\xd4>p\xdd\xb6\x06\xeb&\xbe\x0b}o\xf2i\x83\xf9\xa0\xf9\xabZ\x1c\xb9v\xea\xc0#.\xa0X\x12\x99#i\xd8\xbe\xc7vua\x97\xbbmz\xea\x81\x85R\x80\n\xea\x01\x01\xd1\xed\x8ao7.\xaeD\xf2\xafe\x9cYu2W\x99G0B;u\xb5\x9f\x17*h)\xef\xf6\x13\xea\x95\x10\x10\xc5\x06c\xfe\xa8\xf9M\xd0\xde\xb4\x85=G@\xce\xe6x\xc6\xc2 \xe6\x18\x7f\xe8XO\xa7\x13\xcb\xb9\xb8\x97\xb2~\x18|\xcaJ\xa6\x1e\x90\x87\x87\n\xde\xf0\x8a2\x94\xde$\x17\x9d\xa0\x95\x03\xf8\xe3]\x07+( \xb8\xa2\xbe\x98\xa1\xf8:aL\x1b\x98s\xe67\xcdX!+\x13\xa74B\xa5\x83>L\xf6\xf5\xc2\x9b\x83\xb4\x9eUd\x8e\xc4\xc1Yn\x96@C\xb1\xed\xcb\xfaG\xf2k\x9dVnc]\xb83n\x02t\xd8\x98\x04\xa5;\x9c\xce\x05*\xc5\xe8\x8e\x1a\xe9b\x93Z\xc0[\x8a\x94\xb9F\xb5%^\x94\xc4X,\xbc\xa5\x86\x80$\xdfne\xe1%\xd9n\x96\xbc\xc0\xa2\x80t|\x19\xef\xd94\xe9\x18\x13\xa254\x1f\xcf.\xfa\xc0;T\x991QS\x9f\x89\tfA',
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
                        text="The secret for 'mellon' is 'Welcome to Moria!' and the secret for 'radiance' is 'Life before Death'."
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
                        "thought_signature": b"\n)\x01\xd1\xed\x8aoy\xa0&Q?j\xebB$E\xeb\xd1\xfb\xb1c\x106\xebc\xa1\xc2\xc2l\xdd\xcaY\x01;@\xcd\xa9y\xb4E'}\np\x01\xd1\xed\x8ao\xf1\x9e\x14\xf6]t\xe0\x8a\xa0B\x07\x19_\x0f\xae\x891N\xb1\xbflo9\t\xf6CWb\xc3\xc4KQ\xc0\xc6\xb4\x06P7j\x1ce\xbd\x080O\x89~\x9f\x9dd\xd9\xbe2\x96\xa3\x1f\x84\n\x95\x97\x9a\xf0j3/\x0b\xa0Im\xb0\xc8p\xff\x93\xfaO$2\x05\xbe\x14\x8e`\xfc\x80\xdd\xfc\xecs\xa1\xd7f\xdbU\x8f%`\xce\xb1$z\xb5\x12\x9dxn\xbc\n\xc6\x01\x01\xd1\xed\x8ao\x8b\xa5\xf1A{\xfe\xe4\x11$\xe41\xa6Fq\xab\x9f\xff\x89d9\xf0N\xbf\xa7\x1f\x07\x18\xaef\xa8O\xc3\"E\xa3^\x18\xde\xe1\x04\xc8\xdcy\x81\xfe\xad\xb4\x0f\xdaO\x0bag\xbfT\xe5C\x13\xe1\x0e\xcf\xe2\x85f\xf1\x15\xa47\x8b~\xa1dL\x90\x1b\x1f\x81`\xb4\xc8\xae\xff2\xffkJy\x99\xc6\xa9J\xdf\xc4\xaeS_r\xb2\x08\x02\x9d\x1d6v\x82\xcb28-O;U\xa73\xe9\x14\x91\x85\x93\x9b\xb3A$nuI\xc9iD\x8f\xd4D\xb1[T\x12T\xac\xbb\xb57X\x8c\xe2\xdd\x8d*e\xe6\nT\xac\xbf(~\x9d\x11n\x9a2\x94\x8cF\x03\xf9\xf7\x1aD\x13p8\x98t,i/\xe8\x0e\xe6_m\xfe\x99\xe4\xe9B\xfbM\xf1\r\x0c\xe1\xbd\nP\x01\xd1\xed\x8ao\xca\xe8\x1aH<8\x04\xcc\xf1\x1d\x96\xb9\x81\x06\x8f\x15\x1a)\x00\xdft\x9f\xb2}\xccQ*\x0cj=\xa8\n\x04F\x0c\xe6\xdbX\x07\xaa`\xd3U\x92\xa9\x94?\xd2\xf61\xac\xc8\x0fu\xf3uAMW?\xa9)\x05\r:\xcav2\x9f\x07\x97IN^X",
                        "code_execution_result": None,
                        "executable_code": None,
                        "function_call": None,
                        "function_response": None,
                        "text": "The secret for 'mellon' is 'Welcome to Moria!' and the secret for 'radiance' is 'Life before Death'.",
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
        "n_chunks": 3,
    }
)
