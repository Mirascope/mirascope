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
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
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
                            id="toolu_vrtx_01LANqFTiViajcf2LdRcGxYY",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_vrtx_01PNnnGpWtXUx1tsL5LoXxsm",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_vrtx_01LANqFTiViajcf2LdRcGxYY",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_vrtx_01PNnnGpWtXUx1tsL5LoXxsm",
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
                            id="toolu_vrtx_01LANqFTiViajcf2LdRcGxYY",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_vrtx_01PNnnGpWtXUx1tsL5LoXxsm",
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
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
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
    }
)
async_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
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
                            id="toolu_vrtx_01JVxAP8kxtFbgFSUYTx9CzE",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_vrtx_01DdQ5fPeyimrNYf6C4pQFAS",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "id": "toolu_vrtx_01JVxAP8kxtFbgFSUYTx9CzE",
                                "input": {"password": "mellon"},
                                "name": "secret_retrieval_tool",
                                "type": "tool_use",
                            },
                            {
                                "id": "toolu_vrtx_01DdQ5fPeyimrNYf6C4pQFAS",
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
                            id="toolu_vrtx_01JVxAP8kxtFbgFSUYTx9CzE",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_vrtx_01DdQ5fPeyimrNYf6C4pQFAS",
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
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
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
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
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
                            id="toolu_vrtx_016s1MRCMWAj5jrWE33xHh9m",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_vrtx_01E5iVtKZ7MHAmWVVGZ8Zf3R",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_vrtx_016s1MRCMWAj5jrWE33xHh9m",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_vrtx_01E5iVtKZ7MHAmWVVGZ8Zf3R",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_vrtx_016s1MRCMWAj5jrWE33xHh9m",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_vrtx_01E5iVtKZ7MHAmWVVGZ8Zf3R",
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
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "text",
                                "text": """\
I've successfully retrieved the secrets associated with both passwords:

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
            "n_chunks": 12,
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "anthropic-vertex",
            "model_id": "claude-haiku-4-5@20251001",
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
                            id="toolu_vrtx_01QsJYPnqxiXt33Dzh2eaTdp",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="toolu_vrtx_01L9DGQeUCYbghy8bSFpK9MZ",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
                    raw_message={
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": "toolu_vrtx_01QsJYPnqxiXt33Dzh2eaTdp",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "mellon"},
                            },
                            {
                                "type": "tool_use",
                                "id": "toolu_vrtx_01L9DGQeUCYbghy8bSFpK9MZ",
                                "name": "secret_retrieval_tool",
                                "input": {"password": "radiance"},
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="toolu_vrtx_01QsJYPnqxiXt33Dzh2eaTdp",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="toolu_vrtx_01L9DGQeUCYbghy8bSFpK9MZ",
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
                    provider="anthropic-vertex",
                    model_id="claude-haiku-4-5@20251001",
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
            "n_chunks": 13,
        }
    }
)
