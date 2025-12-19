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
                "input_tokens": 604,
                "output_tokens": 39,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=604, output_tokens=39, server_tool_use=None, service_tier='standard')",
                "total_tokens": 643,
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
                            text="I'll retrieve the secrets for both passwords using parallel tool calls."
                        ),
                        ToolCall(
                            id="toolu_01Tfk647A6Mcr72yhjDRsrz9",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01AJ62fKzqVGyXGwDsp7D3io",
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
                                "text": "I'll retrieve the secrets for both passwords using parallel tool calls.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01Tfk647A6Mcr72yhjDRsrz9",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01AJ62fKzqVGyXGwDsp7D3io",
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
                            id="toolu_01Tfk647A6Mcr72yhjDRsrz9",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01AJ62fKzqVGyXGwDsp7D3io",
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
async_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
            "params": {},
            "finish_reason": None,
            "usage": {
                "input_tokens": 604,
                "output_tokens": 39,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=604, output_tokens=39, server_tool_use=None, service_tier='standard')",
                "total_tokens": 643,
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
                            text="I'll retrieve the secrets for both passwords using parallel tool calls."
                        ),
                        ToolCall(
                            id="toolu_01Vf6JrFVzUgouGLV3HiDufn",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01KVVdehpzKB6FiGhjUHuUvy",
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
                                "text": "I'll retrieve the secrets for both passwords using parallel tool calls.",
                                "type": "text",
                            },
                            {
                                "id": "toolu_01Vf6JrFVzUgouGLV3HiDufn",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01KVVdehpzKB6FiGhjUHuUvy",
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
                            id="toolu_01Vf6JrFVzUgouGLV3HiDufn",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01KVVdehpzKB6FiGhjUHuUvy",
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
            "provider_id": "anthropic",
            "provider_model_name": "claude-sonnet-4-0",
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
                            id="toolu_01VnfuHi3e5xLCSmu3dYU3ZD",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01TLAG1X6XcdwbRGBJLL7NRF",
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
                                "id": "toolu_01VnfuHi3e5xLCSmu3dYU3ZD",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01TLAG1X6XcdwbRGBJLL7NRF",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01VnfuHi3e5xLCSmu3dYU3ZD",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01TLAG1X6XcdwbRGBJLL7NRF",
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
                "raw": "None",
                "total_tokens": 645,
            },
            "n_chunks": 12,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "provider_model_name": "claude-sonnet-4-0",
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
                            text="I'll retrieve the secrets for both passwords you provided."
                        ),
                        ToolCall(
                            id="toolu_0199cTXNM9CoZP2ivCetrRm3",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_011WQyAr9qBAfeS7Ce3mHF8A",
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
                                "text": "I'll retrieve the secrets for both passwords you provided.",
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_0199cTXNM9CoZP2ivCetrRm3",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_011WQyAr9qBAfeS7Ce3mHF8A",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_0199cTXNM9CoZP2ivCetrRm3",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_011WQyAr9qBAfeS7Ce3mHF8A",
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
                "input_tokens": 602,
                "output_tokens": 39,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "raw": "None",
                "total_tokens": 641,
            },
            "n_chunks": 14,
        }
    }
)
