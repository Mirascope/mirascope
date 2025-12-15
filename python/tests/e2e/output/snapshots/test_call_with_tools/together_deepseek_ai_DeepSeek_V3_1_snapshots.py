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
            "provider_id": "together",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
            "provider_model_name": "deepseek-ai/DeepSeek-V3.1",
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
                        Text(
                            text="I'll help you retrieve the secrets using the provided passwords. Let me call the tool for each password:"
                        ),
                        ToolCall(
                            id="call_55eda4ef64954c0cad66c9b2",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_9132280957c1433db7820c60",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": "I'll help you retrieve the secrets using the provided passwords. Let me call the tool for each password:",
                        "tool_calls": [
                            {
                                "id": "call_55eda4ef64954c0cad66c9b2",
                                "type": "function",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": '{"password": "mellon"}',
                                },
                                "index": -1,
                            },
                            {
                                "id": "call_9132280957c1433db7820c60",
                                "type": "function",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": '{"password": "radiance"}',
                                },
                                "index": -1,
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_55eda4ef64954c0cad66c9b2",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_9132280957c1433db7820c60",
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

- Password: "mellon" → Secret: "Welcome to Moria!"
- Password: "radiance" → Secret: "Life before Death"

Both passwords successfully retrieved their associated secrets!\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": """\
Here are the secrets retrieved for each password:

- Password: "mellon" → Secret: "Welcome to Moria!"
- Password: "radiance" → Secret: "Life before Death"

Both passwords successfully retrieved their associated secrets!\
""",
                        "tool_calls": [],
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
            "provider_id": "together",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
            "provider_model_name": "deepseek-ai/DeepSeek-V3.1",
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
                        Text(
                            text='I\'ll retrieve the secrets for the passwords "mellon" and "radiance" using parallel tool calling.'
                        ),
                        ToolCall(
                            id="call_844d8b2ef58541beb71e0795",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_c10958b4a5f54879855155b9",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": 'I\'ll retrieve the secrets for the passwords "mellon" and "radiance" using parallel tool calling.',
                        "tool_calls": [
                            {
                                "id": "call_844d8b2ef58541beb71e0795",
                                "type": "function",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": '{"password": "mellon"}',
                                },
                                "index": -1,
                            },
                            {
                                "id": "call_c10958b4a5f54879855155b9",
                                "type": "function",
                                "function": {
                                    "name": "secret_retrieval_tool",
                                    "arguments": '{"password": "radiance"}',
                                },
                                "index": -1,
                            },
                        ],
                    },
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_844d8b2ef58541beb71e0795",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_c10958b4a5f54879855155b9",
                            name="secret_retrieval_tool",
                            value="Life before Death",
                        ),
                    ]
                ),
                AssistantMessage(
                    content=[
                        Text(
                            text="""\
I've retrieved the secrets for both passwords:

- For password "mellon": The secret is "Welcome to Moria!"
- For password "radiance": The secret is "Life before Death"\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message={
                        "role": "assistant",
                        "content": """\
I've retrieved the secrets for both passwords:

- For password "mellon": The secret is "Welcome to Moria!"
- For password "radiance": The secret is "Life before Death"\
""",
                        "tool_calls": [],
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
            "provider": "together",
            "model_id": "together/deepseek-ai/DeepSeek-V3.1",
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
                            text="I'll help you retrieve secrets using the provided passwords. Let me call the secret retrieval tool for each password."
                        ),
                        ToolCall(
                            id="call_8fb40ff4820f4e58b7058e95",
                            name="secret_retrieval_tool",
                            args='{"password": "mellon"}',
                        ),
                        ToolCall(
                            id="call_e9e2649998244b0f91551cf5",
                            name="secret_retrieval_tool",
                            args='{"password": "radiance"}',
                        ),
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message=None,
                ),
                UserMessage(
                    content=[
                        ToolOutput(
                            id="call_8fb40ff4820f4e58b7058e95",
                            name="secret_retrieval_tool",
                            value="Welcome to Moria!",
                        ),
                        ToolOutput(
                            id="call_e9e2649998244b0f91551cf5",
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

- Password "mellon": "Welcome to Moria!"
- Password "radiance": "Life before Death"\
"""
                        )
                    ],
                    provider_id="together",
                    model_id="together/deepseek-ai/DeepSeek-V3.1",
                    provider_model_name="deepseek-ai/DeepSeek-V3.1",
                    raw_message=None,
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
            "n_chunks": 15,
        }
    }
)
async_stream_snapshot = snapshot({})
