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
                        id="call_I1rBFpMqj7coOwyMai3oPYuu",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_B2vNfAjs3OfMl9w5fjbG0JtS",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_I1rBFpMqj7coOwyMai3oPYuu",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0486c34efb5d96250068e8163126c8819083b62892a67e3fca",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_B2vNfAjs3OfMl9w5fjbG0JtS",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0486c34efb5d96250068e8163172d88190bc3868e717a73a9b",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_I1rBFpMqj7coOwyMai3oPYuu",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_B2vNfAjs3OfMl9w5fjbG0JtS",
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

- **mellon**: "Welcome to Moria!"
- **radiance**: "Life before Death"\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0486c34efb5d96250068e8163267e081909741eec242a44316",
                        "content": [
                            {
                                "annotations": [],
                                "text": """\
Here are the secrets associated with the passwords:

- **mellon**: "Welcome to Moria!"
- **radiance**: "Life before Death"\
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
        "n_chunks": 35,
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
                        id="call_uo1iCXnyuyEi2hrcDDp5rckN",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_fzIrls1NOhfCvW1siCw8IlQw",
                        name="secret_retrieval_tool",
                        args='{"password":"radiance"}',
                    ),
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "arguments": '{"password":"mellon"}',
                        "call_id": "call_uo1iCXnyuyEi2hrcDDp5rckN",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0572a29aa5eabed20068e8163550048197953bca5e06e77a94",
                        "status": "completed",
                    },
                    {
                        "arguments": '{"password":"radiance"}',
                        "call_id": "call_fzIrls1NOhfCvW1siCw8IlQw",
                        "name": "secret_retrieval_tool",
                        "type": "function_call",
                        "id": "fc_0572a29aa5eabed20068e816356ee88197a385af16413049ff",
                        "status": "completed",
                    },
                ],
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="call_uo1iCXnyuyEi2hrcDDp5rckN",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_fzIrls1NOhfCvW1siCw8IlQw",
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

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                    )
                ],
                provider="openai:responses",
                model_id="gpt-4o",
                raw_content=[
                    {
                        "id": "msg_0572a29aa5eabed20068e816366b148197a85f77737f9e88bd",
                        "content": [
                            {
                                "annotations": [],
                                "text": """\
Here are the secrets associated with the passwords:

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
        "n_chunks": 32,
    }
)
without_raw_content_snapshot = snapshot(
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
                        id="call_2l5zWsybzlLfRnKNZcUwPCDD",
                        name="secret_retrieval_tool",
                        args='{"password":"mellon"}',
                    ),
                    ToolCall(
                        id="call_QkfbCECtJTNDR7Mt8HqZG0jf",
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
                        id="call_2l5zWsybzlLfRnKNZcUwPCDD",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="call_QkfbCECtJTNDR7Mt8HqZG0jf",
                        name="secret_retrieval_tool",
                        value="Life before Death",
                    ),
                ]
            ),
            AssistantMessage(
                content=[
                    Text(
                        text="""\
The secrets have been retrieved:

1. Password "mellon": Welcome to Moria!
2. Password "radiance": Life before Death\
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
    }
)
