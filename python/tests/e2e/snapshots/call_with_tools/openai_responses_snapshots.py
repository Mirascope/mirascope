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
        "provider": "openai:responses",
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
                        id="call_7PCAKM4iW29aW8ItSVTC9eV5",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_l7qamG7Q2wqON1MyOUD3aRyW",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_7PCAKM4iW29aW8ItSVTC9eV5",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_045ee92b75b080e00068e70531a4d88196bef2a946e3f13693",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_l7qamG7Q2wqON1MyOUD3aRyW",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_045ee92b75b080e00068e70531c00081969e3a23654e148bd2",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_7PCAKM4iW29aW8ItSVTC9eV5",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_l7qamG7Q2wqON1MyOUD3aRyW",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the retrieved secrets:

- For the password "mellon": Welcome to Moria!
- For the password "radiance": Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_045ee92b75b080e00068e70532be748196af36d8eb6cef6e6d",
                        "content": [
                            {
                                "annotations": [],
                                "text": """\
Here are the retrieved secrets:

- For the password "mellon": Welcome to Moria!
- For the password "radiance": Life before Death\
""",
                                "type": "output_text",
                                "logprobs": [],
                            }
                        ],
                        "role": "assistant",
                        "status": "completed",
                        "type": "message",
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
        "provider": "openai:responses",
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
                        id="call_J4LuJT8K3So8Sj7xkm7kD9ZG",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_RKPhE057TAkNNtKhL0UkaKqP",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_J4LuJT8K3So8Sj7xkm7kD9ZG",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0d091b1043ced5c40068e705350ff081969fc367512a72f5d1",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_RKPhE057TAkNNtKhL0UkaKqP",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0d091b1043ced5c40068e7053570dc81968161667888173255",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_J4LuJT8K3So8Sj7xkm7kD9ZG",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_RKPhE057TAkNNtKhL0UkaKqP",
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

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0d091b1043ced5c40068e7053640048196adfb42a5c9baaffa",
                        "content": [
                            {
                                "annotations": [],
                                "text": """\
The secrets associated with the passwords are:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
""",
                                "type": "output_text",
                                "logprobs": [],
                            }
                        ],
                        "role": "assistant",
                        "status": "completed",
                        "type": "message",
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
        "provider": "openai:responses",
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
                        id="call_LctPBs1R2tGhln7TBf1ZEX3C",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_UbMbQSvY6TYya8s058rrMZyv",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_LctPBs1R2tGhln7TBf1ZEX3C",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_UbMbQSvY6TYya8s058rrMZyv",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
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
        "n_chunks": 28,
    }
)
async_stream_snapshot = snapshot(
    {
        "provider": "openai:responses",
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
                        id="call_afDFm1ADaw5j77gb2E1SRjEh",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_i17I4phd6PznExMGe5BjiVef",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_afDFm1ADaw5j77gb2E1SRjEh",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_i17I4phd6PznExMGe5BjiVef",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
Here are the secrets for the provided passwords:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
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
        "n_chunks": 32,
    }
)
