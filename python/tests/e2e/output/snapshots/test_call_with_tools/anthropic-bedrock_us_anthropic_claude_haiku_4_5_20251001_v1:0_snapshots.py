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
                        id="toolu_bdrk_01UMFJ8LRGwqns2QkckjdoC8",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_bdrk_01Wmzu3yWgP6xVcim7vEcirx",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "id": "toolu_bdrk_01UMFJ8LRGwqns2QkckjdoC8",
                            "input": {"password": "mellon"},
                            "name": "secret_retrieval_tool",
                            "type": "tool_use",
                        },
                        {
                            "id": "toolu_bdrk_01Wmzu3yWgP6xVcim7vEcirx",
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
                        id="toolu_bdrk_01UMFJ8LRGwqns2QkckjdoC8",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_bdrk_01Wmzu3yWgP6xVcim7vEcirx",
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

1. **Password: "mellon"** → Secret: "Welcome to Moria!"
2. **Password: "radiance"** → Secret: "Life before Death"\
"""
                    )
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": """\
I've successfully retrieved the secrets associated with both passwords:

1. **Password: "mellon"** → Secret: "Welcome to Moria!"
2. **Password: "radiance"** → Secret: "Life before Death"\
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
)
async_snapshot = snapshot(
    {
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
                        id="toolu_bdrk_01YWQTGAFFzTb47yBsQ4b6rq",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_bdrk_017A97Qdu6W5r95bWwSD6tux",
                        name="secret_retrieval_tool",
                        args='{"password": "radiance"}',
                    ),
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "id": "toolu_bdrk_01YWQTGAFFzTb47yBsQ4b6rq",
                            "input": {"password": "mellon"},
                            "name": "secret_retrieval_tool",
                            "type": "tool_use",
                        },
                        {
                            "id": "toolu_bdrk_017A97Qdu6W5r95bWwSD6tux",
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
                        id="toolu_bdrk_01YWQTGAFFzTb47yBsQ4b6rq",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_bdrk_017A97Qdu6W5r95bWwSD6tux",
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

1. **Password: "mellon"** → Secret: "Welcome to Moria!"
2. **Password: "radiance"** → Secret: "Life before Death"\
"""
                    )
                ],
                provider="anthropic",
                model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
                raw_message={
                    "role": "assistant",
                    "content": [
                        {
                            "citations": None,
                            "text": """\
Here are the secrets associated with each password:

1. **Password: "mellon"** → Secret: "Welcome to Moria!"
2. **Password: "radiance"** → Secret: "Life before Death"\
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
)
stream_snapshot = snapshot(
    {
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
                    Text(
                        text="I'll retrieve the secrets for both passwords in parallel."
                    ),
                    ToolCall(
                        id="toolu_bdrk_01926uUXFXZW1FEsaCVWD8Nw",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_bdrk_01HfZPdFSfrEDRNJ9NmijQex",
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
                            "type": "text",
                            "text": "I'll retrieve the secrets for both passwords in parallel.",
                        },
                        {
                            "type": "tool_use",
                            "id": "toolu_bdrk_01926uUXFXZW1FEsaCVWD8Nw",
                            "name": "secret_retrieval_tool",
                            "input": {"password": "mellon"},
                        },
                        {
                            "type": "tool_use",
                            "id": "toolu_bdrk_01HfZPdFSfrEDRNJ9NmijQex",
                            "name": "secret_retrieval_tool",
                            "input": {"password": "radiance"},
                        },
                    ],
                },
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_bdrk_01926uUXFXZW1FEsaCVWD8Nw",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_bdrk_01HfZPdFSfrEDRNJ9NmijQex",
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
Here are the secrets associated with each password:

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
        "n_chunks": 14,
    }
)
async_stream_snapshot = snapshot(
    {
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
                        id="toolu_bdrk_01C4mhdyMcw8o2QheAhaXuu8",
                        name="secret_retrieval_tool",
                        args='{"password": "mellon"}',
                    ),
                    ToolCall(
                        id="toolu_bdrk_01MxApcdjyuPU3forzjRLQJa",
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
                            "id": "toolu_bdrk_01C4mhdyMcw8o2QheAhaXuu8",
                            "name": "secret_retrieval_tool",
                            "input": {"password": "mellon"},
                        },
                        {
                            "type": "tool_use",
                            "id": "toolu_bdrk_01MxApcdjyuPU3forzjRLQJa",
                            "name": "secret_retrieval_tool",
                            "input": {"password": "radiance"},
                        },
                    ],
                },
            ),
            UserMessage(
                content=[
                    ToolOutput(
                        id="toolu_bdrk_01C4mhdyMcw8o2QheAhaXuu8",
                        name="secret_retrieval_tool",
                        value="Welcome to Moria!",
                    ),
                    ToolOutput(
                        id="toolu_bdrk_01MxApcdjyuPU3forzjRLQJa",
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
I've successfully retrieved the secrets for both passwords:

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
        "n_chunks": 10,
    }
)
