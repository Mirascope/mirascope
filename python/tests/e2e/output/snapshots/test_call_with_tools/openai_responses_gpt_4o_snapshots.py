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
                            id="call_X8haBK404EekgVGzdjughC6d",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_sBsocB1eHoJ5JRek7l2RLAzS",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_X8haBK404EekgVGzdjughC6d",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_022c6f9c3ddea69d00690a1f8495fc8190a0638886411c91c0",
                            "status": "completed",
                            "response_id": "resp_022c6f9c3ddea69d00690a1f83488c819089f3e6f781f3658c",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_sBsocB1eHoJ5JRek7l2RLAzS",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_022c6f9c3ddea69d00690a1f84b9b48190b6b8ee06c175bc42",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_X8haBK404EekgVGzdjughC6d",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_sBsocB1eHoJ5JRek7l2RLAzS",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets for the given passwords:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_022c6f9c3ddea69d00690a1f8628e0819096cd6e52c5329160",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets for the given passwords:

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
                            "response_id": "resp_022c6f9c3ddea69d00690a1f854c1c8190b3a8dca5e69a4816",
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
    }
)
async_snapshot = snapshot(
    {
        "response": {
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
                            id="call_tCxqlymiNhUrqr9yhdFzYqqs",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_t0Am4hCvwG27GqE10jL7ctQZ",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_tCxqlymiNhUrqr9yhdFzYqqs",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_039f6930b35f776c00690a1fdb58fc8193a4b59d06cd9b812f",
                            "status": "completed",
                            "response_id": "resp_039f6930b35f776c00690a1fd8db8c8193b45f1fcf7789dce2",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_t0Am4hCvwG27GqE10jL7ctQZ",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_039f6930b35f776c00690a1fdb897881939e51b5240180d4e8",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_tCxqlymiNhUrqr9yhdFzYqqs",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_t0Am4hCvwG27GqE10jL7ctQZ",
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

- "mellon": Welcome to Moria!
- "radiance": Life before Death\
"""
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_039f6930b35f776c00690a1fdda9fc81938f4b068d8adecd6c",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with the passwords:

- "mellon": Welcome to Moria!
- "radiance": Life before Death\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                            "response_id": "resp_039f6930b35f776c00690a1fdc42148193b860326a5e088a0e",
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
    }
)
stream_snapshot = snapshot(
    {
        "response": {
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
                            id="call_97ayj0C3bp5IcprjGmdcP3YD",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_SOHDB5HyLUg7QvE7pUWlXUMQ",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_97ayj0C3bp5IcprjGmdcP3YD",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0512b776faee5b9e00690a1fb4afb08193adc53f637ab28645",
                            "status": "completed",
                            "response_id": "resp_0512b776faee5b9e00690a1fb3e6b4819395a39400dddec77c",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_SOHDB5HyLUg7QvE7pUWlXUMQ",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_0512b776faee5b9e00690a1fb4ccd48193a1c954cd4b2e45d6",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_97ayj0C3bp5IcprjGmdcP3YD",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_SOHDB5HyLUg7QvE7pUWlXUMQ",
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

1. **Password "mellon":** Welcome to Moria!
2. **Password "radiance":** Life before Death\
"""
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_0512b776faee5b9e00690a1fb7df488193a4594b67ac6b02cf",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the retrieved secrets:

1. **Password "mellon":** Welcome to Moria!
2. **Password "radiance":** Life before Death\
""",
                                    "type": "output_text",
                                    "logprobs": [],
                                }
                            ],
                            "role": "assistant",
                            "status": "completed",
                            "type": "message",
                            "response_id": "resp_0512b776faee5b9e00690a1fb547dc81938da9d903d4a58194",
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
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
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
                            id="call_BnBrJ4EwrnrNrOAgYK5QJtZk",
                            name="secret_retrieval_tool",
                            args='{"password":"mellon"}',
                        ),
                        ToolCall(
                            id="call_3rPVUHZLIu5xyoiazpL8PRII",
                            name="secret_retrieval_tool",
                            args='{"password":"radiance"}',
                        ),
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "arguments": '{"password":"mellon"}',
                            "call_id": "call_BnBrJ4EwrnrNrOAgYK5QJtZk",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_06995068fdb81d8900690a1fe1b9a881959c5d4f9f4d7e6095",
                            "status": "completed",
                            "response_id": "resp_06995068fdb81d8900690a1fe11b14819596489c2bd1c2a0b6",
                        },
                        {
                            "arguments": '{"password":"radiance"}',
                            "call_id": "call_3rPVUHZLIu5xyoiazpL8PRII",
                            "name": "secret_retrieval_tool",
                            "type": "function_call",
                            "id": "fc_06995068fdb81d8900690a1fe1e4c881959e2a3526d6d10ae1",
                            "status": "completed",
                        },
                    ],
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_BnBrJ4EwrnrNrOAgYK5QJtZk",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_3rPVUHZLIu5xyoiazpL8PRII",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets associated with each password:

- **mellon**: Welcome to Moria!
- **radiance**: Life before Death\
"""
                        )
                    ],
                    provider="openai:responses",
                    model_id="gpt-4o",
                    raw_message=[
                        {
                            "id": "msg_06995068fdb81d8900690a1fe319d08195938dc9b93ecbe933",
                            "content": [
                                {
                                    "annotations": [],
                                    "text": """\
Here are the secrets associated with each password:

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
                            "response_id": "resp_06995068fdb81d8900690a1fe244c08195a96bae2221a1e526",
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
    }
)
