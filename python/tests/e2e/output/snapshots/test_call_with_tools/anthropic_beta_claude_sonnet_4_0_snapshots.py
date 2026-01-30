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
                "provider_tool_usage": None,
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
                            id="toolu_01NR7bVJtkNaURYgoXvcLgFA",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01D5Dh84tPSbPKPPGzXTSaRz",
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
                                "id": "toolu_01NR7bVJtkNaURYgoXvcLgFA",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_01D5Dh84tPSbPKPPGzXTSaRz",
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
                            id="toolu_01NR7bVJtkNaURYgoXvcLgFA",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01D5Dh84tPSbPKPPGzXTSaRz",
                            name="secret_retrieval_tool",
                            result="Life before Death",
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
                    "strict": None,
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
                "provider_tool_usage": None,
                "raw": "BetaUsage(cache_creation=BetaCacheCreation(ephemeral_1h_input_tokens=0, ephemeral_5m_input_tokens=0), cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=606, output_tokens=39, server_tool_use=None, service_tier='standard')",
                "total_tokens": 645,
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
                            id="toolu_015gjqBN4T7teHemz4SRhY4k",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_017vrY2xF9nTMnrb5k7ZKWpD",
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
                                "id": "toolu_015gjqBN4T7teHemz4SRhY4k",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_017vrY2xF9nTMnrb5k7ZKWpD",
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
                            id="toolu_015gjqBN4T7teHemz4SRhY4k",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_017vrY2xF9nTMnrb5k7ZKWpD",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets associated with each password:

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
Here are the secrets associated with each password:

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
                    "strict": None,
                }
            ],
        }
    }
)
stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
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
                            id="toolu_01VWFW9FF8QaS9aWvBEPAw9z",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_012pyoQwpU3MUduNm1AEuMYz",
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
                                "id": "toolu_01VWFW9FF8QaS9aWvBEPAw9z",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_012pyoQwpU3MUduNm1AEuMYz",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_01VWFW9FF8QaS9aWvBEPAw9z",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_012pyoQwpU3MUduNm1AEuMYz",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets retrieved for each password:

- Password "mellon": "Welcome to Moria!"
- Password "radiance": "Life before Death"\
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

- Password "mellon": "Welcome to Moria!"
- Password "radiance": "Life before Death"\
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 606,
                "output_tokens": 38,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 644,
            },
            "n_chunks": 10,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider_id": "anthropic",
            "model_id": "anthropic-beta/claude-sonnet-4-0",
            "provider_model_name": "claude-sonnet-4-0",
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
                            text="I'll retrieve the secrets for both passwords using parallel tool calls."
                        ),
                        ToolCall(
                            id="toolu_011bPS5j9gFZsM7URe1242DY",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_01Q2suTpa6uBzfa9JB9FjSa3",
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
                                "text": "I'll retrieve the secrets for both passwords using parallel tool calls.",
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_011bPS5j9gFZsM7URe1242DY",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_01Q2suTpa6uBzfa9JB9FjSa3",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_011bPS5j9gFZsM7URe1242DY",
                            name="secret_retrieval_tool",
                            result="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_01Q2suTpa6uBzfa9JB9FjSa3",
                            name="secret_retrieval_tool",
                            result="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets associated with each password:

- Password "mellon": "Welcome to Moria!"
- Password "radiance": "Life before Death"\
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
Here are the secrets associated with each password:

- Password "mellon": "Welcome to Moria!"
- Password "radiance": "Life before Death"\
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
                    "strict": None,
                }
            ],
            "usage": {
                "input_tokens": 604,
                "output_tokens": 38,
                "cache_read_tokens": 0,
                "cache_write_tokens": 0,
                "reasoning_tokens": 0,
                "provider_tool_usage": None,
                "raw": "None",
                "total_tokens": 642,
            },
            "n_chunks": 10,
        }
    }
)
