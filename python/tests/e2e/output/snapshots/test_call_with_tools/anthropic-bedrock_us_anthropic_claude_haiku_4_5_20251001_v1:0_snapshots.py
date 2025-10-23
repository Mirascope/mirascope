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
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_01AFiLMvgGxkoLp3gNR1Td9P",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_bdrk_01DQdxYEVE4Qa8BhL2MRb1EN",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01AFiLMvgGxkoLp3gNR1Td9P",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_bdrk_01DQdxYEVE4Qa8BhL2MRb1EN",
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
                            id="toolu_bdrk_01AFiLMvgGxkoLp3gNR1Td9P",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_bdrk_01DQdxYEVE4Qa8BhL2MRb1EN",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
I've successfully retrieved the secrets associated with both passwords:

1. **Password: mellon** → Secret: "Welcome to Moria!"
2. **Password: radiance** → Secret: "Life before Death"\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
I've successfully retrieved the secrets associated with both passwords:

1. **Password: mellon** → Secret: "Welcome to Moria!"
2. **Password: radiance** → Secret: "Life before Death"\
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
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_01ERW2ruQ1M8FUc5X3iTdYyU",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_bdrk_01GzXqYQM1QzY8VxHxgNW7JF",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_bdrk_01ERW2ruQ1M8FUc5X3iTdYyU",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_bdrk_01GzXqYQM1QzY8VxHxgNW7JF",
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
                            id="toolu_bdrk_01ERW2ruQ1M8FUc5X3iTdYyU",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_bdrk_01GzXqYQM1QzY8VxHxgNW7JF",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
Here are the secrets retrieved:

1. **Password: mellon** → Secret: "Welcome to Moria!"
2. **Password: radiance** → Secret: "Life before Death"\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "citations": None,
                                "text": """\
Here are the secrets retrieved:

1. **Password: mellon** → Secret: "Welcome to Moria!"
2. **Password: radiance** → Secret: "Life before Death"\
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
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_01BKZHdpbnH5KYihhoSkWLqC",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_bdrk_01BsS8DZ1LjLsvAViGyi6gLy",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01BKZHdpbnH5KYihhoSkWLqC",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01BsS8DZ1LjLsvAViGyi6gLy",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01BKZHdpbnH5KYihhoSkWLqC",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_bdrk_01BsS8DZ1LjLsvAViGyi6gLy",
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

1. **Password: "mellon"** → Secret: "Welcome to Moria!"
2. **Password: "radiance"** → Secret: "Life before Death"\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
Here are the secrets retrieved for each password:

1. **Password: "mellon"** → Secret: "Welcome to Moria!"
2. **Password: "radiance"** → Secret: "Life before Death"\
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
            "n_chunks": 7,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
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
                            id="toolu_bdrk_01VYgEXJWHmvhWFYSkyZB2w3",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_bdrk_01RKeTPNWx2uMoFiJQJodhmr",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01VYgEXJWHmvhWFYSkyZB2w3",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_bdrk_01RKeTPNWx2uMoFiJQJodhmr",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_bdrk_01VYgEXJWHmvhWFYSkyZB2w3",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_bdrk_01RKeTPNWx2uMoFiJQJodhmr",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
I've successfully retrieved the secrets associated with both passwords:

1. **Password: mellon** → Secret: "Welcome to Moria!"
2. **Password: radiance** → Secret: "Life before Death"\
"""
                        )
                    ],
                    provider="anthropic-bedrock",
                    model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
I've successfully retrieved the secrets associated with both passwords:

1. **Password: mellon** → Secret: "Welcome to Moria!"
2. **Password: radiance** → Secret: "Life before Death"\
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
            "n_chunks": 7,
        }
    }
)
