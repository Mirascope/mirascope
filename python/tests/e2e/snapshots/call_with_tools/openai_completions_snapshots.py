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
                        id="call_48PWiWbKVpKIBOmZX4BT0TfR",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_1yE3tZKwdKM9Zh7zROGxSlS0",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_48PWiWbKVpKIBOmZX4BT0TfR",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_1yE3tZKwdKM9Zh7zROGxSlS0",
                                "function": {
                                    "arguments": '{"password": "radiance"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                        ],
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_48PWiWbKVpKIBOmZX4BT0TfR",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_1yE3tZKwdKM9Zh7zROGxSlS0",
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

- For "mellon": "Welcome to Moria!"
- For "radiance": "Life before Death"\
"""
                    )
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "content": """\
The secrets associated with the passwords are:

- For "mellon": "Welcome to Moria!"
- For "radiance": "Life before Death"\
""",
                        "role": "assistant",
                        "annotations": [],
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
                        id="call_m9OMID8oqvilCr3uun1HDfcm",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_n7IORdNAHm2JuhLcozct7mNQ",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "role": "assistant",
                        "annotations": [],
                        "tool_calls": [
                            {
                                "id": "call_m9OMID8oqvilCr3uun1HDfcm",
                                "function": {
                                    "arguments": '{"password": "mellon"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                            {
                                "id": "call_n7IORdNAHm2JuhLcozct7mNQ",
                                "function": {
                                    "arguments": '{"password": "radiance"}',
                                    "name": "secret_retrieval_tool",
                                },
                                "type": "function",
                            },
                        ],
                    }
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_m9OMID8oqvilCr3uun1HDfcm",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_n7IORdNAHm2JuhLcozct7mNQ",
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
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "content": """\
The secrets associated with the passwords are as follows:

- For "mellon": Welcome to Moria!
- For "radiance": Life before Death\
""",
                        "role": "assistant",
                        "annotations": [],
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
                        id="call_ln01qkbnwFeNRhfi86psg35Z",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_FbcVlNserV7TjIqX0EOUczzH",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_ln01qkbnwFeNRhfi86psg35Z",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_FbcVlNserV7TjIqX0EOUczzH",
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

- For "mellon": "Welcome to Moria!"
- For "radiance": "Life before Death"\
"""
                    )
                ],
                provider="openai:completions",
                model_id="gpt-4o",
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
        "n_chunks": 36,
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
                        id="call_FwSXRiCzZZXTL1eAz8QJ5ljl",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="call_zpDNjpvsWFRYUGiE7qiDR4Vz",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ],
                provider="openai:completions",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_FwSXRiCzZZXTL1eAz8QJ5ljl",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_zpDNjpvsWFRYUGiE7qiDR4Vz",
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

- For "mellon": "Welcome to Moria!"
- For "radiance": "Life before Death"\
"""
                    )
                ],
                provider="openai:completions",
                model_id="gpt-4o",
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
        "n_chunks": 36,
    }
)
