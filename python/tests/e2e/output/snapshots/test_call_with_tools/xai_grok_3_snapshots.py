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
            "provider": "xai",
            "model_id": "grok-3",
            "params": {},
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=(
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                        ToolCall(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
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
            "provider": "xai",
            "model_id": "grok-3",
            "params": {},
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=(
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                        ToolCall(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
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
            "provider": "xai",
            "model_id": "grok-3",
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=(
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                        ToolCall(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
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
            "n_chunks": "variable",
        }
    }
)
async_stream_snapshot = snapshot(
    {
        "response": {
            "provider": "xai",
            "model_id": "grok-3",
            "finish_reason": None,
            "messages": [
                SystemMessage(content=Text(text="Use parallel tool calling.")),
                UserMessage(
                    content=(
                        Text(
                            text="Please retrieve the secrets associated with each of these passwords: mellon,radiance"
                        ),
                    )
                ),
                AssistantMessage(
                    content=(
                        ToolCall(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                        ToolCall(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            args="[xai tool call args]",
                        ),
                    ),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [
                            {
                                "type": "tool_call",
                                "id": "tool_call_001",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                            {
                                "type": "tool_call",
                                "id": "tool_call_002",
                                "name": "secret_retrieval_tool",
                                "args": "[xai tool call args]",
                            },
                        ],
                        "tool_calls": [
                            {
                                "id": "tool_call_001",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                            {
                                "id": "tool_call_002",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": "[xai tool call args]",
                                },
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=(
                        ToolOutput(
                            id="tool_call_001",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="tool_call_002",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    )
                ),
                AssistantMessage(
                    content=(Text(text="[xai assistant text]"),),
                    provider="xai",
                    model_id="grok-3",
                    raw_message={
                        "content": [{"type": "text", "text": "[xai assistant text]"}]
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
            "n_chunks": "variable",
        }
    }
)
