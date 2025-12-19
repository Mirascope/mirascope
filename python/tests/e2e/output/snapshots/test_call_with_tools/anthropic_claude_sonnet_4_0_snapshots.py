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
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 602,
                "output_tokens": 39,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=602, output_tokens=39, server_tool_use=None, service_tier='standard')",
                "total_tokens": 641,
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
                            id="toolu_01BUvqBj8Yb34pNAbCJJY1oc",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01VPuQJ1LonDBYXrr8pqPkqQ",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I'll retrieve the secrets for both passwords you provided.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01BUvqBj8Yb34pNAbCJJY1oc",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01VPuQJ1LonDBYXrr8pqPkqQ",
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
                            id="toolu_01BUvqBj8Yb34pNAbCJJY1oc",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01VPuQJ1LonDBYXrr8pqPkqQ",
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
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
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
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 606,
                "output_tokens": 35,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "Usage(cache_creation=CacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=606, output_tokens=35, server_tool_use=None, service_tier='standard')",
                "total_tokens": 641,
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
                            id="toolu_01D9i29ihVc1jnMZcsnjihvd",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01MHY6tDEpQVfKiymoNQuc3j",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": "I'll retrieve the secrets for both passwords using the secret retrieval tool.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01D9i29ihVc1jnMZcsnjihvd",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01MHY6tDEpQVfKiymoNQuc3j",
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
                            id="toolu_01D9i29ihVc1jnMZcsnjihvd",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01MHY6tDEpQVfKiymoNQuc3j",
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

- Password "mellon": Welcome to Moria!
- Password "radiance": Life before Death\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Here are the secrets retrieved for each password:

- Password "mellon": Welcome to Moria!
- Password "radiance": Life before Death\
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
            "provider_id": "anthropic",
            "provider_model_name": "claude-sonnet-4-0",
            "model_id": "anthropic/claude-sonnet-4-0",
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
                            text="I'll retrieve the secrets for both passwords you provided."
                        ),
                        ToolCall(
                            id="toolu_015cUijgET79LXjgeYQerN2h",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01XZTimPexA7h3EVKesnKt5T",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": "I'll retrieve the secrets for both passwords you provided.",
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_015cUijgET79LXjgeYQerN2h",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01XZTimPexA7h3EVKesnKt5T",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_015cUijgET79LXjgeYQerN2h",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01XZTimPexA7h3EVKesnKt5T",
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

1. **Password "mellon"**: "Welcome to Moria!"
2. **Password "radiance"**: "Life before Death"

Both secrets have been successfully retrieved!\
"""
                        )
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
                    provider_model_name="claude-sonnet-4-0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Here are the secrets retrieved for each password:

1. **Password "mellon"**: "Welcome to Moria!"
2. **Password "radiance"**: "Life before Death"

Both secrets have been successfully retrieved!\
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
                "input_tokens": 602,
                "output_tokens": 52,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 654,
            },
            "n_chunks": 17,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "provider_model_name": "claude-sonnet-4-0",
            "model_id": "anthropic/claude-sonnet-4-0",
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
                            id="toolu_017N2md1Efjsccg9yCoHRqaC",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01S7QvvN8RQAx1m31iAG4HYA",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="anthropic",
                    model_id="anthropic/claude-sonnet-4-0",
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
                                "id": "toolu_017N2md1Efjsccg9yCoHRqaC",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01S7QvvN8RQAx1m31iAG4HYA",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_017N2md1Efjsccg9yCoHRqaC",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01S7QvvN8RQAx1m31iAG4HYA",
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
                    model_id="anthropic/claude-sonnet-4-0",
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
                "raw": "None",
                "total_tokens": 645,
            },
            "n_chunks": 10,
        }
    }
)
