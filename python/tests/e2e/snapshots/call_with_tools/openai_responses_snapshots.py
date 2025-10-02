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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
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
                        id="call_JQqtsz9bkXdMOxgKSTPMzrTJ",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_tMJduiy2x9jyYFdvuj9EECKz",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_JQqtsz9bkXdMOxgKSTPMzrTJ",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_tMJduiy2x9jyYFdvuj9EECKz",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets associated with the passwords:

- Password "mellon": Welcome to Moria!
- Password "radiance": Life before Death\
"""
                    )
                ]
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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
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
                        id="call_eR7uv8TAMgK9QIvsUi1vCN7l",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_v2jm1GF65QeGcFRag3maPgd1",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_eR7uv8TAMgK9QIvsUi1vCN7l",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_v2jm1GF65QeGcFRag3maPgd1",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The secrets associated with the passwords are as follows:

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
"""
                    )
                ]
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
        "provider": "openai:completions",
        "model_id": "gpt-4o",
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
                        id="call_gW1z2A8yHEXnMckKyEy9j3Yw",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_r2JnBaLPnPmwnz9Xg12oi2XO",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_gW1z2A8yHEXnMckKyEy9j3Yw",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_r2JnBaLPnPmwnz9Xg12oi2XO",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The secrets associated with the passwords are as follows:
- For the password "mellon": "Welcome to Moria!"
- For the password "radiance": "Life before Death"\
"""
                    )
                ]
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
        "n_chunks": 40,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:completions",
        "model_id": "gpt-4o",
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
                        id="call_PcjqAXHF0Lqxpbmlz1K2eW1C",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_Q1fNFQmcOS7JfHf2fktmc8tz",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ]
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_PcjqAXHF0Lqxpbmlz1K2eW1C",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_Q1fNFQmcOS7JfHf2fktmc8tz",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The secrets associated with the passwords are:

- "mellon": "Welcome to Moria!"
- "radiance": "Life before Death"\
"""
                    )
                ]
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
        "n_chunks": 32,
    }
)
