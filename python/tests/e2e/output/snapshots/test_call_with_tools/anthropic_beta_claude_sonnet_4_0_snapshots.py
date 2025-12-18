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
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 602,
                "output_tokens": 39,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
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
                        Text(
                            text="I'll retrieve the secrets for both passwords you provided."
                        ),
                        ToolCall(
                            id="toolu_01TWimojn2PTE3xXFV1hXCLA",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01EnJcbb8jA3991aZxoXpGzz",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": "I'll retrieve the secrets for both passwords you provided.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01TWimojn2PTE3xXFV1hXCLA",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01EnJcbb8jA3991aZxoXpGzz",
                                "input": {"password": "radiance"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01TWimojn2PTE3xXFV1hXCLA",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01EnJcbb8jA3991aZxoXpGzz",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets retrieved for each password:

- **Password "mellon"**: Welcome to Moria!
- **Password "radiance"**: Life before Death\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": """\
Here are the secrets retrieved for each password:

- **Password "mellon"**: Welcome to Moria!
- **Password "radiance"**: Life before Death\
""",
                                "type": "text",
                            }
                        ],
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
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 606,
                "output_tokens": 39,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
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
                        Text(
                            text="I'll retrieve the secrets for both passwords using the secret retrieval tool."
                        ),
                        ToolCall(
                            id="toolu_01DwJWvVkNiJh4UxfwJ8y5Fb",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01Ar4f3WUAeEP1XkLLniqgGs",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": "I'll retrieve the secrets for both passwords using the secret retrieval tool.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01DwJWvVkNiJh4UxfwJ8y5Fb",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01Ar4f3WUAeEP1XkLLniqgGs",
                                "input": {"password": "radiance"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01DwJWvVkNiJh4UxfwJ8y5Fb",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01Ar4f3WUAeEP1XkLLniqgGs",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets retrieved for each password:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "text": """\
Here are the secrets retrieved for each password:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
""",
                                "type": "text",
                            }
                        ],
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
            "provider": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
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
                        Text(
                            text="I'll retrieve the secrets for both passwords using the secret retrieval tool."
                        ),
                        ToolCall(
                            id="toolu_01WDdCywnm8qipwhxfx6pqeK",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_018E4FGuyx2MeDT3P5MpwxgW",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "I'll retrieve the secrets for both passwords using the secret retrieval tool.",
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01WDdCywnm8qipwhxfx6pqeK",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_018E4FGuyx2MeDT3P5MpwxgW",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01WDdCywnm8qipwhxfx6pqeK",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_018E4FGuyx2MeDT3P5MpwxgW",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets retrieved for each password:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Here are the secrets retrieved for each password:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
""",
                            }
                        ],
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
                "input_tokens": 606,
                "output_tokens": 39,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
            "n_chunks": 13,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
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
                        Text(
                            text="I'll retrieve the secrets for both passwords using the secret retrieval tool."
                        ),
                        ToolCall(
                            id="toolu_01H12BvQ98hDyFJZ1v1hwvzN",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01HynpzuYJw7npk4AKcaxyEa",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "I'll retrieve the secrets for both passwords using the secret retrieval tool.",
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01H12BvQ98hDyFJZ1v1hwvzN",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01HynpzuYJw7npk4AKcaxyEa",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01H12BvQ98hDyFJZ1v1hwvzN",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01HynpzuYJw7npk4AKcaxyEa",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
I've successfully retrieved the secrets for both passwords:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic-beta/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
I've successfully retrieved the secrets for both passwords:

- Password "mellon": **Welcome to Moria!**
- Password "radiance": **Life before Death**\
""",
                            }
                        ],
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
                "input_tokens": 606,
                "output_tokens": 40,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
            },
            "n_chunks": 12,
        }
    }
)
